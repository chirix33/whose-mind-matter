"""Pilot pipeline with a scripted mock client (no model). Real-model runs live in scripts/run_pilot.py."""

import json

import pytest

from officeminds.devgen import generate
from officeminds.episode import VisibleHistory
from vomi.clients import ChatResult
from vomi.pilot import ARMS, BUDGET, MAX_ATTEMPTS, ledger, load_prompts, policy_messages, run_episode_arm, task_card


class SchemaMock:
    """Answers from the request's JSON schema: first legal action, first allowed unit value, first candidate."""

    def __init__(self, garbage: bool = False):
        self.garbage, self.n = garbage, 0

    def chat(self, messages, **params):
        self.n += 1
        if self.garbage:
            return ChatResult("not json", None, "mock", "stop", 10, 2, None, 0.0)
        schema = params["response_format"]["json_schema"]["schema"]["properties"]
        if "action" in schema:
            acts = schema["action"]["enum"]
            out = {"action": next((a for a in acts if a.startswith("deliver")), acts[0])}
        elif "select" in schema:
            out = {"select": schema["select"]["items"]["enum"][:1], "stop": False}
        else:
            user = messages[-1]["content"]
            path = json.loads(user.split("path=")[1].split(", variable=")[0])
            var = user.split('variable="')[1].split('"')[0]
            about = user.split('about="')[1].split('"')[0]
            out = {"path": path, "variable": var, "about": about, "as_of_step": 0,
                   "hypotheses": [{"value": schema["hypotheses"]["items"]["properties"]["value"]["enum"][0], "p": 1.0}],
                   "evidence_ids": [], "unresolved": []}
        return ChatResult(json.dumps(out), "mock reasoning", "mock", "stop", 100, 20, None, 0.01)


DECODING = {"temperature": 0.0, "max_tokens": 64}


@pytest.fixture(scope="module")
def insts():
    return {i.instance_id: i for i in generate()}


@pytest.mark.parametrize("arm", ARMS)
def test_every_arm_runs_an_episode_with_accounting(insts, arm):
    inst = insts["dev-v2-nested_reliability-g0-permuted0"]
    r = run_episode_arm(SchemaMock(), inst, arm, DECODING, reference_set=["K(pia)"])
    assert r.steps >= 1 and r.outcome in ("success", "error", "timeout")
    assert "decision" in r.usage and r.usage["decision"]["calls"] == r.steps
    assert r.usage["decision"]["reasoning_tokens_known"] is False  # unknown is never reported as 0
    if arm == "direct":
        assert r.privileged["units_instantiated"] == 0 and "unit" not in r.usage
    if arm in ("random", "router"):
        assert r.privileged["units_instantiated"] <= BUDGET
    if arm == "router":
        assert r.usage["router"]["calls"] >= 1


def test_failure_protocol_logs_attempts_and_falls_back(insts):
    inst = insts["dev-v2-stop-g0-bystander1"]
    r = run_episode_arm(SchemaMock(garbage=True), inst, "dense", DECODING)
    dec = [c for c in r.calls if c["kind"] == "decision"]
    assert all(len(c["attempts"]) == MAX_ATTEMPTS and c["fallback"] == "wait()" for c in dec)
    assert r.outcome == "timeout" and r.usage["decision"]["fallbacks"] == r.steps
    units = [c for c in r.calls if c["kind"] == "unit"]
    assert units and all(not c["ok"] for c in units) and r.graph_final == []  # abstained units are not notes


def test_rendered_policy_request_is_visible_only_and_carries_stakes(insts):
    prompts = load_prompts()
    for iid in ("dev-v2-false_belief-g2-stakes1-evidence1", "dev-v2-false_belief-g2-stakes4-evidence1"):
        inst = insts[iid]
        w = inst.scenario.build(inst.hidden)
        hist = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
        msgs, _ = policy_messages(prompts, inst.scenario.config, inst.scenario.brief, hist, None)
        text = msgs[-1]["content"]
        assert f"costs -{0.5 * inst.scenario.config.stakes:g}" in text
        for key, val in inst.hidden:
            assert key not in text
        assert "bs-" not in text


def test_symbolic_arm_passes_llm_content_not_truth(insts):
    inst = insts["dev-v2-false_belief-g2-stakes1-evidence0"]
    r = run_episode_arm(SchemaMock(), inst, "symbolic", DECODING, reference_set=["K(" + inst.scenario.config.roster[0] + ")"])
    for note in r.graph_final:  # notes come from the (mock) LLM unit output, never from content()
        assert note["output"]["hypotheses"][0]["p"] == 1.0
