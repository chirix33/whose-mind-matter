"""D-020 input-contract audit (CPU only; existing pilot data; no model calls).

Question: did the deployed checker (checker_gate) and the Bayes reference receive exactly the public information the LLM
had? Both received the per-instance `Scenario` object (`inst.scenario`): the disclosed hidden-variable prior plus a
builder that closes over generator metadata the LLM never sees as such: the construction ID, the role -> name mapping,
the distractor level and the office order.

Test: build a CARD-COMPILED public model from what the LLM saw.
  - Enumerate every generator pattern (all 12 constructions x 3 distractor levels x every assignment of the roster names
    to roles x the disclosed rate options) whose rendered task card (render r7, which contains the public-model text) is
    BYTE-IDENTICAL to the card the LLM received.
  - The card-compiled model is the uniform mixture of those patterns, each with its own disclosed hidden prior. It uses
    the generator's template library (task-specific engineering supplied in advance; disclosed), but no metadata of
    the realized instance.
  - Recompute, under that model and the same robot-visible histories:
      (1) every checker_gate check in the pilot (p, location, verdict);
      (2) the t0 Bayes value and best first action for all 192 pilot states;
      (3) the realized return of the deterministic Bayes planner on each state's actual hidden draw.
    (3) is an exact CPU evaluation on existing states, not a model run. It is labelled as such.
If (1) and (2) are identical, the instance metadata was informationally redundant given the card and the history. The
uniform pattern weighting is then also irrelevant whenever the history pins a single pattern; that is reported.

    python3 scripts/hybrid_input_audit.py RUN_DIR
"""

from __future__ import annotations

import itertools
import json
import re
import statistics
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.scenarios import Scenario  # noqa: E402
from officeminds.world import Action  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.pilot import task_card  # noqa: E402
from vomi.relational import GateVerdict, gate, j_commit  # noqa: E402
import run_hybrid_fallback as RF  # noqa: E402

OUT = ROOT / "reports" / "hybrid-block" / "audit"
RATE_OPTIONS = {"4a": [(("q_moved", G._f(x)),) for x in ("0.05", "0.06")],
                "4b": [(("r_X", G._f(a)), ("r_Y", G._f(b))) for a, b in (("0.02", "0.3"), ("0.03", "0.4"))],
                "4c": [(("r_incentive", G._f(x)),) for x in ("0.05", "0.06")]}
STRATUM = {c: s for s, cs in G.CONSTRUCTIONS.items() for c in cs}


def card_of(spec, n, stakes) -> tuple[str, object]:
    params = dict(G.prior_of(spec, n)[0][0])
    w = G.build_world(spec, n, stakes, params)
    brief = f"Deliver the package to {n['R'].capitalize()}."
    return task_card(w.config, brief, 7), w.config


def card_class(inst) -> list[tuple]:
    """Every (spec, role->name) pattern whose rendered card equals the instance's card."""
    sc = inst.scenario
    target = task_card(sc.config, sc.brief, 7)
    roster = list(sc.config.roster)
    R = sc.config.recipient
    out = []
    for c in [x for cs in G.CONSTRUCTIONS.values() for x in cs]:
        for level in G.LEVELS:
            roles = G.roles_for(c, level)
            if len(roles) != len(roster):
                continue
            others = [p for p in roster if p != R]
            for perm in itertools.permutations(others):
                n = dict(zip(roles, [R, *perm]))
                for rates in RATE_OPTIONS.get(c, [()]):
                    spec = G.PublicSpec(f"audit-{c}", STRATUM[c], c, level, tuple(n[r] for r in roles),
                                        tuple(inst.spec.offices), rates)
                    try:
                        card, _ = card_of(spec, n, inst.variant.stakes)
                    except Exception:
                        continue
                    if card == target:
                        out.append((spec, n))
    return out


def compiled_scenario(inst, cls) -> Scenario:
    k = len(cls)
    rows = []
    for i, (spec, n) in enumerate(cls):
        for params, w in G.prior_of(spec, n):
            rows.append(((("pattern", str(i)),) + params, w / k))

    def build(p):
        spec, n = cls[int(p["pattern"])]
        return G.build_world(spec, n, inst.variant.stakes, {x: v for x, v in p.items() if x != "pattern"})
    return Scenario(inst.scenario.id + "-card-compiled", inst.scenario.brief, "audit", tuple(rows), build)


