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


def unit_output_schema(fact_domain: list[str], variable: str | None = None) -> dict:
    """JSON schema for structured decoding (vLLM `response_format`). With `variable`, hypothesis
    values are restricted to that variable's type (rooms + unknown, or intents)."""
    knowledge_values = list(fact_domain) + list(KNOWLEDGE_VALUES_EXTRA)
    values = {"knowledge": set(knowledge_values), "reliability": set(INTENT_VALUES)}.get(
        variable, set(knowledge_values) | set(INTENT_VALUES))
    hypothesis = {
        "type": "object",
        "properties": {
            "value": {"type": "string", "enum": sorted(values)},
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


# ----------------------------------------------------------------------------- package pilot-v2 (grounding revision)
# Pilot review (2026-10-28) items A/B:
# - each hypothesis carries its own support: visible evidence ID + kind (direct observation,
#   testimony, or an inference about who had access) + a short note;
# - `unknown` means the PERSON has no belief. If the ROBOT cannot tell, the unit sets
#   status = "insufficient_evidence" and still gives its distribution over the person's possible
#   contents; that is an inference abstention, never a claim that the person is ignorant.
# The validator is a STRUCTURAL check only: a cited ID can be real but irrelevant; support
# adequacy is judged by scoring (vomi.fidelity) and audit, not here.
SUPPORT_KINDS = ("observation", "testimony", "access_inference")
STATUSES = ("attributed", "insufficient_evidence")
SUPPORT_MIN_P = 0.05  # hypotheses at or above this mass need support when status == attributed


def unit_output_schema_v2(fact_domain: list[str], variable: str) -> dict:
    values = sorted(set(fact_domain) | {"unknown"}) if variable == "knowledge" else sorted(INTENT_VALUES)
    support = {"type": "object", "properties": {
        "evidence_id": {"type": "string"}, "kind": {"type": "string", "enum": list(SUPPORT_KINDS)},
        "note": {"type": "string"}}, "required": ["evidence_id", "kind", "note"], "additionalProperties": False}
    hypothesis = {"type": "object", "properties": {
        "value": {"type": "string", "enum": values}, "p": {"type": "number", "minimum": 0, "maximum": 1},
        "support": {"type": "array", "items": support}}, "required": ["value", "p", "support"], "additionalProperties": False}
    return {"type": "object", "properties": {
        "path": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
        "variable": {"type": "string", "enum": ["knowledge", "reliability"]},
        "about": {"type": "string"}, "as_of_step": {"type": "integer", "minimum": 0},
        "status": {"type": "string", "enum": list(STATUSES)},
        "hypotheses": {"type": "array", "items": hypothesis, "minItems": 1},
        "unresolved": {"type": "array", "items": {"type": "string"}}},
        "required": ["path", "variable", "about", "as_of_step", "status", "hypotheses", "unresolved"],
        "additionalProperties": False}


def validate_unit_output_v2(text: str, path: tuple[str, ...], variable: str, fact_domain: list[str],
                            visible_ids: set[str], tol: float = 1e-3) -> tuple[dict | None, list[str]]:
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
    if obj.get("status") not in STATUSES:
        errors.append("bad_status")
    allowed = set(fact_domain) | {"unknown"} if variable == "knowledge" else set(INTENT_VALUES)
    hyps = obj.get("hypotheses") or []
    if not hyps or any(h.get("value") not in allowed for h in hyps):
        errors.append("bad_hypothesis_value")
    elif abs(sum(float(h.get("p", 0)) for h in hyps) - 1.0) > tol:
        errors.append("probabilities_not_normalized")
    cited = [s.get("evidence_id") for h in hyps for s in (h.get("support") or [])]
    if any(e not in visible_ids for e in cited):
        errors.append("cites_non_visible_evidence")
    if obj.get("status") == "attributed" and any(float(h.get("p", 0)) >= SUPPORT_MIN_P and not h.get("support") for h in hyps):
        errors.append("unsupported_hypothesis")
    if not errors:
        obj["evidence_ids"] = sorted({e for e in cited})  # graph/notes convenience; derived, not model-supplied
    return (obj if not errors else None), errors


# ----------------------------------------------------------------------------- package pilot-v2.1 (autonomous block Round 1)
# Separates three things pilot-v2 conflated: the PERSON has no belief ("unknown" with its own support), the
# ROBOT is unsure which belief they hold (status "uncertain", a broad distribution: a normal output), and full
# abstention (status "abstain", rare). Support may cite a numbered r4 public rule ("RULE<n>", kind public_rule).
# Still a STRUCTURAL validator: cited support is not checked for entailment (scoring + audit do that).
SUPPORT_KINDS_V21 = SUPPORT_KINDS + ("public_rule",)
STATUSES_V21 = ("grounded", "uncertain", "abstain")
RULE_IDS = tuple(f"RULE{i}" for i in range(1, 7))


def unit_output_schema_v21(fact_domain: list[str], variable: str) -> dict:
    s = unit_output_schema_v2(fact_domain, variable)
    s["properties"]["status"]["enum"] = list(STATUSES_V21)
    s["properties"]["hypotheses"]["items"]["properties"]["support"]["items"]["properties"]["kind"]["enum"] = list(SUPPORT_KINDS_V21)
    return s


def validate_unit_output_v21(text: str, path: tuple[str, ...], variable: str, fact_domain: list[str],
                             visible_ids: set[str], tol: float = 1e-3) -> tuple[dict | None, list[str]]:
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
    if obj.get("status") not in STATUSES_V21:
        errors.append("bad_status")
    allowed = set(fact_domain) | {"unknown"} if variable == "knowledge" else set(INTENT_VALUES)
    hyps = obj.get("hypotheses") or []
    if not hyps or any(h.get("value") not in allowed for h in hyps):
        errors.append("bad_hypothesis_value")
    elif abs(sum(float(h.get("p", 0)) for h in hyps) - 1.0) > tol:
        errors.append("probabilities_not_normalized")
    supports = [s for h in hyps for s in (h.get("support") or [])]
    if any(s.get("evidence_id") not in visible_ids | set(RULE_IDS) for s in supports):
        errors.append("cites_non_visible_evidence")
    if any((s.get("kind") == "public_rule") != (s.get("evidence_id") in RULE_IDS) for s in supports):
        errors.append("rule_citation_mismatch")
    if obj.get("status") != "abstain" and any(float(h.get("p", 0)) >= SUPPORT_MIN_P and not h.get("support") for h in hyps):
        errors.append("unsupported_hypothesis")
    if not errors:
        obj["evidence_ids"] = sorted({s["evidence_id"] for s in supports if s["evidence_id"] not in RULE_IDS})
        obj["rule_ids"] = sorted({s["evidence_id"] for s in supports if s["evidence_id"] in RULE_IDS})
    return (obj if not errors else None), errors
