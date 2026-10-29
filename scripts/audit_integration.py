"""Integration block part A: audit of the existing repair Stage 2 traces (no model calls). D-016 §3A.

    python3 scripts/audit_integration.py   -> reports/integration-block/audit.{json,md}

Action patterns are the main evidence. The reasoning classification uses the keyword rubric below (written before any
coding of traces), reported with examples and every uncertain case; written reasoning is not a causal record. No causal
comparison between episodes that did and did not ask.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import Action  # noqa: E402
from run_repair import NOTES, frozen_for, stage2_states  # noqa: E402
from vomi.graph import PerspectiveGraph  # noqa: E402

RUN = Path("/home/aashraf/officeminds-runs/repair/repair-stage2-20261029-132459-743ace")
OUT = ROOT / "reports" / "integration-block"
FOCUS = ("2a", "2b", "3a", "3b")
# Rubric v1 was applied once BEFORE the plan gate (output kept as audit-v1-pregate.json). Rubric v2 (below) adds code (v)
# "uses the courier's own belief" (plan-gate RC7) and is fixed in experiment-plan.md Entry 1a, with its hash, before re-coding.
RUBRIC = {
    "uses_own_belief": re.compile(r"\b(knows|believes|thinks|said|says|told)\b[^.]{0,50}\b(meeting(_room)?|meeting is|new office|"
                                  r"current office|changed)\b[^.]{0,60}\b(give|forward|hand)", re.I),
    "forwarding_rule": re.compile(r"forward\w*[^.]{0,80}\b(thinks|believes|think|believe)\b[^.]{0,40}\b(believes|thinks|will go|goes)\b", re.I),
    "belief_as_location": re.compile(r"\b(believes|says|said|thinks|told|answer\w*)\b[^.]{0,80}\b(so|therefore|thus|hence|meaning)\b"
                                     r"[^.]{0,60}\b(is|likely|probably|must be|should be)\b", re.I),
}


def G_focal(st):
    from officeminds.devgen3 import focal_units
    return focal_units(st["inst"])


def parse(a: str) -> Action:
    kind, _, rest = a.partition("(")
    args = [x for x in rest.rstrip(")").split(",") if x]
    return Action(kind, *args)


def classify(text: str) -> str:
    if not text.strip():
        return "uncertain"
    hits = [k for k, rx in RUBRIC.items() if rx.search(text)]
    if len(hits) == 1:
        return hits[0]
    return "uncertain" if len(hits) > 1 else "other"


def main():
    eps = [json.loads(l) for l in (RUN / "episodes.jsonl").read_text().splitlines() if l.strip()]
    notes = json.loads(NOTES.read_text())
    sts = {st["state_id"]: st for st in stage2_states(24)}
    first = defaultdict(Counter)
    after_ask = defaultdict(Counter)
    stale_exp = defaultdict(lambda: [0, 0])
    stale_split = defaultdict(lambda: {"after_ask": [0, 0], "sighting_only": [0, 0]})
    ask_sym = defaultdict(lambda: {"asks": 0, "true_content_unchanged": 0, "posterior_unchanged": 0})
    later_wrong = defaultdict(lambda: [0, 0])
    coded = defaultdict(list)
    for e in eps:
        st = sts[e["state_id"]]
        c, cond = st["inst"].construction, e["condition"]
        if cond not in ("none", "inferred", "reference"):
            continue
        stakes = st["inst"].variant.stakes
        key = f"{c}|{cond}|{stakes:g}"
        acts = [parse(a) for a in e["actions"]]
        first[key][acts[0].kind] += 1
        # replay: world + graph status per decision (robot-visible replay of the recorded actions)
        w = st["inst"].scenario.build(st["inst"].hidden)
        h = VisibleHistory(st["inst"].scenario.brief, [(None, w.reset())])
        g = None
        if cond != "none":
            keep, fr = frozen_for(st, cond, notes)
            g = PerspectiveGraph(recipient=st["inst"].scenario.config.recipient, refutation_mode="fact_only")
            for u in keep:
                g.instantiate(u, fr[str(u)], fr[str(u)].get("evidence_ids", []), t=0, cost=0.0)
        dec_calls = [cl for cl in e["calls"] if cl["kind"] == "decision"]
        for t, a in enumerate(acts):
            if t > 0 and g is not None:
                g.advance(h)
                stale = any(r["status"] == "stale" for r in g.policy_view())
                stale_exp[key][0] += stale
                stale_exp[key][1] += 1
                kind = "after_ask" if any(x.kind == "ask" for x in acts[:t]) else "sighting_only"
                stale_split[key][kind][0] += stale
                stale_split[key][kind][1] += 1
            if a.kind == "ask" and c in FOCUS and cond == "reference":
                from vomi.oracle import ExactOracle
                from vomi.units import content
                h2 = VisibleHistory(h.brief, list(h.steps) + [(a, w.clone().step(a))])
                o_a, o_b = ExactOracle(st["inst"].scenario, h), ExactOracle(st["inst"].scenario, h2)
                wb = w.clone()
                wb.step(a)
                for u in G_focal(st):
                    pa, pb = {}, {}
                    for p_, x in o_a.belief:
                        pa[content(x, u)[0]] = pa.get(content(x, u)[0], 0) + p_
                    for p_, x in o_b.belief:
                        pb[content(x, u)[0]] = pb.get(content(x, u)[0], 0) + p_
                    k2 = f"{c}|asked-{next((r for r, n in st['inst'].role.items() if n == a.target), '?')}|{u}"
                    ask_sym[k2]["asks"] += 1
                    ask_sym[k2]["true_content_unchanged"] += content(w, u) == content(wb, u)
                    ask_sym[k2]["posterior_unchanged"] += all(abs(pa.get(v, 0) - pb.get(v, 0)) < 1e-9 for v in set(pa) | set(pb))
            o = w.step(a)
            if t > 0 and a.kind in ("give", "drop"):
                later_wrong[key][1] += 1
                later_wrong[key][0] += o.outcome == "error"
            if t > 0 and acts[t - 1].kind == "ask":
                after_ask[key][a.kind + ("_wrong" if a.kind in ("give", "drop") and o.outcome == "error" else "")] += 1
            if c in ("2b", "3b") and cond == "reference" and a.kind in ("give", "drop") and t < len(dec_calls):
                text = (dec_calls[t]["attempts"][-1].get("reasoning") or "")
                coded[c].append({"state_id": e["state_id"], "replicate": e["replicate"], "step": t, "action": str(a),
                                 "outcome": o.outcome, "class": classify(text), "excerpt": text[:400]})
            h.steps.append((a, o))
            if o.done:
                break
    res = {"label": "Audit of repair Stage 2 traces (no model calls); action patterns are the main evidence",
           "run": RUN.name,
           "first_action": {k: dict(v) for k, v in sorted(first.items())},
           "after_ask_next_action": {k: dict(v) for k, v in sorted(after_ask.items())},
           "stale_exposure_later_decisions": {k: f"{a}/{b}" for k, (a, b) in sorted(stale_exp.items())},
           "later_give_drop_wrong": {k: f"{a}/{b}" for k, (a, b) in sorted(later_wrong.items())},
           "stale_exposure_split": {k: {kk: f"{a}/{b}" for kk, (a, b) in v.items()} for k, v in sorted(stale_split.items())},
           "existing_asks_symbolic": {k: dict(v) for k, v in sorted(ask_sym.items())},
           "rubric_version": "v2",
           "reasoning_rubric": {k: rx.pattern for k, rx in RUBRIC.items()},
           "reasoning_classes": {c: dict(Counter(x["class"] for x in v)) for c, v in coded.items()},
           "reasoning_examples": {c: {cl: [x for x in v if x["class"] == cl][:3] for cl in ("uses_own_belief", "forwarding_rule", "belief_as_location", "other")}
                                  for c, v in coded.items()},
           "reasoning_uncertain": {c: [x for x in v if x["class"] == "uncertain"] for c, v in coded.items()},
           "reasoning_by_outcome": {c: {cl: dict(Counter(x["outcome"] for x in v if x["class"] == cl))
                                        for cl in ("uses_own_belief", "forwarding_rule", "belief_as_location", "other", "uncertain")}
                                    for c, v in coded.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    L = ["# Audit of existing repair Stage 2 traces (no model calls)", "", f"Run `{RUN.name}`. Action patterns first; "
         "reasoning classes are a keyword-rubric heuristic, not a causal record.", "", "## First action (t0) by construction | condition | stakes", ""]
    L += [f"- {k}: {dict(v)}" for k, v in sorted(first.items()) if k.split("|")[0] in FOCUS]
    L += ["", "## Later decisions (t ≥ 1)", "", "Stale-label exposure (decisions with any shown note marked stale / later decisions):"]
    L += [f"- {k}: {v}" for k, v in res["stale_exposure_later_decisions"].items() if k.split("|")[0] in FOCUS and "|none|" not in k]
    L += ["", "Stale exposure split (after an ask / after a sighting or mention only):"]
    L += [f"- {k}: {v}" for k, v in res["stale_exposure_split"].items() if k.split("|")[0] in FOCUS and "|none|" not in k]
    L += ["", "Asks that occurred (reference episodes): true content unchanged / posterior unchanged:"]
    L += [f"- {k}: {v}" for k, v in res["existing_asks_symbolic"].items()]
    L += ["", "Action right after an ask (suffix _wrong = immediate wrong delivery):"]
    L += [f"- {k}: {v}" for k, v in res["after_ask_next_action"].items() if k.split("|")[0] in FOCUS]
    L += ["", "## Reasoning classes (2b/3b reference give/drop decisions)", "", json.dumps(res["reasoning_classes"]),
          "", "By outcome: " + json.dumps(res["reasoning_by_outcome"]), "",
          f"Uncertain cases listed in audit.json: { {c: len(v) for c, v in res['reasoning_uncertain'].items()} }"]
    (OUT / "audit.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(res["reasoning_classes"]), json.dumps({k: v for k, v in res["first_action"].items() if k.startswith("3b")}))


if __name__ == "__main__":
    main()
