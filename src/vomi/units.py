"""Modeling units u = (path, variable), their true content, and visible-only candidate generation.

Content semantics (implementation-spec §3):
- K(j):     j's belief about each public query fact (``unknown`` if j holds none).
            This is j's epistemic state, not the objective truth: it can be false.
- R(j):     j's stable intent type (cooperative | obstructive). Statement correctness
            is derived from belief vs. truth and is not a unit variable.
- K(j->k):  j's belief about k's belief about each query fact.
            Neither k's actual state nor the robot's belief about k.
- R(j->k):  j's belief about k's intent. Not populated by Tier 1 mechanics yet, so it is
            never generated as a candidate (open item in the spec).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from officeminds.episode import VisibleHistory
from officeminds.world import UNKNOWN, World, WorldConfig

KNOWLEDGE = "knowledge"
RELIABILITY = "reliability"

_INCENTIVE = re.compile(r"\b(i'd rather|i would rather|i want|keep (it|that|the) \w* ?myself)\b", re.I)
_CLAIM = re.compile(r"^(\w+) = (\w+)$")


@dataclass(frozen=True, order=True)
class Unit:
    path: tuple[str, ...]
    variable: str

    @property
    def depth(self) -> int:
        return len(self.path)

    def __str__(self) -> str:
        return f"{self.variable[0].upper()}({'->'.join(self.path)})"


def K(*path: str) -> Unit:
    return Unit(tuple(path), KNOWLEDGE)


def R(*path: str) -> Unit:
    return Unit(tuple(path), RELIABILITY)


def content(world: World, unit: Unit) -> tuple:
    """True content of ``unit`` in ``world`` (privileged; used for oracle labels only)."""
    j = unit.path[0]
    mind = world.minds.get(j)
    if mind is None:
        return ("absent",)
    facts = world.config.query_facts
    if unit.depth == 1:
        if unit.variable == KNOWLEDGE:
            return tuple(mind.beliefs.get(f, UNKNOWN) for f in facts)
        return (mind.intent,)
    k = unit.path[1]
    if unit.variable == KNOWLEDGE:
        return tuple(mind.nested.get((k, f), UNKNOWN) for f in facts)
    return (UNKNOWN,)


def _mentions(text: str, name: str) -> bool:
    return re.search(rf"\b{re.escape(name)}\b", text, re.I) is not None


def generate_candidates(config: WorldConfig, hist: VisibleHistory) -> list[Unit]:
    """Structural preconditions (outline §4.1) evaluated on robot-visible information only."""
    observations = [o for _, o in hist.steps]
    utterances = [u for o in observations for u in o.utterances]
    texts = [hist.brief] + [t for _, t in utterances]

    observed = {p for o in observations for p in o.people_present} | {s for s, _ in utterances}
    mentioned = {p for p in config.roster if any(_mentions(t, p) for t in texts)}
    known = sorted((observed | mentioned) & set(config.roster))

    units = [K(j) for j in known]
    for j in known:
        for k in known:
            if j == k:
                continue
            talked = any(s in (j, k) and _mentions(t, k if s == j else j) for s, t in utterances)
            together = any(j in o.people_present and k in o.people_present for o in observations)
            if talked or together:
                units.append(K(j, k))

    claims: dict[str, set[str]] = {}
    claimants: dict[str, set[str]] = {}
    for s, t in utterances:
        if m := _CLAIM.match(t):
            claims.setdefault(m[1], set()).add(m[2])
            claimants.setdefault(m[1], set()).add(s)
    conflicted = {s for f, vals in claims.items() if len(vals) > 1 for s in claimants[f]}
    for j in known:
        if j in conflicted or any(s == j and _INCENTIVE.search(t) for s, t in utterances):
            units.append(R(j))
    return sorted(units)
