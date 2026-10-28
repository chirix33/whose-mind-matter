"""Export the dev-v3 block evidence bundle pieces (no model calls).

    python3 scripts/export_dev_v3_evidence.py <round_b_run_dir>

Writes reports/dev-v3-block/evidence/:
  matched-traces.json   agent-visible t0 view + card vs the privileged minds of the same world, with the exact
                        ask-aware first-action Q table, for the 2a holder-swap pair and the 3a/3b depth pair
  episodes-roundB-local.csv   one row per Round B episode (no privileged content beyond the hidden-world id)
  roundB-example-episodes.json   one complete 3c episode per condition (agent view + calls; privileged block kept
                        separate under "privileged")
  hashes.json           sha256 of every evidence and report file of the block
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import _minds_snapshot  # noqa: E402
from qualify_dev_v3 import opt_set, q_table, t0  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.pilot import ledger, task_card  # noqa: E402

EV = ROOT / "reports" / "dev-v3-block" / "evidence"


def matched(spec, n, hidden, pattern):
    ss = G.superset_scenario(spec, n, 1.0)
    truth = (("pattern", pattern),) + hidden
    w, h = t0(ss, truth)
    o = ExactOracle(ss, h)
    qs = q_table(o)
    return {"pattern": pattern, "agent_visible": {"ledger": ledger(h)[0],
                                                   "card": task_card(w.config, ss.brief, rev=6)},
            "privileged": {"hidden": dict(truth), "minds_t0": _minds_snapshot(w)},
            "exact_q_first_actions_public_model": qs, "optimal": opt_set(qs)}


def main():
    run = Path(sys.argv[1])
    EV.mkdir(parents=True, exist_ok=True)
    by = {(i.construction, i.variant.stakes, i.variant.permuted): i for i in G.generate()}
    i2a, i3a = by[("2a", 1.0, False)], by[("3a", 1.0, False)]
    traces = {"note": "Same names, labels and hidden draw within each pair; Q values are exact Bayes (plain posterior, "
                      "asks legal) under the stratum superset public model. 'privileged' is evaluator-only.",
              "2a_holder_swap": [matched(i2a.spec, i2a.role, i2a.hidden, p) for p in ("2a:0", "2a:1")],
              "3a_vs_3b_depth2": [matched(i3a.spec, i3a.role, i3a.hidden, p) for p in ("3a:0", "3b:0")]}
    (EV / "matched-traces.json").write_text(json.dumps(traces, indent=1, sort_keys=True) + "\n")
    eps = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    with (EV / "episodes-roundB-local.csv").open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["state_id", "condition", "replicate", "dispatch_index", "return", "outcome", "steps", "actions",
                     "fallbacks", "failed_attempts", "decision_prompt_tokens", "decision_completion_tokens", "wall_clock_s"])
        for e in sorted(eps, key=lambda e: (e["state_id"], e["condition"], e["replicate"])):
            u = e["usage"].get("decision", {})
            wr.writerow([e["state_id"], e["condition"], e["replicate"], e["dispatch_index"], round(e["return_"], 4),
                         e["outcome"], e["steps"], " ".join(e["actions"]),
                         sum(v.get("fallbacks", 0) for v in e["usage"].values()),
                         sum(v.get("attempts_failed", 0) for v in e["usage"].values()),
                         u.get("prompt_tokens"), u.get("completion_tokens"), round(e["wall_clock_s"], 2)])
    ex = {c: next(e for e in eps if e["state_id"] == "dev-v3-3c-stakes1-perm0" and e["condition"] == c and e["replicate"] == 0)
          for c in ("none", "inferred", "reference", "privileged")}
    (EV / "roundB-example-episodes.json").write_text(json.dumps(ex, indent=1, sort_keys=True, default=str) + "\n")
    files = sorted(p for p in (ROOT / "reports" / "dev-v3-block").rglob("*") if p.is_file() and p.name != "hashes.json"
                   and p.suffix != ".zip")
    hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (EV / "hashes.json").write_text(json.dumps(hashes, indent=1, sort_keys=True) + "\n")
    print("wrote", EV, len(hashes), "hashed files")


if __name__ == "__main__":
    main()
