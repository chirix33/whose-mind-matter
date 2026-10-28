"""dev-v3 Round B report (analysis fixed before outcomes: experiment-plan.md Entry 2 + Entry 1a R10).

    python3 scripts/report_dev_v3.py <run_dir> [--tag local|api]   -> reports/dev-v3-block/roundB-results-<tag>.md/.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from vomi.fidelity import robot_known_values, score_output_v3  # noqa: E402
from vomi.pilot import PACKAGES  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from run_dev_v3_notes import CONDITIONS, notes_path, reference_and_privileged, states, t0  # noqa: E402

EPS = 0.05


def classify(ds: list[float]) -> str:
    """R10 stratum classification from per-state paired differences (condition - none, mean over draws)."""
    m = round(sum(ds) / len(ds), 9)  # exact-decimal boundary (fixed after Round B: 0.04999999999999999 is +0.05)
    ds = [round(d, 9) for d in ds]
    if m >= EPS and sum(d > 0 for d in ds) >= 3:
        return "positive"
    if m <= -EPS and sum(d < 0 for d in ds) >= 3:
        return "negative"
    if abs(m) < EPS and all(abs(d) <= 0.10 for d in ds):
        return "null"
    return "inconclusive"


def overall(cls: dict[int, str]) -> str:
    pos = sum(cls[s] == "positive" for s in (2, 3, 4))
    nulneg = sum(cls[s] in ("null", "negative") for s in (2, 3, 4))
    if pos >= 2 and cls[1] != "negative":
        return "headroom present"
    if pos == 0 and nulneg >= 2:
        return "no measurable explicit-note headroom"
    return "inconclusive"


def boot_mean(ds, n=2000, seed=0):
    rng = random.Random(seed)
    xs = sorted(sum(rng.choice(ds) for _ in ds) / len(ds) for _ in range(n))
    return xs[int(0.025 * n)], xs[int(0.975 * n) - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--tag", default="local")
    args = ap.parse_args()
    run = Path(args.run_dir)
    eps = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    manifest = json.loads((run / "manifest.json").read_text())
    frozen = json.loads(notes_path(args.tag).read_text())
    qual = {r["instance_id"]: r for r in json.loads((ROOT / "reports/dev-v3-block/qualification.json").read_text())["instances"]}
    sts = {st["state_id"]: st for st in states()}
    cell = defaultdict(list)
    blocked = [e for e in eps if "blocked" in e]
    for e in eps:
        if "blocked" not in e:
            cell[(e["state_id"], e["condition"])].append(e)
    rows, per_state = [], {}
    for sid, st in sts.items():
        per_state[sid] = {}
        for c in CONDITIONS:
            es = cell[(sid, c)]
            rets = [e["return_"] for e in es]
            per_state[sid][c] = sum(rets) / len(rets) if rets else None
            rows.append({"state_id": sid, "stratum": st["inst"].stratum, "construction": st["inst"].construction,
                         "condition": c, "n": len(es), "returns": [round(r, 3) for r in rets],
                         "outcomes": [e["outcome"] for e in es], "steps": [e["steps"] for e in es],
                         "first_actions": [e["actions"][0] if e["actions"] else None for e in es],
                         "fallbacks": sum(v.get("fallbacks", 0) for e in es for v in e["usage"].values()),
                         "failed_attempts": sum(v.get("attempts_failed", 0) for e in es for v in e["usage"].values()),
                         "bayes_v_t0": qual[sid]["bayes_value_t0"], "bayes_optimal": qual[sid]["optimal_first_actions"]})
    readings, strata_tab = {}, {}
    for c in CONDITIONS[1:]:
        cls = {}
        for s in (1, 2, 3, 4):
            ds = [per_state[sid][c] - per_state[sid]["none"] for sid, st in sts.items() if st["inst"].stratum == s
                  and per_state[sid][c] is not None and per_state[sid]["none"] is not None]
            cls[s] = classify(ds) if len(ds) == 4 else "incomplete"
            strata_tab[(c, s)] = {"d_s": [round(d, 4) for d in ds], "mean": round(sum(ds) / len(ds), 4) if ds else None,
                                  "boot95": [round(x, 4) for x in boot_mean(ds)] if ds else None, "class": cls[s]}
        readings[c] = overall(cls) if "incomplete" not in cls.values() else "incomplete"
    # note fidelity vs the aligned public-model posterior (scoring v3.1) and truth
    fid = []
    for sid, st in sts.items():
        inst = st["inst"]
        w, h = t0(inst)
        for u in st["units"]:
            note = frozen["states"][sid]["notes"]["inferred"].get(str(u))
            _, _, post = reference_and_privileged(inst, u)
            cfg = inst.scenario.config
            domain = list(cfg.fact_domains[cfg.query_facts[0]])
            vals = PACKAGES["pilot-v2.1"].schema(domain, u.variable)["properties"]["hypotheses"]["items"]["properties"]["value"]["enum"]
            from vomi.units import content
            s = score_output_v3(note, content(w, u)[0], post, robot_known_values(h, cfg.recipient), vals, False)
            fid.append({"state_id": sid, "unit": str(u), "status": (note or {}).get("status"),
                        "category": s.get("category"), "content_category": s.get("content_category"),
                        "top": s.get("top"), "truth": content(w, u)[0], "posterior": post,
                        "tv_posterior": s.get("tv_posterior"), "unsupported_mass": s.get("unsupported_mass")})
    usage = defaultdict(lambda: defaultdict(float))
    for e in eps:
        if "blocked" in e:
            continue
        for k, v in e["usage"].items():
            for f in ("calls", "prompt_tokens", "completion_tokens", "latency_s"):
                usage[e["condition"]][f"{k}_{f}"] += v.get(f, 0)
    note_usage = defaultdict(float)
    for sid, v in frozen["states"].items():
        for u, call in v["calls"].items():
            for a in call["attempts"]:
                note_usage["calls"] += 1
                note_usage["prompt_tokens"] += a.get("prompt_tokens") or 0
                note_usage["completion_tokens"] += a.get("completion_tokens") or 0
    identical = {}
    for sid, v in frozen["states"].items():
        r = v["rendered_notes_sha256"]
        identical[sid] = [(a, b) for i, a in enumerate(CONDITIONS) for b in CONDITIONS[i + 1:] if r[a] == r[b]]
    res = {"run_id": manifest["run_id"], "tag": args.tag, "episodes": len(eps) - len(blocked), "blocked": len(blocked),
           "rows": rows, "strata": {f"{c}|{s}": v for (c, s), v in strata_tab.items()}, "readings": readings,
           "fidelity": fid, "usage_by_condition": usage, "note_usage": note_usage, "identical_conditions": identical,
           "wall_clock_s": manifest.get("wall_clock_s")}
    outj = ROOT / "reports" / "dev-v3-block" / f"roundB-results-{args.tag}.json"
    outj.write_text(json.dumps(res, indent=1, sort_keys=True, default=float) + "\n")
    L = [f"# Round B results ({args.tag}) — run `{manifest['run_id']}`", "",
         f"Generated by `scripts/report_dev_v3.py`. {res['episodes']} episodes, {res['blocked']} blocked. Development data; "
         "per-state draws first; the bootstrap is descriptive (4 dependent states per stratum).", "",
         "## Per state and condition (raw returns per draw)", "",
         "| state | Bayes V* (opt) | none | inferred | reference | privileged |", "|---|---|---|---|---|---|"]
    for sid, st in sts.items():
        cells = []
        for c in CONDITIONS:
            r = next(x for x in rows if x["state_id"] == sid and x["condition"] == c)
            cells.append(" ".join(f"{v:+.2f}" for v in r["returns"]) + f" ({'/'.join(sorted(set(r['first_actions']), key=str))})")
        q = qual[sid]
        L.append(f"| {sid.replace('dev-v3-', '')} | {q['bayes_value_t0']:.3f} ({', '.join(q['optimal_first_actions'])}) | " + " | ".join(cells) + " |")
    L += ["", "## Stratum classification (R10; d_s = condition − none per state, mean over draws)", "",
          "| condition | stratum | d_s | mean | boot95 (descr.) | class |", "|---|---|---|---|---|---|"]
    for (c, s), v in strata_tab.items():
        L.append(f"| {c} | {s} | {v['d_s']} | {v['mean']} | {v['boot95']} | {v['class']} |")
    L += ["", "**Readings (pre-declared rule):** " + "; ".join(f"{c}: {r}" for c, r in readings.items())
          + " (privileged is never counted as deployable value).", "",
          "## Inferred-note fidelity (vs the aligned public-model posterior; scoring v3.1)", "",
          "| state | unit | status | category | content cat. | top | truth | posterior |", "|---|---|---|---|---|---|---|---|"]
    for f in fid:
        L.append(f"| {f['state_id'].replace('dev-v3-', '')} | {f['unit']} | {f['status']} | {f['category']} | "
                 f"{f['content_category']} | {f['top']} | {f['truth']} | {f['posterior']} |")
    L += ["", f"Identical rendered conditions: { {k.replace('dev-v3-', ''): v for k, v in identical.items() if v} or 'none'}", "",
          f"Note generation usage: {dict(note_usage)}", "", "Policy usage by condition (sums):"]
    for c, u in usage.items():
        L.append(f"- {c}: " + ", ".join(f"{k} {v:.0f}" for k, v in sorted(u.items())))
    (ROOT / "reports" / "dev-v3-block" / f"roundB-results-{args.tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(readings), outj)


if __name__ == "__main__":
    main()
