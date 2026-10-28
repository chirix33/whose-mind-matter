"""Robot-side perspective graph G_t and controller-visible features (implementation-spec §5.3).

Everything here is computed from the robot-visible history plus the robot's own unit outputs.
Nothing reads hidden worlds.

Retention and update rule (D-002 fixed continuation):
- an instantiated unit stays in the graph; it is never silently erased or re-inferred;
- when new visible evidence touches the unit's people, the record is marked ``stale`` with
  the new evidence IDs; the symbolic actor updates its belief by exact conditioning at zero
  incremental instantiation cost, so a refresh is not a new instantiation;
- a person's earlier location claim refuted by the robot's own later observation (it stood in
  the claimed room and the recipient was absent) marks that person's unit ``contradicted``.

Refresh / abstain rule (D-007): an output is valid as of its timestamp only. Status is always
visible to the policy (`policy_view`). A ``contradicted`` unit must be refreshed (a counted
re-inference call, recorded in `history`) or marked ``abstain`` before the policy may use it;
a ``stale`` unit may be used but is shown as stale.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from officeminds.episode import VisibleHistory
from officeminds.world import WorldConfig

from .units import Unit


@dataclass
class UnitRecord:
    unit: str
    path: tuple[str, ...]
    variable: str
    # Either the scalar diagnostic {"p_default_holds", "p_default_violated"} or a typed hypothesis
    # list [{"content": [...], "default_holds": bool, "p": float}, ...].
    output: dict | list
    confidence: float  # probability of the modal hypothesis
    evidence: list[str]  # visible evidence IDs ("t<step>:<kind>:<who>")
    timestamp: int  # the output is valid as of this step only
    cost_calls: float  # instantiation + refreshes
    status: str = "fresh"  # fresh | retained | stale | contradicted | refreshed | abstain
    history: list = field(default_factory=list)  # earlier (timestamp, output, status) before refreshes


def _confidence(output) -> float:
    if isinstance(output, list):  # typed symbolic reference hypotheses
        return max(h["p"] for h in output)
    if "hypotheses" in output:  # typed LLM unit output (vomi.unit_schema)
        return max(float(h["p"]) for h in output["hypotheses"])
    return max(output.values())  # scalar diagnostic fields


@dataclass
class PerspectiveGraph:
    units: dict[str, UnitRecord] = field(default_factory=dict)
    recipient: str = "alice"  # public task recipient (WorldConfig.recipient)

    def instantiate(self, u: Unit, output, evidence: list[str], t: int, cost: float = 1.0) -> UnitRecord:
        if str(u) in self.units:
            raise ValueError(f"{u} already instantiated; retained units are not re-inferred")
        rec = UnitRecord(str(u), u.path, u.variable, output, _confidence(output), evidence, t, cost)
        self.units[str(u)] = rec
        return rec

    def refresh(self, u: Unit, output, evidence: list[str], t: int, cost: float = 1.0) -> UnitRecord:
        """Counted re-inference of a retained unit from the current visible history."""
        rec = self.units[str(u)]
        rec.history.append({"timestamp": rec.timestamp, "output": rec.output, "status": rec.status})
        rec.output, rec.confidence, rec.timestamp = output, _confidence(output), t
        rec.evidence = sorted(set(rec.evidence) | set(evidence))
        rec.cost_calls += cost
        rec.status = "refreshed"
        return rec

    def abstain(self, u: Unit) -> None:
        self.units[str(u)].status = "abstain"

    def policy_view(self) -> list[dict]:
        """What the decision policy sees: outputs WITH their status and timestamp."""
        return [{"unit": r.unit, "output": r.output, "status": r.status, "as_of": r.timestamp}
                for r in self.units.values() if r.status != "abstain"]

    def advance(self, hist: VisibleHistory) -> None:
        """Retain every unit; mark stale/contradicted from new visible evidence only."""
        for rec in self.units.values():
            if rec.status == "abstain":
                continue
            new = [e for e in visible_evidence(hist, rec.path) if int(e.split(":")[0][1:]) > rec.timestamp]
            refuted = [c for c in contradicted_claims(hist, rec.path[-1], self.recipient)
                       if c.observed_after > rec.timestamp]
            if refuted:
                rec.status = "contradicted"
            elif new:
                rec.status = "stale"
            else:
                rec.status = "retained"
                continue
            rec.evidence = sorted(set(rec.evidence) | set(new))

    def total_cost(self) -> float:
        return sum(r.cost_calls for r in self.units.values())


def _mentions(text: str, name: str) -> bool:
    return re.search(rf"\b{re.escape(name)}\b", text, re.I) is not None


@dataclass(frozen=True)
class Refutation:
    claim_t: int
    claim: str
    observed_after: int  # step at which the robot's own observation refuted it


def contradicted_claims(hist: VisibleHistory, person: str, recipient: str = "alice") -> list[Refutation]:
    """Visible contradictions of `person`'s location claims: the robot later stood in the claimed
    room and did not see the recipient there. Uses robot observations only."""
    out = []
    for _, o in hist.steps:
        for speaker, text in o.utterances:
            if speaker == person and text.startswith(f"{recipient}_loc = "):
                room = text.split(" = ", 1)[1]
                seen = [o2.t for _, o2 in hist.steps if o2.t > o.t and o2.room == room and recipient not in o2.people_present]
                if seen:
                    out.append(Refutation(o.t, text, min(seen)))
    return out


def visible_evidence(hist: VisibleHistory, path: tuple[str, ...]) -> list[str]:
    ev = []
    for _, o in hist.steps:
        for p in path:
            if p in o.people_present:
                ev.append(f"t{o.t}:seen:{p}")
        for i, (speaker, text) in enumerate(o.utterances):
            if speaker in path:
                ev.append(f"t{o.t}:said{i}:{speaker}")
            elif any(_mentions(text, p) for p in path):
                ev.append(f"t{o.t}:mentioned{i}:{speaker}")
    if any(_mentions(hist.brief, p) for p in path):
        ev.append("t0:brief")
    return sorted(set(ev))


def visible_features(config: WorldConfig, hist: VisibleHistory, u: Unit, margin: float) -> dict:
    """Outline §4.2 structural features. ``margin`` must come from the actor's own scores."""
    obs = [o for _, o in hist.steps]
    t = hist.last.t
    last_seen = [o.t for o in obs for p in u.path if p in o.people_present]
    spoke = any(s in u.path for o in obs for s, _ in o.utterances)
    claims: dict[str, set] = {}
    for o in obs:
        for _, text in o.utterances:
            if " = " in text:
                f, v = text.split(" = ", 1)
                claims.setdefault(f, set()).add(v)
    return {
        "depth": u.depth,
        "variable": u.variable,
        "steps_since_seen": (t - max(last_seen)) if last_seen else None,
        "spoke_to_robot": spoke,
        "n_conflicting_facts": sum(len(v) > 1 for v in claims.values()),
        "stated_incentive": any(s == u.path[-1] and re.search(r"\b(i'd rather|i want)\b", txt, re.I)
                                for o in obs for s, txt in o.utterances),
        "stakes": config.stakes,
        "decision_margin": round(margin, 10),
        "n_evidence": len(visible_evidence(hist, u.path)),
    }
