"""Grounded bounded-policy labels (D-001/D-002 review outcomes). Hand derivations in spec §6.2."""

import json

import pytest

from officeminds.episode import VisibleHistory
from officeminds.scenarios import ALL_CASES
from officeminds.world import Action
from vomi.graph import PerspectiveGraph, visible_evidence, visible_features
from vomi.oracle import GROUNDED_SCALAR, PRIVILEGED_BAYES, PRIVILEGED_BOUNDED, ExactOracle
from vomi.units import K, R, generate_candidates


def setup(case, testimony="face_value", params=None):
    sc = ALL_CASES[case]()
    w = sc.build(params or sc.prior[0][0])
    hist = VisibleHistory(sc.brief, [(None, w.reset())])
    return sc, hist, ExactOracle(sc, hist, testimony=testimony)


def J(o, *units, record=GROUNDED_SCALAR):
    return o.evaluate(frozenset(units), record=record).value


# ------------------------------------------------------------------ D-001 invariance pair
def test_invisible_world_pair_gives_identical_actor_inputs_and_outputs():
    """Two hidden worlds (Alice switched offices or not) with identical visible history."""
    pa = (("initial", "office_a"), ("moved", "yes"))
    pb = (("initial", "office_a"), ("moved", "no"))
    sa, ha, oa = setup("false_belief", params=pa)
    sb, hb, ob = setup("false_belief", params=pb)
    assert json.dumps(ha.to_agent_dict()) == json.dumps(hb.to_agent_dict())
    ca, cb = generate_candidates(sa.config, ha), generate_candidates(sb.config, hb)
    assert ca == cb
    for u in ca:
        assert oa.grounded_output(u) == ob.grounded_output(u)
        ma = oa.decision_margin(oa.actor_items(frozenset(), GROUNDED_SCALAR, 0), oa.obs)
        mb = ob.decision_margin(ob.actor_items(frozenset(), GROUNDED_SCALAR, 0), ob.obs)
        assert visible_features(sa.config, ha, u, ma) == visible_features(sb.config, hb, u, mb)
        # The grounded actor's action is the same in every world consistent with h ...
        acts = {str(a) for a in oa.evaluate(frozenset({u}), record=GROUNDED_SCALAR).actions}
        assert len(acts) == 1
    # ... whereas Alice's PRIVATE content differs across the pair (rec's belief does not), so only
    # the privileged record lets that difference reach the actor.
    priv = oa.evaluate(frozenset({K("alice")}), record=PRIVILEGED_BOUNDED).actions
    assert len({str(a) for a in priv}) > 1


def test_unsupported_unit_gets_no_value_from_hidden_truth():
    """Legacy record rewards K(alice) for revealing an absent person's mind; the grounded record does not."""
    _, _, o = setup("depth1_knowledge")
    assert J(o, K("alice"), record=PRIVILEGED_BAYES) - J(o, record=PRIVILEGED_BAYES) == pytest.approx(0.125)
    assert J(o, K("alice")) - J(o) == pytest.approx(0.0)


# ------------------------------------------------------------------ false belief / testimony default
def test_false_belief_hand_values_and_testimony_robustness():
    _, _, o = setup("false_belief")
    # Face value: ask rec, trust the answer, drop: 0.7*0.90 + 0.3*(-0.05-0.05-0.5) = 0.45
    assert J(o) == pytest.approx(0.45)
    assert o.evaluate(record=GROUNDED_SCALAR).actions[0] == Action("ask", "rec", "alice_loc")
    # K(rec): P(outdated)=0.3 so walking now (0.5*0.85 + 0.5*0.75 = 0.80) beats ask-and-walk (0.77)
    assert J(o, K("rec")) == pytest.approx(0.80)
    d = o.decompose(K("rec"))
    assert (d.d_action, d.d_memory, d.residual) == pytest.approx((0.35, 0.0, 0.0), abs=1e-9)
    assert J(o, K("alice")) == pytest.approx(J(o))
    # Hedged default (eps=0.25): P_actor(moved)=0.075/0.775, so it already walks (0.80): the gain vanishes.
    _, _, oh = setup("false_belief", testimony="hedged")
    assert J(oh) == pytest.approx(0.80) and J(oh, K("rec")) == pytest.approx(0.80)


def test_direct_testimony_default_acts_on_face_value():
    """Bob claims office_a: the face-value actor drops there immediately (stakes x4, q=0.95)."""
    _, _, o = setup("stakes_m4_q0.95")
    assert o.evaluate(record=GROUNDED_SCALAR).actions[0] == Action("drop", "office_a")
    assert J(o) == pytest.approx(0.95 * 0.95 - 0.05 * 2.05)
    # Grounded R(bob): P(A)=0.95 < 0.9655 threshold at x4 -> walk: 0.95*0.85 + 0.05*0.75
    assert J(o, R("bob")) == pytest.approx(0.845)
    # Regression: K(alice)'s belief equals the target, so exposing its content marginal would leak
    # the whole-scene posterior. Grounded outputs carry only P(default holds | h): no value here.
    assert J(o, K("alice")) == pytest.approx(J(o))
    assert o.grounded_output(K("alice"))["p_default_holds"] == pytest.approx(1.0)