def parse(s):
    m = re.match(r"(\w+)\((\w*)(?:,(\w+))?\)", s)
    return Action(m[1], m[2] or "", m[3] or "")


def verdict(p, loc, hist, cfg):
    excl = RF.excluded_offices(hist, cfg)
    loc_n = RF.normalized_loc(loc, cfg, excl)
    if cfg.recipient in hist.last.people_present:
        j = j_commit(p, cfg.stakes)
        return GateVerdict("", p, j, 0.95, j >= 0.95, "")
    return gate("", p, loc_n, hist.last.room, cfg.horizon - hist.last.t, cfg, excl, "")


def planner_rollout(sc_model, world):
    """Deterministic Bayes planner (expectimax under `sc_model`, visible history only) on one real world."""
    h = VisibleHistory(sc_model.brief, [(None, world.reset())])
    total = 0.0
    while not h.last.done:
        o = ExactOracle(sc_model, h)
        a = o.best_action(o.belief, h.last)
        obs = world.step(a)
        h.steps.append((a, obs))
        total += obs.reward
    return total, [str(a) for a in h.actions]


def main():
    run = Path(sys.argv[1])
    eps = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    states = {s["state_id"]: s for s in RF.states()}
    t_start = time.monotonic()
    classes, compiled = {}, {}
    for sid, st in states.items():
        cls = card_class(st["inst"])
        assert any(c[0].construction == st["inst"].construction and c[1] == st["inst"].role for c in cls), sid
        classes[sid] = cls
        compiled[sid] = compiled_scenario(st["inst"], cls)
    # (2) + (3): t0 Bayes value / action and planner rollouts, instance model vs card-compiled model
    t0_rows = []
    for sid, st in states.items():
        inst = st["inst"]
        sc_i, sc_c = inst.scenario, compiled[sid]
        h = VisibleHistory(sc_i.brief, [(None, sc_i.build(inst.hidden).reset())])
        oi, oc = ExactOracle(sc_i, h), ExactOracle(sc_c, h)
        vi, vc = oi.value(oi.belief, h.last), oc.value(oc.belief, h.last)
        ai, ac = str(oi.best_action(oi.belief, h.last)), str(oc.best_action(oc.belief, h.last))
        ri, acts_i = planner_rollout(sc_i, sc_i.build(inst.hidden))
        rc, acts_c = planner_rollout(sc_c, sc_i.build(inst.hidden))
        t0_rows.append({"state_id": sid, "construction": inst.construction, "stakes": inst.variant.stakes,
                        "card_class_size": len(classes[sid]),
                        "card_class_constructions": sorted({c[0].construction for c in classes[sid]}),
                        "patterns_consistent_t0": len({dict(p)["pattern"] for p in oc.params}),
                        "v_instance": round(vi, 10), "v_card_compiled": round(vc, 10),
                        "best_instance": ai, "best_card_compiled": ac,
                        "planner_return_instance_model": round(ri, 10), "planner_return_card_compiled": round(rc, 10),
                        "planner_actions_card_compiled": acts_c})
    # (1) every checker_gate check, replayed on the identical visible history
    check_rows, replay_mismatch = [], 0
    for e in eps:
        if e["condition"] != "checker_gate":
            continue
        st = states[e["state_id"]]
        inst = st["inst"]
        sc_i, sc_c = inst.scenario, compiled[e["state_id"]]
        cfg = sc_i.config
        w = sc_i.build(inst.hidden)  # privileged replay ONLY to regenerate the recorded observations
        h = VisibleHistory(sc_i.brief, [(None, w.reset())])
        for k, log in enumerate(e["steps"]):
            for key, act in (("check", log["proposal"]), ("second_check", log.get("redecision"))):
                chk = log.get(key) if key == "check" else log.get("second_check")
                if not chk or "p" not in chk:
                    continue
                a = parse(act)
                pi, li = RF.tracker_check(sc_i, h, a)
                pc, lc = RF.tracker_check(sc_c, h, a)
                vi, vc = verdict(pi, li, h, cfg), verdict(pc, lc, h, cfg)
                oc = ExactOracle(sc_c, h)
                check_rows.append({"state_id": e["state_id"], "draw": e["draw"], "t": h.last.t, "action": act,
                                   "logged_p": chk["p"], "p_instance": round(pi, 10), "p_card_compiled": round(pc, 10),
                                   "loc_max_abs_diff": round(max(abs(li.get(x, 0) - lc.get(x, 0))
                                                                 for x in set(li) | set(lc)), 12),
                                   "allow_logged": chk["allow"], "allow_instance": vi.allow,
                                   "allow_card_compiled": vc.allow,
                                   "patterns_consistent": len({dict(p)["pattern"] for p in oc.params})})
            obs = w.step(parse(log["executed"]))
            h.steps.append((parse(log["executed"]), obs))
        rec = e["agent_view"]["steps"]
        if [s["obs"] for s in h.to_agent_dict()["steps"]] != [s["obs"] for s in rec]:
            replay_mismatch += 1
    summ = {
        "states": len(t0_rows), "checks": len(check_rows), "episode_replay_mismatches": replay_mismatch,
        "card_class_size": {"min": min(r["card_class_size"] for r in t0_rows),
                            "max": max(r["card_class_size"] for r in t0_rows),
                            "states_with_class_gt1": sum(r["card_class_size"] > 1 for r in t0_rows)},
        "card_class_constructions_by_instance": {c: sorted({x for r in t0_rows if r["construction"] == c
                                                            for x in r["card_class_constructions"]})
                                                 for c in sorted({r["construction"] for r in t0_rows})},
        "t0_value_max_abs_diff": max(abs(r["v_instance"] - r["v_card_compiled"]) for r in t0_rows),
        "t0_best_action_disagreements": sum(r["best_instance"] != r["best_card_compiled"] for r in t0_rows),
        "t0_states_history_pins_one_pattern": sum(r["patterns_consistent_t0"] == 1 for r in t0_rows),
        "check_p_max_abs_diff": max(abs(r["p_instance"] - r["p_card_compiled"]) for r in check_rows),
        "check_loc_max_abs_diff": max(r["loc_max_abs_diff"] for r in check_rows),
        "check_verdict_disagreements": sum(r["allow_instance"] != r["allow_card_compiled"] for r in check_rows),
        "logged_vs_recomputed_verdict_disagreements": sum(r["allow_logged"] != r["allow_instance"] for r in check_rows),
        "logged_vs_recomputed_p_max_abs_diff": max(abs(r["logged_p"] - round(r["p_instance"], 4)) for r in check_rows),
        "checks_history_pins_one_pattern": sum(r["patterns_consistent"] == 1 for r in check_rows),
        "bayes_v_t0_mean_card_compiled": round(statistics.mean(r["v_card_compiled"] for r in t0_rows), 4),
        "planner_realized_return_mean_card_compiled": round(statistics.mean(r["planner_return_card_compiled"]
                                                                            for r in t0_rows), 4),
        "planner_realized_return_mean_instance_model": round(statistics.mean(r["planner_return_instance_model"]
                                                                             for r in t0_rows), 4),
        "planner_realized_return_by_stakes": {f"x{s:g}": round(statistics.mean(r["planner_return_card_compiled"]
                                                                               for r in t0_rows if r["stakes"] == s), 4)
                                              for s in (1.0, 4.0)},
        "planner_outcomes": {k: sum(1 for r in t0_rows if k(r)) for k in []},
        "cpu_s": round(time.monotonic() - t_start, 1),
    }
    summ.pop("planner_outcomes")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "input-audit.json").write_bytes(json.dumps({"summary": summ, "t0": t0_rows}, indent=1).encode("utf-8"))
    (OUT / "input-audit-checks.jsonl").write_bytes("".join(json.dumps(r) + "\n" for r in check_rows).encode("utf-8"))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
