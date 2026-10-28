"""Stage 1 review corrections: depth consistency, polarity, typed vs scalar outputs, best-subset
reference, unit-vs-STOP stakes pair, and an evidence-change trace (D-007, D-011)."""

import pytest

from officeminds.episode import VisibleHistory
from officeminds.scenarios import ALL_CASES, REVERSAL_WITNESS
from officeminds.world import Action
from vomi.allocation import conditional_relevance, minimal_sufficient, reference_value, score_allocation, stop
from vomi.graph import PerspectiveGraph, visible_evidence
from vomi.oracle import GROUNDED_SCALAR, GROUNDED_TYPED, PRIVILEGED_BAYES, PRIVILEGED_BOUNDED, ExactOracle
from vomi.units import K, R, default_holds, generate_candidates


def setup(case, testimony="face_value", params=None):
    sc = ALL_CASES[case]()
    params = params or (REVERSAL_WITNESS if case.startswith("reversal") else sc.prior[0][0])
    w = sc.build(params)
    hist = VisibleHistory(sc.brief, [(None, w.reset())])
    return sc, hist, ExactOracle(sc, hist, testimony=testimony)


# ------------------------------------------------------------------ correction 1: depth
@pytest.mark.parametrize("case", sorted(ALL_CASES))
@pytest.mark.parametrize("record", [GROUNDED_SCALAR, GROUNDED_TYPED, PRIVILEGED_BOUNDED, PRIVILEGED_BAYES])
def test_required_depth_never_exceeds_a_sufficient_sets_depth(case, record):
    sc, hist, o = setup(case)
    units = generate_candidates(sc.config, hist)
    d = o.effective_depth(units, record=record)
    gold = minimal_sufficient(o.subset_values(units, record=record))
    depths = [max((u.depth for u in G), default=0) for G in gold]
    assert d <= min(depths) and d == min(depths)


def test_depth_claims_from_review():
    for testimony, expected in (("face_value", 2), ("hedged", 0)):
        sc, hist, o = setup("path_asymmetry", testimony)
        assert o.effective_depth(generate_candidates(sc.config, hist), record=GROUNDED_SCALAR) == expected
    sc, hist, o = setup("nested_reliability")
    assert o.effective_depth(generate_candidates(sc.config, hist), record=GROUNDED_SCALAR) == 1  # {K(rec)} suffices


# ------------------------------------------------------------------ correction 5: polarity
@pytest.mark.parametrize("case", ["false_belief", "nested_reliability", "path_asymmetry", "relevance_shift"])
def test_scalar_output_polarity_and_projection(case):
    sc, hist, o = setup(case)
    for u in generate_candidates(sc.config, hist):
        out = o.grounded_output(u)
        assert set(out) == {"p_default_holds", "p_default_violated"}
        assert out["p_default_holds"] + out["p_default_violated"] == pytest.approx(1.0)
        # After I-projection the actor's own marginal equals the unit output (same event, same polarity).
        assert o.actor_marginal_holds(u, {u}, GROUNDED_SCALAR) == pytest.approx(out["p_default_holds"], abs=1e-9)


def test_unknown_counts_as_satisfying_a_knowledge_default():
    sc = ALL_CASES["depth1_knowledge"]()
    w = sc.build((("alice_loc", "office_a"), ("rec_saw", "no")))
    assert w.minds["rec"].beliefs.get("alice_loc") is None and default_holds(w, K("rec"))
    _, _, o = setup("false_belief")
    assert o.grounded_output(K("rec")) == {"p_default_holds": pytest.approx(0.7), "p_default_violated": pytest.approx(0.3)}


# ------------------------------------------------------------------ correction 2: typed vs scalar
def test_typed_output_carries_content_and_can_legitimately_help():
    """stakes_m4_q0.95: Alice's belief, inferred from visible evidence under the declared model,
    is useful content (typed +0.045); the scalar diagnostic carries only accuracy (0)."""
    _, _, o = setup("stakes_m4_q0.95")
    typed = o.typed_output(K("alice"))
    assert sum(h["p"] for h in typed) == pytest.approx(1.0)
    assert {tuple(h["content"]) for h in typed} == {("office_a",), ("office_b",)}
    assert all(h["default_holds"] for h in typed)  # Alice knows where she is
    j0 = o.evaluate(record=GROUNDED_TYPED).value
    assert o.evaluate(frozenset({K("alice")}), record=GROUNDED_TYPED).value - j0 == pytest.approx(0.045)
    assert o.decompose(K("alice"), record=GROUNDED_SCALAR).delta_j == pytest.approx(0.0)


def test_typed_outputs_are_identical_across_invisible_world_pair():
    _, _, oa = setup("false_belief", params=(("initial", "office_a"), ("moved", "yes")))
    _, _, ob = setup("false_belief", params=(("initial", "office_a"), ("moved", "no")))
    for u in (K("rec"), K("alice")):
        assert oa.typed_output(u) == ob.typed_output(u)


