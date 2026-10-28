"""Autonomous block Round 1: grounding package pilot-v2.1 and scoring v3."""

from __future__ import annotations

import json

import pytest

from officeminds.devgen import generate
from officeminds.episode import VisibleHistory
from vomi.fidelity import CATS_V3, score_output_v3
from vomi.graph import PerspectiveGraph
from vomi.pilot import PACKAGES, PEOPLE_RULES_R4, load_prompts, notes_text, unit_messages
from vomi.unit_schema import validate_unit_output_v21
from vomi.units import Unit

DOMAIN = ["office_a", "office_b"]
IDS = {"t0:said0", "t0:seen:bob"}


def out(status, hyps, path=("bob",)):
    return json.dumps({"path": list(path), "variable": "knowledge", "about": "alice_loc", "as_of_step": 0,
                       "status": status, "hypotheses": hyps, "unresolved": []})


def sup(eid, kind):
    return [{"evidence_id": eid, "kind": kind, "note": "n"}]


def test_v21_accepts_rule_support_and_broad_uncertain_distributions():
    text = out("uncertain", [{"value": "office_a", "p": 0.5, "support": sup("RULE2", "public_rule")},
                             {"value": "office_b", "p": 0.5, "support": sup("RULE2", "public_rule")}])
    parsed, errors = validate_unit_output_v21(text, ("bob",), "knowledge", DOMAIN, IDS)
    assert errors == [] and parsed["rule_ids"] == ["RULE2"] and parsed["evidence_ids"] == []


@pytest.mark.parametrize("hyps,status,err", [
    ([{"value": "office_a", "p": 1.0, "support": []}], "grounded", "unsupported_hypothesis"),
    ([{"value": "office_a", "p": 1.0, "support": sup("t9:said0", "testimony")}], "grounded", "cites_non_visible_evidence"),
    ([{"value": "office_a", "p": 1.0, "support": sup("RULE2", "testimony")}], "grounded", "rule_citation_mismatch"),
    ([{"value": "office_a", "p": 1.0, "support": sup("t0:said0", "public_rule")}], "grounded", "rule_citation_mismatch"),
    ([{"value": "office_a", "p": 1.0, "support": sup("t0:said0", "testimony")}], "insufficient_evidence", "bad_status"),
])
def test_v21_structural_failures_are_named(hyps, status, err):
    _, errors = validate_unit_output_v21(out(status, hyps), ("bob",), "knowledge", DOMAIN, IDS)
    assert err in errors


def test_v21_abstention_does_not_need_support():
    parsed, errors = validate_unit_output_v21(out("abstain", [{"value": "office_a", "p": 0.5, "support": []},
                                                              {"value": "office_b", "p": 0.5, "support": []}]),
                                              ("bob",), "knowledge", DOMAIN, IDS)
    assert errors == []


def test_v21_requests_render_r4_rules_and_require_r4():
    inst = generate(version="dev-v2")[0]
    w = inst.scenario.build(inst.hidden)
    h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
    u = Unit((inst.scenario.config.recipient,), "knowledge")
    msgs, _, _ = unit_messages(load_prompts("pilot-v2.1"), inst.scenario.config, inst.scenario.brief, h, u, "pilot-v2.1", 4)
    assert PEOPLE_RULES_R4 in msgs[1]["content"] and "RULE" in msgs[0]["content"]
    assert PACKAGES["pilot-v2.1"].min_render_revision == 4


def score(parsed_hyps, status, truth, posterior, ambiguous=False, known=()):
    return score_output_v3({"status": status, "hypotheses": parsed_hyps}, truth, posterior, set(known),
                           ["office_a", "office_b", "unknown"], ambiguous)


def test_v3_categories_partition_and_separate_hedged_from_committed():
    post = {"office_a": 1.0}
    assert score([{"value": "office_a", "p": 0.9}], "grounded", "office_a", post)["category"] == "correct_supported"
    assert score([{"value": "office_b", "p": 0.9}], "grounded", "office_a", post)["category"] == "unsupported_committed"
    assert score([{"value": "office_b", "p": 0.4}, {"value": "office_a", "p": 0.35}, {"value": "unknown", "p": 0.25}],
                 "uncertain", "office_a", post)["category"] == "unsupported_hedged"
    assert score([{"value": "office_b", "p": 0.9}], "grounded", "office_a", post, ambiguous=True)["category"] == "ambiguous_reference"
    assert score([{"value": "office_b", "p": 0.9}], "abstain", "office_a", post)["category"] == "abstained"
    assert score([{"value": "office_b", "p": 0.9}], "insufficient_evidence", "office_a", post)["category"] == "abstained"
    assert score_output_v3(None, "office_a", post, set(), [])["category"] == "invalid"
    lk = score([{"value": "office_b", "p": 0.9}], "grounded", "unknown", {"unknown": 1.0}, known=("office_b",))
    assert lk["category"] == "leakage"
    assert set(CATS_V3) >= {"correct_supported", "unsupported_committed", "ambiguous_reference", "abstained", "invalid"}


def test_v31_tied_top_category_does_not_depend_on_list_order():
    post = {"office_a": 0.5, "office_b": 0.5}
    a = score([{"value": "office_a", "p": 0.5}, {"value": "office_b", "p": 0.5}], "uncertain", "office_b", post)
    b = score([{"value": "office_b", "p": 0.5}, {"value": "office_a", "p": 0.5}], "uncertain", "office_b", post)
    assert a["category"] == b["category"] == "supported_spread"
    # an unsupported value tied with a supported one does not decide the category
    c = score([{"value": "unknown", "p": 0.5}, {"value": "office_a", "p": 0.5}], "uncertain", "office_b", post)
    d = score([{"value": "office_a", "p": 0.5}, {"value": "unknown", "p": 0.5}], "uncertain", "office_b", post)
    assert c["category"] == d["category"] == "incorrect_supported"
    # all tied values unsupported: committed unsupported content regardless of order
    e = score([{"value": "office_a", "p": 0.5}, {"value": "office_b", "p": 0.5}], "grounded", "unknown", {"unknown": 1.0})
    f = score([{"value": "office_b", "p": 0.5}, {"value": "office_a", "p": 0.5}], "grounded", "unknown", {"unknown": 1.0})
    assert e["category"] == f["category"] == "unsupported_committed"


def test_v3_supported_wrong_answer_is_not_hallucination_even_in_ambiguous_contexts():
    s = score([{"value": "office_b", "p": 0.9}], "grounded", "office_a", {"office_a": 0.5, "office_b": 0.5}, ambiguous=True)
    assert s["category"] == "incorrect_supported"


def test_uncertain_status_is_rendered_and_not_shown_as_abstention():
    inst = generate(version="dev-v2")[0]
    w = inst.scenario.build(inst.hidden)
    h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
    g = PerspectiveGraph(recipient=inst.scenario.config.recipient, refutation_mode="fact_only")
    u = Unit((inst.scenario.config.recipient,), "knowledge")
    o = {"path": list(u.path), "variable": "knowledge", "about": "x", "as_of_step": 0, "status": "uncertain",
         "hypotheses": [{"value": "a", "p": 0.5, "support": sup("RULE2", "public_rule")},
                        {"value": "b", "p": 0.5, "support": sup("RULE2", "public_rule")}],
         "unresolved": [], "evidence_ids": [], "rule_ids": ["RULE2"]}
    g.instantiate(u, o, [], t=0)
    text = notes_text(g, h, 4)
    assert "INFERENCE UNCERTAIN" in text and "ABSTAINED" not in text and "RULE2 public_rule" in text
