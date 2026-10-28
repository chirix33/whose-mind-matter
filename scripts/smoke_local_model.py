"""Local model smoke test: endpoint reachability, chat, structured-output validity, latency, concurrency.

Run (WSL, server from scripts/serve_local_model.sh already up):
    python scripts/smoke_local_model.py --config configs/models/local_gpt_oss_20b.json --n 10

Outputs (outside Git): $OFFICEMINDS_RUNS/smoke/<run_id>/{manifest.json,calls.jsonl}
The decision prompt uses only the robot-visible view of a tiny OfficeMinds episode.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.scenarios import depth1_knowledge  # noqa: E402
from officeminds.world import legal_actions  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.clients import make_client  # noqa: E402

PROMPT_VERSION = "smoke-decision-v1"


def decision_messages():
    sc = depth1_knowledge()
    w = sc.build(sc.prior[0][0])
    hist = VisibleHistory(sc.brief, [(None, w.reset())])
    acts = [str(a) for a in legal_actions(sc.config, hist.last)]
    layout = {r: list(n) for r, n in sc.config.adjacency.items()}
    user = (
        "You control an office delivery robot. Respond with JSON only: "
        '{"action": <one of the legal actions, verbatim>, "abstain": <true if you cannot decide>}.\n'
        f"Layout (adjacency): {json.dumps(layout)}\n"
        "Rules: each step costs 0.05; success +1; a wrong chute drop (drop) is an irreversible error costing 0.5.\n"
        f"Visible history: {json.dumps(hist.to_agent_dict())}\n"
        f"Legal actions: {json.dumps(acts)}"
    )
    schema = {
        "type": "object",
        "properties": {"action": {"type": "string", "enum": acts}, "abstain": {"type": "boolean"}},
        "required": ["action", "abstain"],
        "additionalProperties": False,
    }
    return [{"role": "user", "content": user}], acts, schema


def validate(text: str, acts: list[str]) -> tuple[bool, str]:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return False, "not_json"
    if not isinstance(obj, dict) or obj.get("action") not in acts or not isinstance(obj.get("abstain"), bool):
        return False, "schema_violation"
    return True, obj["action"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    client = make_client(cfg)
    manifest = runlog.new_manifest("smoke", cfg | {"n": args.n, "concurrency": args.concurrency, "prompt_version": PROMPT_VERSION})
    out = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "smoke" / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    calls = (out / "calls.jsonl").open("w")
    dec = cfg.get("decoding", {})

    models = client.list_models()
    messages, acts, schema = decision_messages()

    def call(mode: str, i: int):
        params = dict(dec)
        if mode == "schema":
            params["response_format"] = {"type": "json_schema", "json_schema": {"name": "decision", "schema": schema}}
        r = client.chat(messages, **params)
        ok, detail = (False, "request_error") if r.error else validate(r.text, acts)
        rec = {"mode": mode, "i": i, "valid": ok, "detail": detail, **asdict(r)}
        calls.write(json.dumps(rec) + "\n")
        return rec

    # Warm-up (excluded from latency stats, kept in the log).
    warm = call("warmup", 0)
    results = {"warmup": [warm]}
    for mode in ("prompt_only", "schema"):
        results[mode] = [call(mode, i) for i in range(args.n)]

    t0 = time.monotonic()
    with ThreadPoolExecutor(args.concurrency) as pool:
        conc = list(pool.map(lambda i: call("schema_concurrent", i), range(2 * args.concurrency)))
    conc_wall = time.monotonic() - t0
    calls.close()

    def summarize(rs):
        lat = [r["latency_s"] for r in rs]
        comp = [r["completion_tokens"] for r in rs if r["completion_tokens"] is not None]
        reas = [r["reasoning_tokens"] for r in rs]
        return {
            "n": len(rs),
            "valid_rate": sum(r["valid"] for r in rs) / len(rs),
            "failure_details": sorted({r["detail"] for r in rs if not r["valid"]}),
            "actions": {a: sum(r["detail"] == a for r in rs) for a in sorted({r["detail"] for r in rs if r["valid"]})},
            "latency_s_median": statistics.median(lat),
            "latency_s_max": max(lat),
            "completion_tokens_median": statistics.median(comp) if comp else None,
            "prompt_tokens": rs[0]["prompt_tokens"],
            "reasoning_tokens_reported": any(x is not None for x in reas),
            "reasoning_text_present_rate": sum(bool(r["reasoning"]) for r in rs) / len(rs),
            "errors": sorted({r["error"] for r in rs if r["error"]}),
        }

    summary = {
        "served_models": models,
        "warmup_latency_s": warm["latency_s"],
        "prompt_only": summarize(results["prompt_only"]),
        "schema": summarize(results["schema"]),
        "schema_concurrent": summarize(conc) | {
            "requests": len(conc),
            "wall_clock_s": conc_wall,
            "throughput_req_per_s": len(conc) / conc_wall,
            "sum_of_latencies_s": sum(r["latency_s"] for r in conc),
        },
        "gpu_after": runlog.gpu_snapshot(),
        "note": "GPU memory is the server's reservation (gpu-memory-utilization), not a measured activation peak.",
    }
    path = runlog.finish(manifest, out, summary=summary)
    print(json.dumps(summary, indent=2))
    print(f"manifest: {path}")


if __name__ == "__main__":
    main()
