"""Pilot-review repairs: r3 interface, pilot-v2 package, scoring v2, Responses adapter + spend cap (no network)."""

import io
import json

import pytest

from officeminds.devgen import generate
from officeminds.episode import VisibleHistory
from officeminds.world import Action
from vomi import clients
from vomi.clients import BudgetExceeded, OpenAIResponsesClient, SpendLedger
from vomi.fidelity import score_output
from vomi.graph import PerspectiveGraph
from vomi.pilot import PEOPLE_RULES, load_prompts, notes_text, policy_messages, task_card, unit_messages
from vomi.unit_schema import unit_output_schema_v2, validate_unit_output_v2
from vomi.units import K


def v2(status="attributed", hyps=None):
    return json.dumps({"path": ["kim"], "variable": "knowledge", "about": "x_loc", "as_of_step": 1, "status": status,
                       "hypotheses": hyps if hyps is not None else [{"value": "a", "p": 1.0, "support": []}], "unresolved": []})


def test_v2_validator_requires_support_only_for_attributions():
    args = (("kim",), "knowledge", ["a", "b"], {"t0:said0"})
    assert validate_unit_output_v2(v2(), *args)[1] == ["unsupported_hypothesis"]  # confident claim, no support
    ok, errs = validate_unit_output_v2(v2(hyps=[{"value": "a", "p": 1.0, "support": [{"evidence_id": "t0:said0",
                                                                                     "kind": "testimony", "note": "said a"}]}]), *args)
    assert errs == [] and ok["evidence_ids"] == ["t0:said0"]
    spread = [{"value": "a", "p": 0.4, "support": []}, {"value": "b", "p": 0.3, "support": []}, {"value": "unknown", "p": 0.3, "support": []}]
    assert validate_unit_output_v2(v2("insufficient_evidence", spread), *args)[1] == []  # abstention: no false ignorance claim
    bad = [{"value": "a", "p": 1.0, "support": [{"evidence_id": "bs-secret", "kind": "observation", "note": ""}]}]
    assert "cites_non_visible_evidence" in validate_unit_output_v2(v2(hyps=bad), *args)[1]
    schema = unit_output_schema_v2(["a", "b"], "knowledge")
    assert set(schema["required"]) == set(schema["properties"]) and schema["additionalProperties"] is False  # strict-mode ready


def test_r3_task_card_and_notes_show_rules_evidence_and_abstention():
    inst = generate()[0]
    cfg = inst.scenario.config
    w = inst.scenario.build(inst.hidden)
    h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
    assert PEOPLE_RULES in task_card(cfg, inst.scenario.brief, rev=3) and PEOPLE_RULES not in task_card(cfg, inst.scenario.brief, rev=2)
    g = PerspectiveGraph(recipient=cfg.recipient, refutation_mode="fact_only")
    out = json.loads(v2("insufficient_evidence", [{"value": "unknown", "p": 1.0, "support": []}]))
    out["evidence_ids"] = [f"t0:seen:{h.last.people_present[0]}"] if h.last.people_present else []
    g.instantiate(K("kim"), out, out["evidence_ids"], t=0)
    text = notes_text(g, h, rev=3)
    assert "INFERENCE ABSTAINED" in text and "cited evidence" in text
    if out["evidence_ids"]:
        assert "excerpts: [" in text
    assert "INFERENCE ABSTAINED" not in notes_text(g, h, rev=2)  # r2 rendering preserved for the original run


def test_fact_refutation_keeps_the_belief_attribution():
    from officeminds.scenarios import ALL_CASES
    sc = ALL_CASES["false_belief"]()
    w = sc.build((("initial", "office_a"), ("moved", "yes")))
    h = VisibleHistory(sc.brief, [(None, w.reset())])
    for a in (Action("ask", "rec", "alice_loc"), Action("move", "hall"), Action("move", "office_a")):
        h.steps.append((a, w.step(a)))
    for mode, expected in (("contradict", "contradicted"), ("fact_only", "fact_refuted")):
        g = PerspectiveGraph(refutation_mode=mode)
        g.instantiate(K("rec"), {"hypotheses": [{"value": "office_a", "p": 0.9}]}, [], t=1)
        g.advance(h)
        assert g.units["K(rec)"].status == expected


