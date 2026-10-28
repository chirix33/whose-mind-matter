"""D-003 set-valued gold + conditional D4 target; P2 boundary checks; D-005 reward/horizon semantics."""

import pytest

from officeminds.episode import VisibleHistory
from officeminds.scenarios import ALL_CASES, _config
from officeminds.world import Action, Event, PersonMind, World
from vomi.allocation import conditional_relevance, minimal_sufficient, score_allocation, stop
from vomi.oracle import GROUNDED_SCALAR, PRIVILEGED_BAYES, ExactOracle
from vomi.theory import best_return_by_outcome, gap_decrease_bounds, p2_certifies_no_flip
from vomi.units import K, R, content, generate_candidates


def values_for(case, record, units=None):
    sc = ALL_CASES[case]()
    w = sc.build(sc.prior[0][0])
    hist = VisibleHistory(sc.brief, [(None, w.reset())])
    o = ExactOracle(sc, hist)
    units = units or generate_candidates(sc.config, hist)
    return o, units, o.subset_values(units, record=record)


# ------------------------------------------------------------------ D-003 / D4
def test_substitutes_conditional_relevance_and_stop():
    _, units, v = values_for("substitutes", PRIVILEGED_BAYES)
    assert conditional_relevance(frozenset(), v) == set(units)  # every substitute completes ∅
    assert stop(frozenset({K("bob")}), v)  # after one substitute: STOP ...
    assert conditional_relevance(frozenset({K("bob")}), v) == set()  # ... and nothing else is relevant
    s = score_allocation(frozenset({K("bob")}), v)
    assert (s.matched_gold, s.precision, s.recall, s.f1, s.regret) == (["K(bob)"], 1.0, 1.0, 1.0, 0.0)
    s2 = score_allocation(frozenset({K("bob"), K("alice")}), v)
    assert s2.matched_gold == ["K(alice)"] and (s2.precision, s2.recall) == (0.5, 1.0)  # one matched set
    assert sorted(s2.wasted) == ["K(alice)", "K(bob)"]  # each is redundant given the other


def test_complementary_bundle_is_missed_as_a_bundle_not_as_units():
    o, _, _ = values_for("nested_reliability", GROUNDED_SCALAR)
    pair = [K("bob", "rec"), R("bob")]
    v = o.subset_values(pair, record=GROUNDED_SCALAR)
    assert minimal_sufficient(v) == [frozenset(pair)]
    s = score_allocation(frozenset(), v)
    assert s.missed == [] and s.missed_bundles == [sorted(map(str, pair))]
    assert conditional_relevance(frozenset({R("bob")}), v) == {K("bob", "rec")}
    assert s.regret == pytest.approx(0.225) and s.regret_budget == 0.0  # nothing fits a 0-unit budget


def test_minimum_cost_completion_variant():
    _, units, v = values_for("nested_reliability", GROUNDED_SCALAR)
    full = conditional_relevance(frozenset(), v)
    cheap = conditional_relevance(frozenset(), v, minimum_cost=True)
    assert cheap == {K("rec"), K("rec", "bob"), R("rec", "bob")} < full


# ------------------------------------------------------------------ P2
def test_p2_strict_inequality_and_tie_boundary():
    q = {"a": 1.0, "b": 0.8, "c": 0.5}
    assert p2_certifies_no_flip(q, {"b": 0.19, "c": 0.4})
    assert not p2_certifies_no_flip(q, {"b": 0.2, "c": 0.4})  # equality: a tie is possible


def test_per_action_bound_is_not_a_gap_bound():
    """|Δq(a)| <= 0.1 for every action does NOT bound the gap change by 0.1 (it is up to 0.2)."""
    q = {"a": 1.0, "b": 0.85}
    q_after = {"a": 0.9, "b": 0.95}  # each moved by 0.1
    assert max(abs(q_after[x] - q[x]) for x in q) == pytest.approx(0.1)
    assert p2_certifies_no_flip(q, {"b": 0.1})  # unsound certification from per-action bound ...
    assert max(q_after, key=q_after.get) == "b"  # ... yet the action flips
    assert not p2_certifies_no_flip(q, gap_decrease_bounds(q, [q_after]))  # exact gap bound is sound


@pytest.mark.parametrize("case", ["depth1_knowledge", "distractor_plausible", "substitutes", "stakes_m1_q0.975"])
def test_p2_certification_implies_no_current_action_flip(case):
    """End-to-end on the legacy record: exact gap bounds over every feasible content of a unit."""
    o, units, _ = values_for(case, PRIVILEGED_BAYES)
    q0 = dict(o.ranked_actions(o.belief, o.obs))
    for u in units:
        contents = sorted({content(x, u) for x in o.worlds})
        q_by_c = []
        for c in contents:
            items = tuple((p, x) for p, x in o.belief if content(x, u) == c)
            total = sum(p for p, _ in items)
            q_by_c.append(dict(o.ranked_actions(tuple((p / total, x) for p, x in items), o.obs)))
        if p2_certifies_no_flip(q0, gap_decrease_bounds(q0, q_by_c)):
            assert o.decompose(u, record=PRIVILEGED_BAYES).p_flip == 0


# ------------------------------------------------------------------ D-005 reward / horizon
def _one_room_world(horizon):
    cfg = _config(["alice", "rec"], ["alice_loc"], handoff={"rec": ("", "alice_loc")}, horizon=horizon)
    minds = {"alice": PersonMind(), "rec": PersonMind()}
    bs = (Event("bs", -1, "witness", "hall", "alice", "alice_loc", "office_b", present=("alice", "rec")),)
    return World(cfg, "lobby", {"alice": "office_b", "rec": "office_a"}, minds, bs)


def test_success_on_last_allowed_step_counts():
    w = _one_room_world(horizon=1)
    w.reset()
    o = w.step(Action("drop", "office_b"))
    assert (o.outcome, o.reward, o.done) == ("success", pytest.approx(0.95), True)


def test_timeout_has_no_extra_penalty_and_invalid_action_is_a_costed_noop():
    w = _one_room_world(horizon=2)
    w.reset()
    o1 = w.step(Action("give", "rec"))  # rec is not co-located: invalid -> no-op
    assert (o1.done, o1.reward) == (False, pytest.approx(-0.05))
    o2 = w.step(Action("wait"))
    assert (o2.outcome, o2.reward) == ("timeout", pytest.approx(-0.05))


def test_misrouted_handoff_is_terminal_irreversible_error():
    sc = ALL_CASES["nested_reliability"]()
    w = sc.build((("alice_loc", "office_a"), ("bob_intent", "obstructive"), ("rec_naive", "yes")))
    w.reset()
    o = w.step(Action("give", "rec"))
    assert (o.outcome, o.reward, o.done) == ("error", pytest.approx(-0.55), True)


@pytest.mark.parametrize("case", sorted(ALL_CASES))
def test_no_early_failure_incentive_under_full_information(case):
    """D-005 audit: in every hypothesis world, the best success beats every failure outcome."""
    sc = ALL_CASES[case]()
    for params, _ in sc.prior:
        w = sc.build(params)
        best = best_return_by_outcome(w, w.reset())
        failures = [v for k, v in best.items() if k != "success"]
        assert "success" in best and all(best["success"] > f for f in failures), (case, params, best)
