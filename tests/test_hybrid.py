"""Hybrid block (D-019): referent engine, relation cache and decision interface (CPU only)."""

from fractions import Fraction

import pytest

from officeminds import hybridfam as F
from officeminds.episode import VisibleHistory
from officeminds.world import Action
from vomi.oracle import ExactOracle
from vomi.relational import (ProvenanceIndex, RelationCache, ReferentEngine, SPECS, j_commit, search_value)

SEED = 20261500


def _hist(sc, params, acts=()):
    w = sc.build(params)
    h = VisibleHistory(sc.brief, [(None, w.reset())])
    for a in acts:
        h.steps.append((a, w.step(a)))
    return h


def _engine(case, h):
    return ReferentEngine(SPECS[case.construction](case.scenario.config), ProvenanceIndex.build(h))


def _enum_p(sc, h, courier):
    cfg = sc.config
    other, fact = cfg.handoff_routes[courier]
    o = ExactOracle(sc, h)
    return sum(w for w, x in o.belief
               if (x.minds[courier].nested.get((other, fact), "unknown") if other
                   else x.minds[courier].beliefs.get(fact, "unknown")) == x.people_rooms[cfg.recipient])


@pytest.mark.parametrize("case", [c for c in F.cases(SEED) if c.stakes == 1.0], ids=lambda c: c.construction)
def test_engine_matches_public_model_enumeration_in_every_world(case):
    sc = case.scenario
    for params, _ in sc.prior:
        h = _hist(sc, params)
        eng = _engine(case, h)
        for c in sc.config.handoff_routes:
            assert float(eng.p_equal(eng.route(c), eng.pm.recipient_loc(eng))) == pytest.approx(_enum_p(sc, h, c), abs=1e-12)


def test_matched_marginals_different_joint_2d():
    case = next(c for c in F.cases(SEED) if c.construction == "2d" and c.stakes == 1.0)
    eng = _engine(case, _hist(case.scenario, case.hidden))
    H, N = case.names["H"], case.names["N"]
    loc = eng.pm.recipient_loc(eng)
    assert eng.dist(eng.route(H)) == eng.dist(eng.route(N)) == eng.dist(loc)  # identical marginals
    assert eng.p_equal(eng.route(N), loc) == 1 and eng.p_equal(eng.route(H), loc) == 0  # opposite joints
    assert eng.p_equal_product(eng.route(N), loc) == Fraction(1, 2)


def test_uncertain_provenance_2e_is_not_deterministic():
    case = next(c for c in F.cases(SEED) if c.construction == "2e")
    eng = _engine(case, _hist(case.scenario, case.hidden))
    H = case.names["H"]
    assert eng.p_equal(eng.route(H), eng.pm.recipient_loc(eng)) == Fraction(3, 4)


def test_answer_updates_robot_estimate_not_person_term():
    case = next(c for c in F.cases(SEED) if c.construction == "2d")
    H = case.names["H"]
    fact = case.scenario.config.query_facts[0]
    e0 = _engine(case, _hist(case.scenario, case.hidden))
    e1 = _engine(case, _hist(case.scenario, case.hidden, [Action("ask", H, fact)]))
    assert e0.route(H) == e1.route(H)
    assert len(e0.dist(e0.route(H))) == 2 and len(e1.dist(e1.route(H))) == 1


def test_cache_reuse_and_refresh_match_fresh_computation():
    for case in [c for c in F.cases(SEED) if c.construction == "seq"]:
        sc, cfg = case.scenario, case.scenario.config
        for ret in ("yes", "no"):
            params = tuple((k, ret if k == "ret" else v) for k, v in case.hidden)
            for acts in ([Action("wait"), Action("wait")], [Action("move", "hall"), Action("move", "lobby")]):
                cache = RelationCache()
                for k in range(3):
                    eng = _engine(case, _hist(sc, params, acts[:k]))
                    for c in cfg.handoff_routes:
                        rec, _ = cache.get(c, eng)
                        assert rec.p == eng.p_equal(eng.route(c), eng.pm.recipient_loc(eng))


def test_gate_formulas():
    assert j_commit(1.0, 4.0) == pytest.approx(0.95)
    assert j_commit(0.5, 1.0) == pytest.approx(0.2)
    offices = ("o1", "o2", "o3")
    # uniform over two offices from the lobby: 0.5*(1-0.15) + 0.5*(1-0.25)
    assert search_value({"o1": 0.5, "o2": 0.5}, "lobby", 8, offices) == pytest.approx(0.80)
    # horizon too short to reach any office and deliver: timeout without penalty after the walked steps
    assert search_value({"o1": 1.0}, "lobby", 2, offices) == pytest.approx(-0.10)


def test_fallback_direct_prompt_is_the_repair_block_direct_prompt():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import run_hybrid_fallback as RF
    from officeminds import devgen3 as G
    from officeminds.world import legal_actions
    from vomi.pilot import load_prompts, policy_messages
    prompts = load_prompts("pilot-v1")
    for inst in G.generate(20261499)[:8]:
        sc, cfg = inst.scenario, inst.scenario.config
        h = VisibleHistory(sc.brief, [(None, sc.build(inst.hidden).reset())])
        acts = [str(a) for a in legal_actions(cfg, h.last)]
        assert RF.decision_messages(prompts, cfg, sc.brief, h, acts) == policy_messages(prompts, cfg, sc.brief, h, None, 7)[0]


def test_fallback_tracker_reads_no_hidden_values():
    import inspect
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import run_hybrid_fallback as RF
    src = inspect.getsource(RF.tracker_check) + inspect.getsource(RF.check_messages) + inspect.getsource(RF.decision_messages)
    assert "hidden" not in src.replace("hidden-variable", "") and "world" not in src