def test_typed_llm_unit_schema_and_failure_protocol():
    import json
    from vomi.unit_schema import unit_output_schema, validate_unit_output
    dom = ["office_a", "office_b"]
    schema = unit_output_schema(dom)
    assert "action" not in schema["properties"] and schema["additionalProperties"] is False
    ok = {"path": ["rec"], "variable": "knowledge", "about": "alice_loc", "as_of_step": 1,
          "hypotheses": [{"value": "office_a", "p": 0.7}, {"value": "unknown", "p": 0.3}],
          "evidence_ids": ["t1:said0:rec"], "unresolved": ["Alice may have moved after rec saw her"]}
    parsed, errs = validate_unit_output(json.dumps(ok), ("rec",), "knowledge", dom, {"t1:said0:rec"})
    assert parsed is not None and errs == []
    bad = dict(ok, recommended_action="drop(office_a)", evidence_ids=["bs-alice-switches"])
    parsed, errs = validate_unit_output(json.dumps(bad), ("rec",), "knowledge", dom, {"t1:said0:rec"})
    assert parsed is None and set(errs) == {"out_of_scope_field", "cites_non_visible_evidence"}
    assert validate_unit_output("rec probably knows", ("rec",), "knowledge", dom, set()) == (None, ["not_json"])


# ------------------------------------------------------------------ correction 4: best-subset reference
def test_best_subset_reference_differs_from_j_all_when_non_monotone():
    a, b = "a", "b"
    v = {frozenset(): 0.5, frozenset({a}): 0.9, frozenset({b}): 0.6, frozenset({a, b}): 0.7}
    assert reference_value(v) == 0.9 and reference_value(v, reference="all") == 0.7
    assert minimal_sufficient(v) == [frozenset({a})]
    s = score_allocation(frozenset({a, b}), v)
    assert s.regret == pytest.approx(0.2) and s.regret_vs_all_historical == pytest.approx(0.0)
    assert s.wasted == ["b"]  # J(A) - J(A - b) = -0.2 <= 0
    assert stop(frozenset({a}), v) and not stop(frozenset({b}), v)
    assert conditional_relevance(frozenset(), v) == {a}
    assert conditional_relevance(frozenset({b}), v) == {a}  # best reachable superset of {b} is {a, b}
    # Net objective with a stated price: the empty allocation can be optimal.
    assert minimal_sufficient(v, lam=0.5) == [frozenset()]


# ------------------------------------------------------------------ D-011: unit vs STOP stakes pair
def test_grounded_unit_vs_stop_isolating_stakes_pair():
    p_err = 35 / 691
    res = {}
    for m in (1, 4):
        sc, hist, o = setup(f"reversal_m{m}")
        units = generate_candidates(sc.config, hist)
        d = o.decompose(K("bob"), record=GROUNDED_SCALAR)
        res[m] = (units, d, o.grounded_output(K("bob")), o)
        assert d.delta_j == pytest.approx(0.95 - (1 + 0.5 * m) * p_err - (0.85 - 0.10 * p_err))
        assert (d.p_flip, d.d_memory, d.a0, d.ay) == (1.0, 0.0, "move(hall)", "drop(office_a)")
        table = o.outcome_table(frozenset({K("bob")}), GROUNDED_SCALAR)
        assert sum(r["posterior"] for r in table if r["params"]["alice_loc"] == "office_b") == pytest.approx(p_err)
        assert {r["action"] for r in table} == {"drop(office_a)"}
    (u1, d1, g1, o1), (u4, d4, g4, o4) = res[1], res[4]
    assert u1 == u4 and g1 == g4 and o1.params == o4.params  # same candidates, inference output, prior
    lam = 0.01  # illustrative price per one-call unit, held fixed across stakes (not a measured cost)
    assert d1.net_vomi(lam) == pytest.approx(0.01909, abs=1e-5) and d4.net_vomi(lam) == pytest.approx(-0.05689, abs=1e-5)
    for m, prefers_stop in ((1, False), (4, True)):
        o = res[m][3]
        v = o.subset_values([K("bob")], record=GROUNDED_SCALAR)
        assert stop(frozenset(), v, lam=lam) is prefers_stop


# ------------------------------------------------------------------ D-007: evidence changes an inference
def test_trace_where_new_evidence_changes_a_useful_inference():
    sc = ALL_CASES["false_belief"]()
    w = sc.build((("initial", "office_a"), ("moved", "yes")))
    h = VisibleHistory(sc.brief, [(None, w.reset())])
    h.steps.append((Action("ask", "rec", "alice_loc"), w.step(Action("ask", "rec", "alice_loc"))))
    o1 = ExactOracle(sc, h)
    g = PerspectiveGraph()
    g.instantiate(K("rec"), o1.grounded_output(K("rec")), visible_evidence(h, ("rec",)), t=1)
    assert g.units["K(rec)"].output["p_default_holds"] == pytest.approx(0.7)
    for a in (Action("move", "hall"), Action("move", "office_a")):
        h.steps.append((a, w.step(a)))
    g.advance(h)
    assert g.policy_view()[0]["status"] == "contradicted"  # visible to the policy, not silently used
    o3 = ExactOracle(sc, h)
    g.refresh(K("rec"), o3.grounded_output(K("rec")), visible_evidence(h, ("rec",)), t=3)
    rec = g.units["K(rec)"]
    assert rec.output["p_default_holds"] == pytest.approx(0.0) and rec.status == "refreshed"
    assert rec.cost_calls == 2.0 and rec.history[0]["output"]["p_default_holds"] == pytest.approx(0.7)
    g.advance(h)  # the old refutation predates the refresh: no re-flagging
    assert rec.status == "retained"
