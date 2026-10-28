"""Autonomous block Round 3 analysis, as pre-registered and amended (experiment-plan.md, Round 3 entry + amendment).

    python3 scripts/report_round3.py <round-3 run dir> <round-2 run dir>

Writes reports/autonomous-block/round3-results.md. Round 2 draws are shown side by side and never pooled into the
Round 3 tests; the combined column is labelled descriptive.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRICE_IN, PRICE_OUT = 2e-6, 1e-5
K_RECIPIENT, OTHER, TWIN = ["s2", "s4", "s5"], ["s3", "s6", "s7", "s8"], ["s1"]


def mean(xs):
    xs = list(xs)
    return statistics.mean(xs) if xs else float("nan")


def load(run: Path):
    man = json.loads((run / "manifest.json").read_text())
    eps = [json.loads(l) for l in (run / "episodes.jsonl").open()]
    cell = defaultdict(list)
    for e in eps:
        if "blocked" not in e:
            cell[(e["state_id"], e["condition"])].append(e)
    return man, eps, cell


def main():
    r3, r2 = Path(sys.argv[1]), Path(sys.argv[2])
    man, eps, cell = load(r3)
    _, _, cell2 = load(r2)
    freeze3 = json.loads((ROOT / "reports/autonomous-block/round3-notes-freeze.json").read_text())
    freeze2 = json.loads((ROOT / "reports/autonomous-block/round2-notes-freeze.json").read_text())
    for (s, c), es in cell.items():  # injected payloads must be the frozen ones
        for e in es:
            if c == "reference_doubt":
                assert e["note_sha256"] == freeze3["states"][s]["note_sha256"]
            elif c != "none":
                assert e["note_sha256"] == freeze2["states"][s]["note_sha256"][c]
    states = sorted({s for s, _ in cell}, key=lambda s: int(s[1:]))
    blocked = [e for e in eps if "blocked" in e]
    succ = lambda es: sum(e["outcome"] == "success" for e in es)
    m = {k: mean(e["return_"] for e in v) for k, v in cell.items()}
    L = ["# Round 3 results: replication and matched doubt control (development data; exploratory)", "",
         f"Run `{man['run_id']}` (commit `{man.get('git_commit', '?')[:7]}`, dirty paths {len(man.get('dirty_paths', []))}); policy "
         f"{man['config']['model']} effort {man['config']['decoding'].get('reasoning_effort')}, cap {man['config']['decoding'].get('max_tokens')}, "
         f"rules r{man['config']['render_revision']}, concurrency {man['config']['concurrency']}, stage cap env "
         f"{man['config'].get('stage_cap_usd_env')}. Episodes {len(eps)}, blocked {len(blocked)}. Wall clock {man.get('wall_clock_s', 0):.0f} s.",
         "Every injected payload hash was checked against `round3-notes-freeze.json` / `round2-notes-freeze.json`. At s1 and s9 "
         "reference_doubt is byte-identical to inferred_bare (rendered-note hashes equal), so the s9 doubt arm pools both cells (8 draws).", ""]
    if blocked:
        L += ["Blocked: " + "; ".join(f"{e['state_id']}/{e['condition']}/r{e['replicate']}: {e['blocked'][:80]}" for e in blocked), ""]

    # ---- s9: H3a / H3b
    s9 = {c: cell[("s9", c)] for c in ("none", "reference", "reference_doubt", "inferred_bare")}
    pooled = s9["reference_doubt"] + s9["inferred_bare"]
    n_none, n_ref, n_pool = succ(s9["none"]), succ(s9["reference"]), succ(pooled)
    h3a = n_none <= 1 and n_ref <= 1 and n_pool >= 6 and len(s9["none"]) == 4 and len(s9["reference"]) == 4 and len(pooled) == 8
    h3b = "holds" if (n_pool >= 6 and n_ref <= 1) else ("fails" if n_pool <= 2 else "inconclusive")
    if n_none >= 2 or n_ref >= 2:
        h3b = "inconclusive" if h3b == "holds" else h3b
    L += ["## s9 (H3a replication, H3b doubt): successes / draws", "",
          "| condition | Round 3 | Round 2 (not pooled) | combined (descriptive) | Round 3 actions |", "|---|---|---|---|---|"]
    r2map = {"none": "none", "reference": "reference", "reference_doubt": "inferred_bare", "inferred_bare": "inferred_bare"}
    for c, es in s9.items():
        e2 = cell2.get(("s9", r2map[c]), []) if c != "reference_doubt" else []
        acts = Counter(" ".join(e["actions"]) for e in es).most_common(2)
        L.append(f"| {c} | {succ(es)}/{len(es)} | {succ(e2)}/{len(e2) if e2 else '—'} | "
                 f"{succ(es) + succ(e2)}/{len(es) + len(e2)} | " + "; ".join(f"{a} ×{n}" for a, n in acts) + " |")
    L.append(f"| **pooled doubt arm** (reference_doubt + inferred_bare, identical prompts) | **{n_pool}/{len(pooled)}** | "
             f"3/3 (inferred_bare) | {n_pool + 3}/{len(pooled) + 3} | |")
    L += ["", f"**H3a (replication: none ≤1/4, reference ≤1/4, pooled doubt ≥6/8): {'holds' if h3a else 'does not hold'}.** "
          f"**H3b (pooled ≥6/8 with reference ≤1/4 → holds; pooled ≤2/8 → fails; else inconclusive): {h3b}.**", ""]

    # ---- H3c: cost of doubt in the other states
    L += ["## H3c: reference_doubt − reference (and − none) in the other states (mean return over 4 draws; mean steps)", "",
          "| state | stratum | none | reference | reference_doubt | doubt − reference | doubt − none | steps none / ref / doubt | first action differs from modal reference |",
          "|---|---|---|---|---|---|---|---|---|"]
    strat = {**{s: "K(recipient)" for s in K_RECIPIENT}, **{s: "other" for s in OTHER}, **{s: "s9 twin" for s in TWIN}, "s9": "s9"}
    for s in states:
        st = {c: mean(e["steps"] for e in cell[(s, c)]) for c in ("none", "reference", "reference_doubt")}
        modal = Counter(e["actions"][0] for e in cell[(s, "reference")] if e["actions"]).most_common(1)[0][0]
        diff = sum(e["actions"][0] != modal for e in cell[(s, "reference_doubt")] if e["actions"])
        L.append(f"| {s} | {strat[s]} | {m[(s, 'none')]:+.3f} | {m[(s, 'reference')]:+.3f} | {m[(s, 'reference_doubt')]:+.3f} | "
                 f"{m[(s, 'reference_doubt')] - m[(s, 'reference')]:+.3f} | {m[(s, 'reference_doubt')] - m[(s, 'none')]:+.3f} | "
                 f"{st['none']:.2f} / {st['reference']:.2f} / {st['reference_doubt']:.2f} | {diff}/{len(cell[(s, 'reference_doubt')])} |")
    eight = [s for s in states if s != "s9"]
    d_ref = {s: m[(s, "reference_doubt")] - m[(s, "reference")] for s in eight}
    d_none = {s: m[(s, "reference_doubt")] - m[(s, "none")] for s in eight}
    neg, pos = sum(v < -1e-9 for v in d_ref.values()), sum(v > 1e-9 for v in d_ref.values())
    h3c = mean(d_ref.values()) <= -0.025 and neg > pos
    L += ["", "| group | states | mean doubt − reference | mean doubt − none | negative / positive states (vs reference) |", "|---|---|---|---|---|"]
    for g, ss in (("all 8 (excl. s9)", eight), ("K(recipient): doubt contradicts rule 2", K_RECIPIENT), ("other", OTHER), ("s1 (s9 twin)", TWIN)):
        L.append(f"| {g} | {', '.join(ss)} | {mean(d_ref[s] for s in ss):+.3f} | {mean(d_none[s] for s in ss):+.3f} | "
                 f"{sum(d_ref[s] < -1e-9 for s in ss)} / {sum(d_ref[s] > 1e-9 for s in ss)} |")
    L += ["", f"**H3c (8-state mean ≤ −0.025 and negative > positive states): {'holds' if h3c else 'does not hold'}** "
          f"(mean {mean(d_ref.values()):+.3f}; {neg} negative, {pos} positive).", ""]

    # ---- replication of Round 2's none vs reference
    L += ["## Replication check: none − reference per state (Round 3 vs Round 2)", "",
          "| state | R3 none | R3 reference | R3 none − ref | R2 none − ref | R3 none successes | R3 reference successes |", "|---|---|---|---|---|---|---|"]
    for s in states:
        r2d = mean(e["return_"] for e in cell2[(s, "none")]) - mean(e["return_"] for e in cell2[(s, "reference")])
        L.append(f"| {s} | {m[(s, 'none')]:+.3f} | {m[(s, 'reference')]:+.3f} | {m[(s, 'none')] - m[(s, 'reference')]:+.3f} | {r2d:+.3f} | "
                 f"{succ(cell[(s, 'none')])}/{len(cell[(s, 'none')])} | {succ(cell[(s, 'reference')])}/{len(cell[(s, 'reference')])} |")
    # ---- cost
    L += ["", "## Compute and cost", "", "| condition | episodes | mean steps | mean prompt tokens | mean completion tokens | mean USD / episode |",
          "|---|---|---|---|---|---|"]
    for c in ("none", "reference", "reference_doubt", "inferred_bare"):
        es = [e for s in states for e in cell.get((s, c), [])]
        dec = [e["usage"].get("decision", {}) for e in es]
        L.append(f"| {c} | {len(es)} | {mean(e['steps'] for e in es):.2f} | {mean(d['prompt_tokens'] for d in dec):.0f} | "
                 f"{mean(d['completion_tokens'] for d in dec):.0f} | "
                 f"{mean(d['prompt_tokens'] * PRICE_IN + d['completion_tokens'] * PRICE_OUT for d in dec):.4f} |")
    total = sum(d.get("prompt_tokens", 0) * PRICE_IN + d.get("completion_tokens", 0) * PRICE_OUT
                for e in eps if "blocked" not in e for d in [e["usage"].get("decision", {})])
    fails = sum(d.get("attempts_failed", 0) for e in eps if "blocked" not in e for d in e["usage"].values())
    L += ["", f"Round 3 policy spend from tokens: USD {total:.4f}. Failed attempts: {fails}."]
    out = ROOT / "reports/autonomous-block/round3-results.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