def test_scoring_v2_categories():
    vals = ["a", "b", "unknown"]
    out = lambda top, status="attributed": {"status": status, "hypotheses": [{"value": top, "p": 0.9}] +
                                            [{"value": v, "p": 0.05} for v in vals if v != top]}
    post = {"unknown": 0.9, "a": 0.1}
    assert score_output(out("unknown"), "unknown", post, {"a"}, vals)["category"] == "correct_supported"
    assert score_output(out("a"), "unknown", post, {"a"}, vals)["category"] == "leakage"  # robot-known value, no access
    assert score_output(out("b"), "unknown", post, {"a"}, vals)["category"] == "unsupported_incorrect"
    assert score_output(out("a"), "a", post, {"a"}, vals)["category"] == "correct_unsupported"  # lucky guess
    assert score_output(out("a"), "b", {"a": 0.6, "b": 0.4}, set(), vals)["category"] == "incorrect_supported"
    s = score_output(out("a", "insufficient_evidence"), "unknown", post, {"a"}, vals)
    assert s["category"] == "abstained" and s["abstained"] and s["log_score_truth"] < 0
    assert score_output(None, "a", post, set(), vals) == {"valid": False}


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_responses_adapter_mapping_incomplete_refusal_and_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_KEY", "sk-test")
    ledger = SpendLedger(str(tmp_path / "ledger.json"), cap_usd=0.05, price_in=2.0, price_out=10.0)
    c = OpenAIResponsesClient("gpt-6.1-sol", "FAKE_KEY", ledger)
    schema = {"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"], "additionalProperties": False}
    body = c.request_body("gpt-6.1-sol", [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}],
                          {"reasoning_effort": "low", "max_tokens": 900, "temperature": 0.0,
                           "response_format": {"type": "json_schema", "json_schema": {"name": "unit", "schema": schema}}})
    assert body["reasoning"] == {"effort": "low"} and body["max_output_tokens"] == 900 and "temperature" not in body
    assert body["text"]["format"] == {"type": "json_schema", "name": "unit", "schema": schema, "strict": True}
    assert body["input"][0]["role"] == "developer"
    replies = [
        {"status": "completed", "model": "gpt-6.1-sol", "usage": {"input_tokens": 1000, "output_tokens": 500,
         "output_tokens_details": {"reasoning_tokens": 300}}, "output": [{"type": "message", "content": [{"type": "output_text", "text": "{\"x\": \"1\"}"}]}]},
        {"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}, "usage": {"input_tokens": 1000, "output_tokens": 900}, "output": []},
        {"status": "completed", "usage": {"input_tokens": 10, "output_tokens": 5}, "output": [{"type": "message", "content": [{"type": "refusal", "refusal": "no"}]}]},
    ]
    monkeypatch.setattr(clients.urllib.request, "urlopen", lambda req, timeout: _Resp(json.dumps(replies.pop(0)).encode()))
    r = c.chat([{"role": "user", "content": "u"}], max_tokens=900)
    assert r.text == '{"x": "1"}' and r.reasoning_tokens == 300 and r.error is None
    r = c.chat([{"role": "user", "content": "u"}], max_tokens=900)
    assert r.error == "incomplete: max_output_tokens" and r.text == ""
    r = c.chat([{"role": "user", "content": "u"}], max_tokens=900)
    assert r.error.startswith("refusal") and r.text == ""
    assert ledger.state["spent_usd"] == pytest.approx((1000 + 1000 + 10) * 2e-6 + (500 + 900 + 5) * 1e-5)
    with pytest.raises(BudgetExceeded):  # spent ~0.018 + worst case of 4096 output tokens > 0.05
        c.chat([{"role": "user", "content": "u" * 3000}], max_tokens=4096)


def test_missing_api_key_is_reported_not_guessed(monkeypatch, tmp_path):
    monkeypatch.delenv("NO_SUCH_KEY", raising=False)
    with pytest.raises(RuntimeError, match="not set"):
        OpenAIResponsesClient("gpt-6.1-sol", "NO_SUCH_KEY", SpendLedger(str(tmp_path / "l.json"), 5, 2, 10))


def test_unit_requests_for_both_packages_render(tmp_path):
    inst = generate()[0]
    w = inst.scenario.build(inst.hidden)
    h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
    u = K(inst.scenario.config.recipient)
    for pkg in ("pilot-v1", "pilot-v2"):
        msgs, _, _ = unit_messages(load_prompts(pkg), inst.scenario.config, inst.scenario.brief, h, u, pkg, 3)
        assert PEOPLE_RULES in msgs[1]["content"]
        assert ("insufficient_evidence" in msgs[1]["content"]) == (pkg == "pilot-v2")
    pm, _ = policy_messages(load_prompts(), inst.scenario.config, inst.scenario.brief, h, None, 3)
    assert PEOPLE_RULES in pm[1]["content"]
