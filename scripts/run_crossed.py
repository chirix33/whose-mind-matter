"""Crossed diagnostic: which model writes the mental notes vs. which model decides (pilot review 2026-10-28).

Cells (diagnostic only; main experiments must use one backbone for notes and policy):
  policy local + notes local | policy local + notes API | policy API + notes local | policy API + notes API
  direct (no explicit units) for each policy model.
Held fixed within the comparison: frozen dev-v2 instances, legal histories, renderer r3, package pilot-v2
(evidence-bearing schema), graph protocol, and the ALLOCATION: every candidate visible at t0 is instantiated
at t0 and no further allocation happens (fixed diagnostic set). The router is not used.

Prespecified subset (declared before any crossed output): for each of the 8 non-stop families, group g0;
plus group g1 of false_belief, conflict, nested_reliability, directed_perspective; in each group, the FIRST
variant (variants_for order). 12 instances.

    python3 scripts/run_crossed.py --cells local/local local/direct            # local cells
    python3 scripts/run_crossed.py --cells api/local api/api local/api api/direct   # needs OPENAI_API_KEY + cap

A cell whose client cannot be created (e.g. no API key) is recorded as BLOCKED, never silently skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import generate, variants_for  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.clients import BudgetExceeded, make_client  # noqa: E402
from vomi.pilot import RENDER_REVISION, prompt_hashes, run_episode_arm  # noqa: E402
from vomi.units import generate_candidates  # noqa: E402

CONFIGS = {"local": ROOT / "configs/models/local_gpt_oss_20b.json", "api": ROOT / "configs/models/api_gpt_6_1_sol.json"}
FAMILIES = ("ambiguity", "false_belief", "distractors", "conflict", "nested_reliability", "directed_perspective",
            "relevance_shift", "corroborated")
SECOND = ("false_belief", "conflict", "nested_reliability", "directed_perspective")
PACKAGE = "pilot-v2"


def subset(instances):
    out = []
    for fam in FAMILIES:
        for g in (0, 1) if fam in SECOND else (0,):
            first_tag = variants_for(fam)[0].tag(fam)
            out.append(next(i for i in instances if i.instance_id == f"dev-v2-{fam}-g{g}-{first_tag}"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", nargs="+", required=True, help="policy/notes, e.g. local/local api/local local/direct")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()
    insts = subset(generate(version="dev-v2"))
    cfgs = {k: json.loads(p.read_text()) for k, p in CONFIGS.items()}
    meta = {"cells": args.cells, "instances": [i.instance_id for i in insts], "package": PACKAGE, "render_revision": RENDER_REVISION,
            "allocation": "all t0 candidates, no further allocation", "prompt_sha256": prompt_hashes(PACKAGE),
            "models": {k: c["model"] for k, c in cfgs.items()}, "max_tokens": args.max_tokens, "concurrency": args.concurrency}
    manifest = runlog.new_manifest("crossed", meta)
    manifest["dirty_paths"] = [l for l in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if l.strip()]
    out = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "crossed" / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)

    clients, blocked = {}, {}
    for side in {c.split("/")[0] for c in args.cells} | {c.split("/")[1] for c in args.cells if c.split("/")[1] != "direct"}:
        try:
            clients[side] = make_client(cfgs[side])
        except Exception as e:  # missing key etc.
            blocked[side] = f"{type(e).__name__}: {e}"

    def decoding(side):
        d = dict(cfgs[side]["decoding"])
        d["max_tokens"] = max(d.get("max_tokens", 0), args.max_tokens)
        return d

    def job(cell, inst):
        pol, notes = cell.split("/")
        if pol in blocked or (notes != "direct" and notes in blocked):
            return {"cell": cell, "instance_id": inst.instance_id, "blocked": blocked.get(pol) or blocked.get(notes)}
        w = inst.scenario.build(inst.hidden)
        t0_units = generate_candidates(inst.scenario.config, VisibleHistory(inst.scenario.brief, [(None, w.reset())]))
        try:
            if notes == "direct":
                r = run_episode_arm(clients[pol], inst, "direct", decoding(pol), package=PACKAGE)
            else:
                r = run_episode_arm(clients[pol], inst, "fixed", decoding(pol), initial_units=t0_units, allocate=False,
                                    package=PACKAGE, unit_client=clients[notes])
        except BudgetExceeded as e:
            return {"cell": cell, "instance_id": inst.instance_id, "blocked": f"budget: {e}"}
        return {"cell": cell, **asdict(r)}

    t0 = time.monotonic()
    results = []
    with (out / "episodes.jsonl").open("w") as f, ThreadPoolExecutor(args.concurrency) as pool:
        for res in pool.map(lambda ci: job(*ci), [(c, i) for c in args.cells for i in insts]):
            results.append(res)
            f.write(json.dumps(res, default=str) + "\n")
    runlog.finish(manifest, out, wall_clock_s=time.monotonic() - t0, blocked=blocked,
                  episodes=sum("blocked" not in r for r in results))
    for cell in args.cells:
        rs = [r for r in results if r["cell"] == cell and "blocked" not in r]
        if rs:
            print(f"{cell:<14} n={len(rs)} success={sum(r['outcome'] == 'success' for r in rs) / len(rs):.2f} "
                  f"mean_return={sum(r['return_'] for r in rs) / len(rs):+.3f}")
        else:
            print(f"{cell:<14} BLOCKED: {next((r['blocked'] for r in results if r['cell'] == cell), '')}")
    print(f"out: {out}")


if __name__ == "__main__":
    main()
