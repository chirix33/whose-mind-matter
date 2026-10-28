"""Autonomous block Round 2 analysis, exactly as pre-registered (experiment-plan.md, Round 2 entry + amendment).

    python3 scripts/report_round2.py <notes-value run dir>

Writes reports/autonomous-block/round2-results.md. Counts are kept distinct: 9 states (scenarios), 1 frozen note per
state x condition, 3 policy draws. Everything is descriptive; the bootstrap resamples STATES (draws averaged within
a state) and is reported as an interval, never as a significance test.
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONDS = ("none", "inferred", "inferred_bare", "reference", "privileged")
STRATA = {"A (reference informative, consistent)": ["s3"], "B (reference informative via undisclosed base rates)": ["s2", "s6", "s7"],
          "C (reference uninformative 0.5/0.5)": ["s1", "s4", "s5", "s8", "s9"]}
PRICE_IN, PRICE_OUT = 2e-6, 1e-5


def mean(xs):
    xs = list(xs)
    return statistics.mean(xs) if xs else float("nan")


def main():
    run = Path(sys.argv[1])
    man = json.loads((run / "manifest.json").read_text())
    eps = [json.loads(l) for l in (run / "episodes.jsonl").open()]
    notes = json.loads((ROOT / "data/autonomous-block/round2-notes.json").read_text())
    freeze = json.loads((ROOT / "reports/autonomous-block/round2-notes-freeze.json").read_text())
    states = sorted(notes["states"], key=lambda s: int(s[1:]))
    label = {s: notes["states"][s]["symbolic_category"] for s in states}
    blocked = [e for e in eps if "blocked" in e]
    reps = sorted({e["replicate"] for e in eps})
    complete = [r for r in reps if all(any(e["state_id"] == s and e["condition"] == c and e["replicate"] == r and "blocked" not in e
                                           for e in eps) for s in states for c in CONDS)]
    use = [e for e in eps if "blocked" not in e and e["replicate"] in complete]
    for e in use:  # the payload actually injected must be the frozen one
        if e["condition"] != "none":
            assert e["note_sha256"] == freeze["states"][e["state_id"]]["note_sha256"][e["condition"]]
    cell = defaultdict(list)
    for e in use:
        cell[(e["state_id"], e["condition"])].append(e)

    def cost(e):
        d = e["usage"].get("decision", {})
        return d.get("prompt_tokens", 0) * PRICE_IN + d.get("completion_tokens", 0) * PRICE_OUT

    m = {(s, c): mean(e["return_"] for e in cell[(s, c)]) for s in states for c in CONDS}
    delta = {c: {s: m[(s, c)] - m[(s, "none")] for s in states} for c in CONDS if c != "none"}
    L = ["# Round 2 results: replicated value-of-notes diagnostic (development data; exploratory)", "",
         f"Run `{man['run_id']}` (commit `{man.get('git_commit', '?')[:7]}`, dirty paths {len(man.get('dirty_paths', []))}); "
         f"policy {man['config']['model']} effort {man['config']['decoding'].get('reasoning_effort')}, cap "
         f"{man['config']['decoding'].get('max_tokens')}, concurrency {man['config']['concurrency']}, rules r{man['config']['render_revision']}, "
         f"package {man['config']['package']}. Wall clock {man.get('wall_clock_s', 0):.0f} s.",
         f"Frozen notes: `round2-notes-freeze.json` (notes file sha256 `{freeze['notes_file_sha256'][:16]}…`); every injected payload "
         "hash was checked against it.",
         f"Episodes: {len(eps)} dispatched, {len(blocked)} blocked; complete replicate layers used: {complete} "
         f"({len(use)} episodes). Counts: 9 states, 1 note per state x condition, {len(complete)} policy draws.", ""]
    if blocked:
        L += ["Blocked: " + "; ".join(f"{e['state_id']}/{e['condition']}/r{e['replicate']}: {e['blocked'][:80]}" for e in blocked), ""]

    L += ["## Per state: mean return over draws (success/error/timeout counts; within-state SD)", "",
          "| state | unit | label | stratum | " + " | ".join(CONDS) + " |", "|---|---|---|---|" + "---|" * len(CONDS)]
    strat_of = {s: k.split()[0] for k, v in STRATA.items() for s in v}
    for s in states:
        row = []
        for c in CONDS:
            es = cell[(s, c)]
            oc = Counter(e["outcome"] for e in es)
            sd = statistics.pstdev([e["return_"] for e in es]) if len(es) > 1 else 0.0
            row.append(f"{m[(s, c)]:+.3f} ({oc['success']}/{oc['error']}/{oc['timeout']}; sd {sd:.2f})")
        L.append(f"| {s} | {notes['states'][s]['unit']} | {label[s]} | {strat_of[s]} | " + " | ".join(row) + " |")

    L += ["", "## Condition − none, per state averaged over draws", "",
          "| condition | mean Δ (9 states) | better/worse/tie states | useful+carryover states positive (of 4) | drop-one-state range | "
          "reversed by dropping one draw? | bootstrap 90% interval over states | reliable (pre-registered) |",
          "|---|---|---|---|---|---|---|---|"]
    rng = random.Random(20261028)
    useful = [s for s in states if label[s] in ("useful_current_action", "carryover")]
    for c, d in delta.items():
        vals = [d[s] for s in states]
        mu = mean(vals)
        b = sum(v > 1e-9 for v in vals); w = sum(v < -1e-9 for v in vals)
        up = sum(d[s] > 1e-9 for s in useful)
        drop_state = [mean(v for s2, v in d.items() if s2 != s) for s in states]
        flips = []  # drop each single draw of this condition or of `none`, recompute the 9-state mean
        for cc in (c, "none"):
            for s in states:
                for i in range(len(cell[(s, cc)])):
                    rest = [e["return_"] for j, e in enumerate(cell[(s, cc)]) if j != i]
                    mm = dict(m)
                    mm[(s, cc)] = mean(rest)
                    flips.append(mean(mm[(s2, c)] - mm[(s2, "none")] for s2 in states))
        reversed_by_draw = any((f > 1e-9) != (mu > 1e-9) for f in flips) if abs(mu) > 1e-9 else True
        boots = sorted(mean(rng.choice(vals) for _ in vals) for _ in range(5000))
        reliable = (mu >= 0.10 and b > w and up >= 3 and min(drop_state) > 0 and not reversed_by_draw)
        L.append(f"| {c} | {mu:+.3f} | {b}/{w}/{9 - b - w} | {up} | {min(drop_state):+.3f} … {max(drop_state):+.3f} | "
                 f"{'yes' if reversed_by_draw else 'no'} | [{boots[250]:+.3f}, {boots[4750]:+.3f}] | {'yes' if reliable else 'no'} |")

    L += ["", "## By stratum and by original label (mean Δ vs none)", "", "| group | states | " + " | ".join(delta) + " |",
          "|---|---|" + "---|" * len(delta)]
    groups = list(STRATA.items()) + [(f"label {g}", [s for s in states if label[s] == g])
                                     for g in ("useful_current_action", "carryover", "zero_value_stop", "negative")]
    for g, ss in groups:
        L.append(f"| {g} | {', '.join(ss)} | " + " | ".join(f"{mean(delta[c][s] for s in ss):+.3f}" for c in delta) + " |")

    L += ["", "## Contrasts between note conditions (mean over states of per-state difference)", "",
          "| contrast | mean | better/worse/tie | stratum A | stratum B | stratum C |", "|---|---|---|---|---|---|"]
    for a, b_ in (("inferred", "inferred_bare"), ("inferred_bare", "reference"), ("inferred", "reference"),
                  ("privileged", "reference"), ("privileged", "inferred_bare")):
        diff = {s: m[(s, a)] - m[(s, b_)] for s in states}
        v = list(diff.values())
        L.append(f"| {a} − {b_} | {mean(v):+.3f} | {sum(x > 1e-9 for x in v)}/{sum(x < -1e-9 for x in v)}/"
                 f"{sum(abs(x) <= 1e-9 for x in v)} | " + " | ".join(f"{mean(diff[s] for s in ss):+.3f}" for ss in STRATA.values()) + " |")

    L += ["", "## Do notes change what the policy does? First action vs the modal `none` first action", "",
          "| state | modal none first action | " + " | ".join(c for c in CONDS if c != "none") + " |",
          "|---|---|" + "---|" * (len(CONDS) - 1)]
    for s in states:
        modal = Counter(e["actions"][0] for e in cell[(s, "none")] if e["actions"]).most_common(1)[0][0]
        L.append(f"| {s} | {modal} | " + " | ".join(
            f"{sum(e['actions'][0] != modal for e in cell[(s, c)] if e['actions'])}/{len(cell[(s, c)])} differ"
            for c in CONDS if c != "none") + " |")

    L += ["", "## Compute and cost", "",
          f"Note generation (inferred notes, 9 API calls, one-time in this experiment; NOT free in deployment): "
          f"USD {freeze['inferred_notes_usd_ledger_delta']:.4f} (ledger delta).", "",
          "| condition | episodes | mean decision calls | mean prompt tokens / episode | mean completion tokens / episode | "
          "mean reasoning tokens / episode | mean USD / episode (list price) | mean steps | mean wall clock / episode (s) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c in CONDS:
        es = [e for s in states for e in cell[(s, c)]]
        dec = [e["usage"].get("decision", {}) for e in es]
        rt = "n/a" if any(not d.get("reasoning_tokens_known", False) for d in dec) else f"{mean(d['reasoning_tokens'] for d in dec):.0f}"
        L.append(f"| {c} | {len(es)} | {mean(d['calls'] for d in dec):.2f} | {mean(d['prompt_tokens'] for d in dec):.0f} | "
                 f"{mean(d['completion_tokens'] for d in dec):.0f} | {rt} | {mean(cost(e) for e in es):.4f} | "
                 f"{mean(e['steps'] for e in es):.2f} | {mean(e['wall_clock_s'] for e in es):.1f} |")
    fails = sum(d.get("attempts_failed", 0) for e in use for d in e["usage"].values())
    fb = sum(d.get("fallbacks", 0) for e in use for d in e["usage"].values())
    L += ["", f"Failed attempts: {fails}; fallbacks to wait(): {fb}. Episodes ran with concurrency "
          f"{man['config']['concurrency']}; per-episode wall clock includes provider queueing and is not a compute measure.", "",
          "## Note payloads (top value, p; status)", "", "| state | unit | truth | " + " | ".join(CONDS[1:]) + " |",
          "|---|---|---|" + "---|" * (len(CONDS) - 1)]
    for s in states:
        st = notes["states"][s]
        truth = st["notes"]["privileged"]["hypotheses"][0]["value"]
        cells = []
        for c in CONDS[1:]:
            n = st["notes"][c]
            if n is None:
                cells.append("FAILED (no note)")
                continue
            hyps = sorted(n["hypotheses"], key=lambda h: -h["p"])
            cells.append(", ".join(f"{h['value']} {h['p']:.2f}" for h in hyps[:3]) + f" [{n['status']}]")
        L.append(f"| {s} | {st['unit']} | {truth} | " + " | ".join(cells) + " |")
    out = ROOT / "reports/autonomous-block/round2-results.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