# ------------------------------------------------------------------ nested reliability R(j->k)
def test_nested_reliability_case():
    sc, hist, o = setup("nested_reliability")
    units = generate_candidates(sc.config, hist)
    assert R("rec", "bob") in units and R("bob") in units
    # Face value: give(rec) succeeds unless Bob lied AND rec is naive (0.25): 0.75*0.95 - 0.25*0.55
    assert J(o) == pytest.approx(0.575)
    for u in (R("rec", "bob"), K("rec")):  # each exposes the 0.25 failure mass -> walk (0.80)
        assert J(o, u) == pytest.approx(0.80)
    assert J(o, R("bob")) == pytest.approx(0.575)  # default assumes rec sees through Bob
    # Complementary grounded pair: neither alone, both together.
    assert J(o, K("bob", "rec")) == pytest.approx(0.575)
    assert J(o, K("bob", "rec"), R("bob")) == pytest.approx(0.80)


def test_nested_r_content_is_rec_assessment_not_bob_intent():
    from vomi.units import content
    sc = ALL_CASES["nested_reliability"]()
    w = sc.build((("alice_loc", "office_a"), ("bob_intent", "obstructive"), ("rec_naive", "yes")))
    assert content(w, R("bob")) == ("obstructive",)
    assert content(w, R("rec", "bob")) == ("cooperative",)  # a false assessment
    assert w.minds["rec"].beliefs["alice_loc"] == "office_b"  # adopted Bob's lie


# ------------------------------------------------------------------ D-002 decomposition
def test_depth2_handoff_retention_counterexample_decomposes_exactly():
    """Review-required display: the legacy carryover example with both Q evaluations."""
    _, _, o = setup("depth2_handoff")
    d = o.decompose(K("alice"), record=PRIVILEGED_BAYES)
    assert d.q_m_a0 == pytest.approx(0.80)  # J(∅)
    assert d.q_m_ay == pytest.approx(0.80)  # same current action, continuation without the unit
    assert d.q_my_ay == pytest.approx(0.85)  # same action, continuation retains K(alice)
    assert d.d_action == pytest.approx(0.0) and d.d_memory == pytest.approx(0.05)
    assert abs(d.residual) < 1e-12 and d.p_flip == 0 and d.carryover


@pytest.mark.parametrize("case", sorted(ALL_CASES))
@pytest.mark.parametrize("record", [GROUNDED_SCALAR, PRIVILEGED_BOUNDED, PRIVILEGED_BAYES])
def test_decomposition_identity_everywhere(case, record):
    sc, hist, o = setup(case)
    for u in generate_candidates(sc.config, hist):
        d = o.decompose(u, record=record)
        assert abs(d.residual) < 1e-12
        assert d.delta_j == pytest.approx(J(o, u, record=record) - J(o, record=record))


def test_path_asymmetry_directed_unit_with_negative_current_action_component():
    _, _, o = setup("path_asymmetry")
    assert J(o) == pytest.approx(0.575)  # forwarding fails iff Alice heard and did not tell rec (0.25)
    assert J(o, K("rec", "alice")) == pytest.approx(0.80)
    for u in (K("alice", "rec"), K("rec"), K("alice")):
        assert J(o, u) == pytest.approx(0.575)
    d = o.decompose(K("rec", "alice"))
    # Current action flips give->move(hall); the default continuation walks back and gives (3 steps):
    # 0.75*0.85 + 0.25*(-0.65) = 0.475, so D_action = -0.10 and D_memory = +0.325.
    assert d.q_m_ay == pytest.approx(0.475)
    assert (d.d_action, d.d_memory) == pytest.approx((-0.10, 0.325))


# ------------------------------------------------------------------ F3 relevance shift, holder permutation
def test_relevance_shift_turns_rec_off_when_alice_appears():
    sc, hist, o = setup("relevance_shift")
    assert J(o) == pytest.approx(0.675)  # 0.5*0.90 + 0.5*(0.7*0.90 + 0.3*(-0.60))
    assert J(o, K("rec")) == pytest.approx(0.835)  # 0.5*0.90 + 0.5*(0.7*0.80 + 0.3*0.70)
    d = o.decompose(K("rec"))
    assert d.p_flip == 0 and d.d_memory == pytest.approx(0.16) and d.carryover
    w = sc.build((("initial", "office_a"), ("moved", "yes"), ("returns", "yes")))
    h1 = VisibleHistory(sc.brief, [(None, w.reset())])
    h1.steps.append((Action("wait"), w.step(Action("wait"))))
    assert "alice" in h1.last.people_present
    o1 = ExactOracle(sc, h1)
    assert J(o1) == pytest.approx(0.95) and J(o1, K("rec")) == pytest.approx(0.95)


