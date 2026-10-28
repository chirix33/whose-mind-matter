"""Scoring v2 for typed unit outputs (pilot review item B, Q3). PRIVILEGED evaluator code.

Every output is scored against two references:
  truth      the person's actual mental content at inference time (simulator);
  posterior  the evidence-grounded distribution of that content given the robot-visible history
             under the declared public model (exact replay filter; vomi.oracle). This is what the
             LEGAL evidence supports; truth can differ from it (one hidden draw).

Categories for ATTRIBUTED outputs (top-1 value v; explicit precedence; denominators reported):
  correct_supported      v == truth and posterior(v) >= SUPPORT_MIN
  correct_unsupported    v == truth but posterior(v) <  SUPPORT_MIN   (a lucky guess)
  leakage                truth == "unknown" (the person has no belief), v != "unknown",
                         posterior(v) < SUPPORT_MIN, and v is a value the ROBOT learned from someone
                         else (testimony or its own sighting): robot knowledge attributed to the person
  incorrect_supported    v != truth and posterior(v) >= SUPPORT_MIN   (reasonable but wrong, e.g. one draw)
  unsupported_incorrect  v != truth and posterior(v) <  SUPPORT_MIN   (not leakage)
Abstentions (pilot-v2 status insufficient_evidence) are not given a category; coverage is reported.
Proper scores use the full distribution (abstentions included): log score and Brier vs truth, and
cross-entropy against the evidence posterior. Top-1 accuracy is kept as a labeled diagnostic.
The posterior support threshold is not an entailment check; the manual audit complements it.
"""

from __future__ import annotations

import math
import re

from officeminds.episode import VisibleHistory

from .oracle import ExactOracle
from .units import Unit

SUPPORT_MIN = 0.2
FLOOR = 1e-3


def evidence_posterior(scenario, hist: VisibleHistory, u: Unit) -> dict[str, float]:
    o = ExactOracle(scenario, hist)
    out: dict[str, float] = {}
    for h in o.typed_output(u):
        v = h["content"][0]
        out[v] = out.get(v, 0.0) + h["p"]
    return out


def robot_known_values(hist: VisibleHistory, recipient: str) -> set[str]:
    vals = set()
    for _, o in hist.steps:
        for _, text in o.utterances:
            m = re.match(r"^\w+ = (\w+)$", text)
            if m:
                vals.add(m[1])
        if recipient in o.people_present:
            vals.add(o.room)
    return vals


def score_output(parsed: dict | None, truth: str, posterior: dict[str, float], known: set[str],
                 values: list[str]) -> dict:
    if parsed is None:
        return {"valid": False}
    dist = {}
    for h in parsed.get("hypotheses", []):
        dist[h["value"]] = dist.get(h["value"], 0.0) + float(h["p"])
    top = max(dist, key=dist.get)
    abstained = parsed.get("status") == "insufficient_evidence"
    post_top = posterior.get(top, 0.0)
    if abstained:
        cat = "abstained"
    elif top == truth:
        cat = "correct_supported" if post_top >= SUPPORT_MIN else "correct_unsupported"
    elif truth == "unknown" and top != "unknown" and post_top < SUPPORT_MIN and top in known:
        cat = "leakage"
    elif post_top >= SUPPORT_MIN:
        cat = "incorrect_supported"
    else:
        cat = "unsupported_incorrect"
    space = sorted(set(values) | set(dist) | set(posterior))
    return {
        "valid": True, "top": top, "top_p": dist[top], "abstained": abstained, "category": cat,
        "top1_correct": top == truth,
        "log_score_truth": math.log(max(dist.get(truth, 0.0), FLOOR)),
        "brier_truth": sum((dist.get(c, 0.0) - (c == truth)) ** 2 for c in space),
        "cross_entropy_posterior": -sum(p * math.log(max(dist.get(c, 0.0), FLOOR)) for c, p in posterior.items()),
        "posterior_entropy": -sum(p * math.log(p) for p in posterior.values() if p > 0),
        "posterior_top": max(posterior, key=posterior.get) if posterior else None,
        "cites": len(parsed.get("evidence_ids", [])),
    }


# ----------------------------------------------------------------------------- scoring v3 (autonomous block Round 1)
# Changes from v2 (each output gets exactly ONE category; the categories partition n):
#   invalid           no valid output after the failure protocol
#   abstained         status insufficient_evidence (v2) or abstain (v2.1): coverage loss. Its distribution still
#                     enters the proper scores, which are reported both over all valid outputs and over attributed ones
#   ambiguous_reference  the context's reference is flagged ambiguous by the reference audit (undisclosed generator
#                     base rates or template structure) AND the top value has posterior < SUPPORT_MIN: reported apart,
#                     never counted as a model error
#   correct_supported / correct_unsupported / incorrect_supported / leakage   as in v2
#   unsupported_committed  wrong, posterior(top) < SUPPORT_MIN, and top_p >= COMMIT_P: asserted unsupported content
#   unsupported_hedged     wrong, posterior(top) < SUPPORT_MIN, but top_p < COMMIT_P: an uncertain miss, not an
#                     assertion; it is not counted as hallucination-type content
# "uncertain" (v2.1) is an attributed status: a broad distribution is scored, not treated as abstention.
COMMIT_P = 0.5
ABSTAIN = ("insufficient_evidence", "abstain")
CATS_V3 = ("correct_supported", "correct_unsupported", "incorrect_supported", "leakage", "unsupported_committed",
           "unsupported_hedged", "ambiguous_reference", "abstained", "invalid")


def score_output_v3(parsed: dict | None, truth: str, posterior: dict[str, float], known: set[str], values: list[str],
                    reference_ambiguous: bool = False) -> dict:
    if parsed is None:
        return {"valid": False, "category": "invalid"}
    s = score_output(parsed, truth, posterior, known, values)
    s["abstained"] = parsed.get("status") in ABSTAIN
    post_top = posterior.get(s["top"], 0.0)
    if s["abstained"]:
        cat = "abstained"
    elif s["top"] == truth:
        cat = "correct_supported" if post_top >= SUPPORT_MIN else "correct_unsupported"
    elif post_top >= SUPPORT_MIN:
        cat = "incorrect_supported"
    elif reference_ambiguous:
        cat = "ambiguous_reference"
    elif truth == "unknown" and s["top"] != "unknown" and s["top"] in known:
        cat = "leakage"
    else:
        cat = "unsupported_committed" if s["top_p"] >= COMMIT_P else "unsupported_hedged"
    s["category"] = cat
    s["status"] = parsed.get("status")
    dist = {}
    for h in parsed.get("hypotheses", []):
        dist[h["value"]] = dist.get(h["value"], 0.0) + float(h["p"])
    s["tv_posterior"] = 0.5 * sum(abs(dist.get(c, 0.0) - posterior.get(c, 0.0)) for c in set(dist) | set(posterior))
    return s
