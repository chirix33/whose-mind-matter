"""Hybrid block (D-019) fallback step 1: CPU-only trigger-coverage audit on EXISTING no-note traces.

Input: the repair-block Stage 2 run (D-015), condition "none" (direct full-history policy, no notes), 24 dev-v3 seeds
(20261100-23, already inspected development data) x 12 constructions x stakes x1/x4 x 2 draws = 1,152 episodes.

For every recorded irreversible commitment (give / drop) the deployed checker is applied counterfactually at that
history: the public-model posterior (world enumeration under the disclosed model, robot-visible history only) gives
p_success and the recipient-location distribution; the shared gate compares J_commit with the declared search
alternative. Evaluation-only quantities (Bayes value V*(h), realized outcome) are labelled as such.

The "ideal continuation" column replaces a vetoed recorded commitment by V*(h_t): an OPTIMISTIC diagnostic, not a
deployable effect and not a ceiling for every gate.

    python3 scripts/hybrid_trigger_audit.py [episodes.jsonl]
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import Action, legal_actions  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.relational import gate  # noqa: E402

RUN = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "repair" / \
    "repair-stage2-20261029-132459-743ace" / "episodes.jsonl"
OUT = ROOT / "reports" / "hybrid-block"


def parse(s: str) -> Action:
    m = re.match(r"(\w+)\((\w*)(?:,(\w+))?\)", s)
    return Action(m[1], m[2] or "", m[3] or "")


def is_commit(a: Action) -> bool:
    return a.kind in ("give", "drop")


def commit_class(construction: str, a: Action) -> str:
    if a.kind == "give":
        return "social_belief"
    return "testimony_reliability" if construction in ("4b", "4c") else "physical"


def excluded_offices(hist: VisibleHistory, cfg) -> tuple:
    """Offices the robot has entered after the prologue without seeing the recipient (nobody moves afterwards)."""
    return tuple(sorted({o.room for _, o in hist.steps[1:] if o.room in cfg.offices
                         and cfg.recipient not in o.people_present}))


def checker(o: ExactOracle, cfg, a: Action) -> tuple[float, dict]:
    """Deployed checker: public-model posterior from the visible history only (no hidden values)."""
    loc = {}
    p = 0.0
    for w, x in o.belief:
        r = x.people_rooms[cfg.recipient]
        loc[r] = loc.get(r, 0.0) + w
        if a.kind == "give":
            other, fact = cfg.handoff_routes[a.target]
            m = x.minds[a.target]
            dest = m.beliefs.get(fact, "unknown") if not other else m.nested.get((other, fact), "unknown")
            p += w * (dest == r)
        elif a.kind == "drop":
            p += w * (a.target == r)
    return p, loc


def audit(path: Path) -> dict:
    eps = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    eps = [e for e in eps if e.get("condition") == "none" and "blocked" not in e]
    insts = {}
    for seed in sorted({e["seed"] for e in eps}):
        for inst in G.generate(seed):
            insts[(seed, inst.instance_id)] = inst
    rows = []
    for e in eps:
        inst = insts[(e["seed"], e["instance_id"])]
        sc, cfg = inst.scenario, inst.scenario.config
        w = sc.build(inst.hidden)  # evaluation replay (privileged world; the checker below sees only `h`)
        h = VisibleHistory(sc.brief, [(None, w.reset())])
        o0 = ExactOracle(sc, h)
        v0 = o0.value(o0.belief, h.last)
        rewards, commits = 0.0, []
        for k, s in enumerate(e["actions"]):
            a = parse(s)
            assert a in legal_actions(cfg, h.last), (e["state_id"], s)
            if is_commit(a):
                o = ExactOracle(sc, h)
                p, loc = checker(o, cfg, a)
                v = gate(s, p, loc, h.last.room, cfg.horizon - h.last.t, cfg, excluded_offices(h, cfg), "public_model")
                vstar = o.value(o.belief, h.last)  # EVALUATION ONLY
                best = str(o.best_action(o.belief, h.last))  # EVALUATION ONLY
            obs = w.step(a)
            h.steps.append((a, obs))
            if is_commit(a):
                commits.append({"step": k, "action": s, "class": commit_class(inst.construction, a), "p": round(p, 6),
                                "J": round(v.j_commit, 6), "V_alt": round(v.v_alt, 6), "allow": v.allow,
                                "outcome": obs.outcome, "rewards_before": round(rewards, 6), "vstar": round(vstar, 6),
                                "bayes_action": best})
            rewards += obs.reward
        assert abs(rewards - e["return_"]) < 1e-9, e["state_id"]
        first_veto = next((c for c in commits if not c["allow"]), None)
        ideal = first_veto["rewards_before"] + first_veto["vstar"] if first_veto else rewards
        o_first = str(o0.best_action(o0.belief, VisibleHistory(sc.brief, [(None, sc.build(inst.hidden).reset())]).last))
        rows.append({"state_id": e["state_id"], "seed": e["seed"], "construction": inst.construction,
                     "stakes": inst.variant.stakes, "replicate": e["replicate"], "return": round(rewards, 6),
                     "outcome": e["outcome"], "v0_bayes": round(v0, 6), "bayes_first": o_first, "commits": commits,
                     "ideal_after_veto": round(ideal, 6), "actions": e["actions"]})
    return summarize(rows), rows


def summarize(rows: list) -> dict:
    def agg(rs):
        n = len(rs)
        cs = [c for r in rs for c in r["commits"]]
        wrong = [c for c in cs if c["outcome"] == "error"]
        right = [c for c in cs if c["outcome"] == "success"]
        missed = [r for r in rs if not r["commits"] and re.match(r"(give|drop)", r["bayes_first"])]
        return {
            "episodes": n,
            "mean_return": round(sum(r["return"] for r in rs) / n, 4),
            "mean_bayes_v0": round(sum(r["v0_bayes"] for r in rs) / n, 4),
            "mean_lost_vs_bayes": round(sum(r["v0_bayes"] - r["return"] for r in rs) / n, 4),
            "lost_in_error_episodes": round(sum(r["v0_bayes"] - r["return"] for r in rs if r["outcome"] == "error") / n, 4),
            "lost_in_timeouts": round(sum(r["v0_bayes"] - r["return"] for r in rs if r["outcome"] == "timeout") / n, 4),
            "lost_in_successes": round(sum(r["v0_bayes"] - r["return"] for r in rs if r["outcome"] == "success") / n, 4),
            "error_rate": round(sum(r["outcome"] == "error" for r in rs) / n, 4),
            "timeout_rate": round(sum(r["outcome"] == "timeout" for r in rs) / n, 4),
            "commit_triggers": len(cs),
            "wrong_commits": len(wrong), "right_commits": len(right),
            "veto_of_wrong": sum(not c["allow"] for c in wrong), "veto_of_right": sum(not c["allow"] for c in right),
            "allowed_wrong": sum(c["allow"] for c in wrong),
            "episodes_with_veto": sum(any(not c["allow"] for c in r["commits"]) for r in rs),
            "optimistic_gain_ideal_after_veto": round(sum(r["ideal_after_veto"] - r["return"] for r in rs) / n, 4),
            "missed_commit_opportunity_episodes": len(missed),
            "lost_in_missed_opportunity": round(sum(r["v0_bayes"] - r["return"] for r in missed) / n, 4),
            "by_class": {k: {"triggers": sum(c["class"] == k for c in cs),
                             "wrong": sum(c["class"] == k for c in wrong),
                             "veto_wrong": sum(c["class"] == k and not c["allow"] for c in wrong),
                             "veto_right": sum(c["class"] == k and not c["allow"] for c in right)}
                         for k in ("social_belief", "physical", "testimony_reliability")},
        }
    out = {"all": agg(rows)}
    for c in sorted({r["construction"] for r in rows}):
        for st in (1.0, 4.0):
            rs = [r for r in rows if r["construction"] == c and r["stakes"] == st]
            out[f"{c}-x{st:g}"] = agg(rs)
    return out


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else RUN
    summary, rows = audit(path)
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"source": str(path), "condition": "none", "summary": summary}
    (OUT / "trigger-audit.json").write_bytes(json.dumps(res, indent=1).encode("utf-8"))
    (OUT / "trigger-audit-rows.jsonl").write_bytes("".join(json.dumps(r) + "\n" for r in rows).encode("utf-8"))
    print(json.dumps(summary["all"], indent=1))


if __name__ == "__main__":
    main()
