"""Hybrid block (D-019): descriptive reference for the fallback pilot states (CPU, no model).

The public-model Bayes planner is DEPLOYABLE in this regime: it uses only the disclosed public model and the robot-visible
history. Its exact expected return at t0 (expectimax over the posterior) is computed for the 192 pilot states.

    python3 scripts/hybrid_bayes_reference.py
"""
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from officeminds.episode import VisibleHistory  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
import run_hybrid_fallback as RF  # noqa: E402

rows = []
t = time.perf_counter()
for st in RF.states():
    inst = st["inst"]
    h = VisibleHistory(inst.scenario.brief, [(None, inst.scenario.build(inst.hidden).reset())])
    o = ExactOracle(inst.scenario, h)
    rows.append({"state_id": st["state_id"], "construction": inst.construction, "stakes": inst.variant.stakes,
                 "v_bayes_t0": o.value(o.belief, h.last)})
cpu = time.perf_counter() - t
out = {"states": len(rows), "mean_v_bayes_t0": round(statistics.mean(r["v_bayes_t0"] for r in rows), 4),
       "by_stakes": {f"x{s:g}": round(statistics.mean(r["v_bayes_t0"] for r in rows if r["stakes"] == s), 4) for s in (1.0, 4.0)},
       "by_construction": {c: round(statistics.mean(r["v_bayes_t0"] for r in rows if r["construction"] == c), 4)
                           for c in sorted({r["construction"] for r in rows})},
       "cpu_s_total": round(cpu, 2), "note": "expected return of the exact public-model expectimax policy; not a rollout"}
(ROOT / "reports" / "hybrid-block" / "bayes-reference.json").write_bytes(json.dumps(out, indent=1).encode())
print(json.dumps(out, indent=1))
