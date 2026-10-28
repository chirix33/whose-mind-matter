"""Replay the frozen fixed unit contexts under one model and one or more packages; score with scoring v2.

    python3 scripts/run_unit_contexts.py --config configs/models/local_gpt_oss_20b.json --effort low --max-tokens 4096
    python3 scripts/run_unit_contexts.py --config configs/models/api_gpt_6_1_sol.json --effort low
    python3 scripts/run_unit_contexts.py --config ... --packages pilot-v1 pilot-v2 pilot-v2.1 \
        --contexts reports/autonomous-block/unit-contexts-v1-r4.jsonl

Requests are EXACTLY the frozen payloads in reports/pilot/unit-contexts-v1.jsonl (verified by hash), sent
sequentially (concurrency 1). Failure protocol as in the pilot (3 attempts). Incomplete or refused responses are
recorded as failed attempts, never dropped. Writes $OFFICEMINDS_RUNS/unit-contexts/<run_id>/{records.jsonl,manifest.json}.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vomi import runlog  # noqa: E402
from vomi.clients import BudgetExceeded, make_client  # noqa: E402
from vomi.fidelity import score_output  # noqa: E402
from vomi.pilot import PACKAGES, call_with_protocol, prompt_hashes  # noqa: E402

PUBLIC = ROOT / "reports" / "pilot" / "unit-contexts-v1.jsonl"
PRIVATE = ROOT / "data" / "pilot" / "unit-contexts-v1-privileged.jsonl"


def load_contexts():
    text = PUBLIC.read_text()
    man = PUBLIC.with_suffix(".md").read_text()
    if hashlib.sha256(text.encode()).hexdigest() not in man:
        raise SystemExit("fixed contexts do not match their frozen hash; refusing to run")
    pub = [json.loads(l) for l in text.splitlines()]
    priv = {json.loads(l)["context_id"]: json.loads(l) for l in PRIVATE.open()}
    return pub, priv


def values_for(ctx, pkg):
    return ctx["requests"][pkg]["schema"]["properties"]["hypotheses"]["items"]["properties"]["value"]["enum"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--packages", nargs="+", default=list(PACKAGES))
    ap.add_argument("--effort", default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--contexts", default=None, help="re-rendered context file (e.g. reports/autonomous-block/unit-contexts-v1-r4.jsonl)")
    args = ap.parse_args()
    if args.contexts:
        global PUBLIC
        PUBLIC = ROOT / args.contexts
    cfg = json.loads(Path(args.config).read_text())
    decoding = dict(cfg["decoding"])
    if args.effort:
        decoding["reasoning_effort"] = args.effort
    if args.max_tokens:
        decoding["max_tokens"] = args.max_tokens
    pub, priv = load_contexts()
    missing = [p for p in args.packages if p not in pub[0]["requests"]]
    if missing:
        raise SystemExit(f"packages {missing} are not rendered in {PUBLIC.name}")
    meta = {"model": cfg["model"], "provider": cfg["provider"], "decoding": decoding, "packages": args.packages,
            "prompt_sha256": {p: prompt_hashes(p)["unit_system"] for p in args.packages},
            "contexts_file": str(PUBLIC.relative_to(ROOT)), "contexts_sha256": hashlib.sha256(PUBLIC.read_bytes()).hexdigest(),
            "render_revision": pub[0].get("render_revision"), "concurrency": 1}
    manifest = runlog.new_manifest("unit-contexts", meta)
    status = os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n")
    manifest["dirty_paths"] = [l for l in status if l.strip()]
    out = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "unit-contexts" / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    client = make_client(cfg)
    t0, n, blocked = time.monotonic(), 0, None
    with (out / "records.jsonl").open("w") as f:
        for pkg in args.packages:
            package = PACKAGES[pkg]
            for ctx in pub:
                req = ctx["requests"][pkg]
                path = tuple(ctx["unit"][2:-1].split("->"))
                var = "knowledge" if ctx["unit"].startswith("K(") else "reliability"
                ids = set(ctx["visible_ids"])
                try:
                    rec = call_with_protocol(client, "unit", ctx["k"], ctx["unit"], req["messages"], req["schema"],
                                             lambda t: package.validate(t, path, var, req["domain"], ids), decoding)
                except BudgetExceeded as e:
                    blocked = str(e)
                    break
                p = priv[ctx["context_id"]]
                score = score_output(rec.parsed, p["truth"], p["posterior"], set(p["robot_known"]), values_for(ctx, pkg))
                row = {"context_id": ctx["context_id"], "package": pkg, "model": cfg["model"], "effort": decoding.get("reasoning_effort"),
                       "call": asdict(rec), "usage": rec.usage(), "score": score,
                       "incomplete_attempts": sum(1 for a in rec.attempts if (a.get("error") or "").startswith("incomplete")
                                                  or a.get("finish_reason") == "length")}
                f.write(json.dumps(row, default=str) + "\n")
                f.flush()
                n += 1
            if blocked:
                break
    runlog.finish(out_dir=out, manifest=manifest, records=n, wall_clock_s=time.monotonic() - t0, blocked_by_budget=blocked)
    print(f"records {n}; blocked: {blocked}; out: {out}")


if __name__ == "__main__":
    main()
