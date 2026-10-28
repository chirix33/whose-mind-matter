"""POST-HOC DESCRIPTIVES for dev-v3 Round B (written after seeing the outcomes; not part of the pre-declared reading).

    python3 scripts/describe_dev_v3_roundB.py <run_dir>   -> reports/dev-v3-block/roundB-descriptive-local.json/.md

1. Outcome counts (success / error / timeout) and mean steps per condition x stratum.
2. Rate at which the first action is in the exact Bayes-optimal first-action set (qualification.json).
3. Empirical noise floor: in the 8 states where the reference and privileged MIND NOTES are byte-identical (1c, 3c),
   the two conditions are the same prompt, so their per-state mean difference is pure policy-sampling noise.
4. Robustness of the pre-declared stratum classes to single catastrophic draws: the R10 classification recomputed
   with each state's per-condition mean taken as the MEDIAN of its 3 draws (descriptive sensitivity only).
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from report_dev_v3 import CONDITIONS, classify, overall  # noqa: E402


def main():
    run = Path(sys.argv[1])
    eps = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    qual = {r["instance_id"]: r for r in json.loads((ROOT / "reports/dev-v3-block/qualification.json").read_text())["instances"]}
    stratum = {sid: qual[sid]["stratum"] for sid in qual}
    out = {"label": "POST-HOC DESCRIPTIVE (after outcomes; not the pre-declared reading)"}
    oc = defaultdict(lambda: defaultdict(int))
    steps = defaultdict(list)
    opt = defaultdict(lambda: [0, 0])
    for e in eps:
        k = f"{e['condition']}|{stratum[e['state_id']]}"
        oc[k][e["outcome"]] += 1
        steps[k].append(e["steps"])
        o = opt[e["condition"]]
        o[0] += e["actions"][0] in qual[e["state_id"]]["optimal_first_actions"]
        o[1] += 1
    out["outcomes"] = {k: dict(v) for k, v in sorted(oc.items())}
    out["mean_steps"] = {k: round(statistics.mean(v), 3) for k, v in sorted(steps.items())}
    out["first_action_bayes_optimal_rate"] = {c: f"{a}/{b}" for c, (a, b) in opt.items()}
    cell = defaultdict(list)
    for e in eps:
        cell[(e["state_id"], e["condition"])].append(e["return_"])
    ident = [s for s in qual if (s, "reference") in cell and qual[s]["construction"] in ("1c", "3c")]
    diffs = [statistics.mean(cell[(s, "reference")]) - statistics.mean(cell[(s, "privileged")]) for s in ident]
    out["noise_floor_identical_prompts"] = {"states": len(ident), "ref_minus_priv": [round(d, 4) for d in diffs],
                                            "mean_abs": round(statistics.mean(abs(d) for d in diffs), 4),
                                            "max_abs": round(max(abs(d) for d in diffs), 4)}
    med = {}
    for c in CONDITIONS[1:]:
        cls = {}
        for s in (1, 2, 3, 4):
            sids = sorted({sid for sid, _ in cell if stratum[sid] == s})
            ds = [statistics.median(cell[(sid, c)]) - statistics.median(cell[(sid, "none")]) for sid in sids]
            cls[s] = classify(ds)
        med[c] = {"classes": cls, "reading": overall(cls)}
    out["median_sensitivity"] = med
    (ROOT / "reports/dev-v3-block/roundB-descriptive-local.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    L = ["# Round B (local): post-hoc descriptives", "", f"**{out['label']}.** Run `{run.name}`.", "",
         "## Outcomes per condition | stratum", ""]
    L += [f"- {k}: {v}; mean steps {out['mean_steps'][k]}" for k, v in out["outcomes"].items()]
    L += ["", f"First action in the exact Bayes-optimal set: {out['first_action_bayes_optimal_rate']}", "",
          f"Noise floor (identical prompts, reference vs privileged in 1c/3c): {out['noise_floor_identical_prompts']}", "",
          "Median-of-draws sensitivity of the R10 classes: " + json.dumps(med)]
    (ROOT / "reports/dev-v3-block/roundB-descriptive-local.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
