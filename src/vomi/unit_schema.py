"""Typed unit output for LLM instantiation calls (D-007; Stage 1 review correction 2).

Each selected unit returns a typed hypothesis about ONE (path, variable): what j believes (K(j)),
what j believes k believes (K(j->k)), j's intent (R(j)), or j's assessment of k (R(j->k)).
Outputs must cite robot-visible evidence IDs and may not contain task-action recommendations,
other minds' complete states, or anything read from the hidden world.
"""

from __future__ import annotations

import json

KNOWLEDGE_VALUES_EXTRA = ("unknown",)
INTENT_VALUES = ("cooperative", "obstructive", "unknown")
FORBIDDEN_KEYS = {"action", "recommended_action", "next_action", "answer", "true_state", "hidden"}


def unit_output_schema(fact_domain: list[str]) -> dict:
    """JSON schema for structured decoding (vLLM `response_format`)."""
    knowledge_values = list(fact_domain) + list(KNOWLEDGE_VALUES_EXTRA)
    hypothesis = {
        "type": "object",
        "properties": {
            "value": {"type": "string", "enum": sorted(set(knowledge_values) | set(INTENT_VALUES))},
            "p": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["value", "p"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "path": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
            "variable": {"type": "string", "enum": ["knowledge", "reliability"]},
            "about": {"type": "string"},  # the query fact (knowledge) or assessed person (reliability)
            "as_of_step": {"type": "integer", "minimum": 0},
            "hypotheses": {"type": "array", "items": hypothesis, "minItems": 1},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
            "unresolved": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["path", "variable", "about", "as_of_step", "hypotheses", "evidence_ids", "unresolved"],
        "additionalProperties": False,
    }


def validate_unit_output(text: str, path: tuple[str, ...], variable: str, fact_domain: list[str],
                         visible_ids: set[str], tol: float = 1e-3) -> tuple[dict | None, list[str]]:
    """Declared failure protocol: returns (parsed, errors). Malformed outputs are never dropped
    silently; callers record the errors and apply the bounded-retry / abstain rule."""
    errors = []
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None, ["not_json"]
    if not isinstance(obj, dict):
        return None, ["not_object"]
    if FORBIDDEN_KEYS & set(obj):
        errors.append("out_of_scope_field")
    if tuple(obj.get("path", ())) != tuple(path) or obj.get("variable") != variable:
        errors.append("wrong_unit")
    allowed = set(fact_domain) | {"unknown"} if variable == "knowledge" else set(INTENT_VALUES)
    hyps = obj.get("hypotheses") or []
    if not hyps or any(h.get("value") not in allowed for h in hyps):
        errors.append("bad_hypothesis_value")
    elif abs(sum(float(h.get("p", 0)) for h in hyps) - 1.0) > tol:
        errors.append("probabilities_not_normalized")
    if any(e not in visible_ids for e in obj.get("evidence_ids", [])):
        errors.append("cites_non_visible_evidence")
    return (obj if not errors else None), errors