def test_holder_permutation_is_name_symmetric():
    _, _, orec = setup("holder_rec")
    _, _, ocar = setup("holder_carol")
    assert J(orec) == pytest.approx(J(ocar)) == pytest.approx(0.45)
    assert J(orec, K("rec")) == pytest.approx(J(ocar, K("carol"))) == pytest.approx(0.80)
    assert J(orec, K("carol")) == pytest.approx(J(ocar, K("rec"))) == pytest.approx(0.45)


# ------------------------------------------------------------------ D-006 ranking reversal
def test_stakes_ranking_reversal_privileged_bounded():
    """Bob says A, Carol says B. Consistent worlds (alice, bob, carol) with weights ∝ 0.5*b*c:
    w1 (A, acc, mist) .016; w2 (A, acc, obs) .64; w3 (B, mist, acc) .01; w4 (B, obs, acc) .025.
    Default actor: w1 and w3 each violate one default -> P(A)=.016/.026 -> walk A-first:
    J0 = (p1+p2)*0.85 + (p3+p4)*0.75. U=R(bob) flips only in w4 (walk -> drop B, +0.2, stake-free).
    V=K(carol) reveals Carol's belief but not its accuracy: the actor blames Carol and drops A everywhere."""
    from officeminds.scenarios import REVERSAL_WITNESS
    s = 0.016 + 0.64 + 0.01 + 0.025
    pA, p4 = (0.016 + 0.64) / s, 0.025 / s
    j0 = pA * 0.85 + (1 - pA) * 0.75
    out = {}
    for m in (1, 4):
        _, _, o = setup(f"reversal_m{m}", params=REVERSAL_WITNESS)
        assert len(o.worlds) == 4 and J(o, record=PRIVILEGED_BOUNDED) == pytest.approx(j0)
        u, v = o.decompose(R("bob"), record=PRIVILEGED_BOUNDED), o.decompose(K("carol"), record=PRIVILEGED_BOUNDED)
        assert u.delta_j == pytest.approx(p4 * 0.2)
        assert v.delta_j == pytest.approx(pA * 0.95 - (1 - pA) * (0.05 + 0.5 * m) - j0)
        assert u.d_memory == v.d_memory == 0
        assert (u.p_flip, v.p_flip) == pytest.approx((p4, 1.0))  # flip ranking V > U at both stakes
        out[m] = (u.delta_j, v.delta_j)
    assert out[1][0] < out[1][1] and out[4][0] > out[4][1]  # VoMI ranking reverses
    # Isolation: identical base action and targets across stakes.
    o1, o4 = (setup(f"reversal_m{m}", params=REVERSAL_WITNESS)[2] for m in (1, 4))
    for S in (frozenset(), frozenset({R("bob")}), frozenset({K("carol")})):
        assert o1.evaluate(S, record=PRIVILEGED_BOUNDED).actions == o4.evaluate(S, record=PRIVILEGED_BOUNDED).actions


# ------------------------------------------------------------------ graph retention
def test_graph_retains_units_and_tracks_new_evidence_without_new_cost():
    sc, hist, o = setup("false_belief")
    g = PerspectiveGraph()
    g.instantiate(K("rec"), o.grounded_output(K("rec")), visible_evidence(hist, ("rec",)), t=0)
    with pytest.raises(ValueError):
        g.instantiate(K("rec"), o.grounded_output(K("rec")), [], t=0)
    w = sc.build(sc.prior[0][0])
    w.reset()
    hist.steps.append((Action("wait"), w.step(Action("wait"))))
    g.advance(hist)
    assert g.units["K(rec)"].status == "stale"  # rec still visible: new evidence, no new inference
    assert g.total_cost() == 1.0
    rec = g.units["K(rec)"]
    assert rec.confidence == pytest.approx(0.7)  # P(rec's belief is not outdated | h)
    # Contradiction from the robot's own observation: rec said office_a, robot finds it empty.
    w = sc.build((("initial", "office_a"), ("moved", "yes")))
    h = VisibleHistory(sc.brief, [(None, w.reset())])
    for a in (Action("ask", "rec", "alice_loc"), Action("move", "hall"), Action("move", "office_a")):
        h.steps.append((a, w.step(a)))
    g2 = PerspectiveGraph()
    g2.instantiate(K("rec"), o.grounded_output(K("rec")), [], t=0)
    g2.advance(h)
    assert g2.units["K(rec)"].status == "contradicted"
