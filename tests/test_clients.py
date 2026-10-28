import importlib.util
from pathlib import Path

from vomi.clients import MockClient

ROOT = Path(__file__).resolve().parents[1]


def _smoke():
    spec = importlib.util.spec_from_file_location("smoke", ROOT / "scripts" / "smoke_local_model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_mock_client_never_reports_reasoning_tokens_as_zero():
    r = MockClient(['{"action": "wait", "abstain": false}']).chat([{"role": "user", "content": "x"}])
    assert r.reasoning_tokens is None and r.prompt_tokens is None


def test_smoke_prompt_is_agent_visible_only_and_validator_works():
    smoke = _smoke()
    messages, acts, schema = smoke.decision_messages()
    text = messages[0]["content"]
    assert "rec_saw" not in text and "bs-alice-walks" not in text and "purpose" not in text
    assert smoke.validate('{"action": "wait()", "abstain": false}', acts) == (True, "wait()")
    assert smoke.validate('{"action": "fly", "abstain": false}', acts) == (False, "schema_violation")
    assert smoke.validate("I think wait", acts) == (False, "not_json")
