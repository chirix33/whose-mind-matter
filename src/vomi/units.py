"""Modeling units u = (path, variable), their true content, and visible-only candidate generation.

Content semantics (implementation-spec §3):
- K(j):     j's belief about each public query fact (``unknown`` if j holds none).
            This is j's epistemic state, not the objective truth: it can be false.
- R(j):     j's stable intent type (cooperative | obstructive). Statement correctness
            is derived from belief vs. truth and is not a unit variable.
- K(j->k):  j's belief about k's belief about each query fact.
            Neither k's actual state nor the robot's belief about k.
- R(j->k):  j's assessment of k's intent (cooperative | obstructive | unknown). Not k's
            actual intent, and not j's own reliability while talking about k.

Face-value defaults (implementation-spec §4.2): an UNMODELED factor is assumed to satisfy
``default_holds``: no false (nested) beliefs about query facts, everyone cooperative, and
accurate assessments. A modeled unit removes exactly its own default.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from officeminds.episode import VisibleHistory
from officeminds.world import COOPERATIVE, UNKNOWN, World, WorldConfig

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
    return (mind.assessments.get(k, UNKNOWN),)


def all_factors(world: World) -> list[Unit]:
    """Every mental factor of every person in this world (depth <= 2)."""
    people = sorted(world.minds)
    out = [u for j in people for u in (K(j), R(j))]
    out += [u for j in people for k in people if j != k for u in (K(j, k), R(j, k))]
    return out


def default_holds(world: World, unit: Unit) -> bool:
    """Whether ``unit``'s content satisfies the face-value default in ``world``."""
    j = unit.path[0]
    mind = world.minds.get(j)
    if mind is None:
        return True
    facts = world.config.query_facts
    if unit.depth == 1:
        if unit.variable == KNOWLEDGE:
            return all(mind.beliefs.get(f, UNKNOWN) in (UNKNOWN, world.truth(f)) for f in facts)
        return mind.intent == COOPERATIVE
    other = world.minds.get(unit.path[1])
    if other is None:
        return True
    if unit.variable == KNOWLEDGE:
        return all(mind.nested.get((unit.path[1], f), UNKNOWN) in (UNKNOWN, other.beliefs.get(f, UNKNOWN))
                   for f in facts)
    return mind.assessments.get(unit.path[1], UNKNOWN) in (UNKNOWN, other.intent)


def _mentions(text: str, name: str) -> bool:
    return re.search(rf"\b{re.escape(name)}\b", text, re.I) is not None


def generate_candidates(config: WorldConfig, hist: VisibleHistory) -> list[Unit]:
    """Structural preconditions (outline §4.1) evaluated on robot-visible information only."""
    observations = [o for _, o in hist.steps]
    utterances = [u for o in observations for u in o.utterances]
    notices = [n for o in observations for n in o.notices]  # dev-v3 visible prologue events
    # statements/remarks in notices count as utterances: (speaker, the quoted text)
    utterances += [(a, line.split('says: "', 1)[1][:-1]) for k, a, line, _ in notices if k in ("statement", "remark")]
    texts = [hist.brief] + [t for _, t in utterances] + [line for _, _, line, _ in notices]

    observed = ({p for o in observations for p in o.people_present} | {s for s, _ in utterances}
                | {a for _, a, _, _ in notices} | {p for *_, ps in notices for p in ps})
    mentioned = {p for p in config.roster if any(_mentions(t, p) for t in texts)}
    known = sorted((observed | mentioned) & set(config.roster))

    units = [K(j) for j in known]
    for j in known:
        for k in known:
            if j == k:
                continue
            talked = any(s in (j, k) and _mentions(t, k if s == j else j) for s, t in utterances)
            together = any(j in o.people_present and k in o.people_present for o in observations) or any(
                {j, k} <= {a, *ps} for _, a, _, ps in notices)
            if talked or together:
                units.append(K(j, k))

    claims: dict[str, set[str]] = {}
    claimants: dict[str, set[str]] = {}
    for s, t in utterances:
        if m := _CLAIM.match(t):
            claims.setdefault(m[1], set()).add(m[2])
            claimants.setdefault(m[1], set()).add(s)
    conflicted = {s for f, vals in claims.items() if len(vals) > 1 for s in claimants[f]}
    doubtful = {j for j in known if j in conflicted or any(s == j and _INCENTIVE.search(t) for s, t in utterances)}
    units += [R(j) for j in doubtful]
    # R(j->k): visible j-k contact (as for K(j->k)) AND visible evidence about k's reliability.
    units += [R(u.path[0], u.path[1]) for u in list(units) if u.depth == 2 and u.variable == KNOWLEDGE
              and u.path[1] in doubtful]
    return sorted(units)
