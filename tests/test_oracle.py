"""Exact symbolic-oracle checks against hand-derived values (derivations in implementation-spec §6)."""

import pytest

from officeminds.episode import VisibleHistory
from officeminds.scenarios import TINY_CASES
from officeminds.world import Action
from vomi.oracle import ExactOracle, brute_force_best_return
from vomi.units import K, R, generate_candidates


def oracle(case):
    sc = TINY_CASES[case]()
    w = sc.build(sc.prior[0][0])
    hist = VisibleHistory(sc.brief, [(None, w.reset())])
    return sc, hist, ExactOracle(sc, hist)


def J(o, *units, continuation="retain"):
    return o.evaluate(frozenset(units), continuation).value


def test_depth0_needs_no_mental_units():
    _, _, o = oracle("depth0_visible")
    assert J(o) == pytest.approx(0.95)
    assert o.evaluate().actions[0] == Action("deliver")
    r = o.unit_report(K("rec"))
    assert r.content_entropy_bits == pytest.approx(1.0)  # content varies ...
    assert r.p_flip == 0 and r.delta_j == pytest.approx(0)  # ... but can never flip the action (P1)


def test_depth1_knowledge_hand_values():
    _, _, o = oracle("depth1_knowledge")
    # ask rec (1 step); known -> drop (0.90); unknown -> walk (0.80 - 0.05 avg) => 0.825
    assert J(o) == pytest.approx(0.825)
    # K(rec) known -> drop now (0.95); unknown -> walk (0.80) => 0.875
    assert J(o, K("rec")) == pytest.approx(0.875)
    assert o.evaluate().actions[0] == Action("ask", "rec", "alice_loc")
    r = o.unit_report(K("rec"), lam=0.1)
    assert r.p_flip == pytest.approx(1.0) and r.net_vomi == pytest.approx(0.05 - 0.1)


def test_plausible_vs_obvious_distractor():
    _, _, o = oracle("distractor_plausible")
    assert J(o) == pytest.approx(0.8375)
    assert J(o, K("rec")) == pytest.approx(0.8875)
    assert J(o, K("carol")) == pytest.approx(0.8875)
    assert J(o, K("rec"), K("carol")) == pytest.approx(0.9125)
    _, _, o = oracle("distractor_obvious")
    r = o.unit_report(K("carol"))
    assert r.content_entropy_bits == 0 and r.p_flip == 0 and r.net_vomi == 0  # pruned by P1


def test_substitutes_make_gold_sets_non_unique():
    sc, hist, o = oracle("substitutes")
    assert J(o) == pytest.approx(0.90)
    units = generate_candidates(sc.config, hist)
    assert set(units) == {K("alice"), K("bob"), K("alice", "bob"), K("bob", "alice")}
    labels = o.allocation_labels(units)
    assert labels.j_full == pytest.approx(0.95)
    assert sorted(labels.minimal_sufficient) == [["K(alice)"], ["K(alice->bob)"], ["K(bob)"], ["K(bob->alice)"]]
    assert labels.loo_necessary == []  # no single unit is necessary, yet each has value 0.05
    assert o.unit_report(K("alice"), S={K("bob", "alice")}).delta_j == pytest.approx(0)


def test_depth2_complementary_pair_and_certification():
    sc, hist, o = oracle("depth2_handoff")
    a, ra = K("alice"), K("rec", "alice")
    assert J(o) == pytest.approx(0.80)
    assert J(o, a) == pytest.approx(0.85)
    assert J(o, ra) == pytest.approx(0.80)
    assert J(o, a, ra) == pytest.approx(0.90)
    # Neither unit alone flips the first action; together they do (P3a, first-step flips).
    base = o.evaluate().actions
    assert o.evaluate(frozenset({a})).actions == base
    assert o.evaluate(frozenset({ra})).actions == base
    assert o.evaluate(frozenset({a, ra})).actions != base
    # K(alice) alone has value without any first-step flip under "retain": §3.4 decomposition residual.
    r = o.unit_report(a)
    assert r.p_flip == 0 and r.no_flip_residual == pytest.approx(0.05)
    # Under "drop" continuation the decomposition is exact and K(alice) alone is worthless.
    assert o.unit_report(a, continuation="drop").delta_j == pytest.approx(0)
    units = generate_candidates(sc.config, hist)
    assert o.effective_depth(units) == 2
    assert o.indistinguishable_pairs(units, below_depth=2)  # depth-1 identical, decisions differ
    labels = o.allocation_labels(units)
    assert ["K(alice)", "K(rec->alice)"] in labels.minimal_sufficient
    assert ["K(alice)", "K(alice->rec)"] in labels.minimal_sufficient  # substitute path


@pytest.mark.parametrize("q", [0.975, 0.95])
def test_stakes_pairs(q):
    out = {}
    for m in (1, 4):
        _, _, o = oracle(f"stakes_m{m}_q{q}")
        assert len(o.worlds) == 2  # the visible claim filters to (A, coop) and (B, obstructive)
        out[m] = o.unit_report(R("bob"))
    assert out[1].content_entropy_bits == pytest.approx(out[4].content_entropy_bits)
    if q == 0.975:  # base action is drop(office_a) at both stakes
        assert out[1].p_flip == pytest.approx(out[4].p_flip) == pytest.approx(0.025)
        assert out[1].delta_j == pytest.approx(0.0375) and out[4].delta_j == pytest.approx(0.075)
    else:  # base action itself changes with stakes, so flip probability changes too (P5 caveat)
        assert out[1].p_flip == pytest.approx(0.05) and out[4].p_flip == pytest.approx(1.0)


@pytest.mark.parametrize("case", sorted(TINY_CASES))
def test_point_mass_expectimax_matches_brute_force(case):
    """Independent check: with a single known world, belief expectimax == exhaustive sequence search."""
    sc, _, o = oracle(case)
    for _, w in o.belief:
        single = ((1.0, w),)
        assert o.value(single, o.obs) == pytest.approx(brute_force_best_return(w, o.obs))


@pytest.mark.parametrize("case", sorted(TINY_CASES))
def test_value_identities(case):
    sc, hist, o = oracle(case)
    units = generate_candidates(sc.config, hist)
    full_info = sum(p * brute_force_best_return(w, o.obs) for p, w in o.belief)
    v = o.value(o.belief, o.obs)
    assert J(o) == pytest.approx(v)  # J(empty) is the Bayes-optimal value
    assert v <= J(o, *units) + 1e-9 <= full_info + 2e-9  # information never hurts the symbolic agent
