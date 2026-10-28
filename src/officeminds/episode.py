"""Episode execution, the agent/privileged split, and deterministic replay."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field

from .scenarios import Params, Scenario
from .world import Action, Observation, World


@dataclass
class VisibleHistory:
    """Robot-visible action-observation history h_t (actions included, AGENTS.md §5.1)."""

    brief: str
    steps: list[tuple[Action | None, Observation]] = field(default_factory=list)

    @property
    def actions(self) -> list[Action]:
        return [a for a, _ in self.steps if a is not None]

    @property
    def last(self) -> Observation:
        return self.steps[-1][1]

    def to_agent_dict(self) -> dict:
        """The ONLY serialization allowed into policy, controller, or prompt inputs."""
        return {
            "brief": self.brief,
            "steps": [{"action": str(a) if a else None, "obs": o.to_dict()} for a, o in self.steps],
        }


@dataclass
class PrivilegedTrace:
    """Oracle/evaluator annotations. Stored separately; never passed to agents."""

    scenario_id: str
    params: Params
    event_log: list[dict]
    minds_by_step: list[dict]

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "params": [list(x) for x in self.params],
            "event_log": self.event_log,
            "minds_by_step": self.minds_by_step,
        }


def sample_params(scenario: Scenario, seed: int) -> Params:
    rng = random.Random(seed)
    params, weights = zip(*scenario.prior)
    return rng.choices(params, weights=weights, k=1)[0]


def _minds_snapshot(world: World) -> dict:
    return {
        p: {
            "room": world.people_rooms.get(p, "offstage"),  # backstory-only people
            "intent": m.intent,
            "beliefs": dict(sorted(m.beliefs.items())),
            "nested": {f"{o}:{f}": v for (o, f), v in sorted(m.nested.items())},
            "perceived": list(m.perceived),
        }
        for p, m in sorted(world.minds.items())
    }


def run_episode(scenario: Scenario, params: Params, policy) -> tuple[VisibleHistory, PrivilegedTrace, World]:
    """Run ``policy(history) -> Action`` until done. The policy sees only the VisibleHistory."""
    world = scenario.build(params)
    hist = VisibleHistory(scenario.brief, [(None, world.reset())])
    minds = [_minds_snapshot(world)]
    while not hist.last.done:
        action = policy(hist)
        hist.steps.append((action, world.step(action)))
        minds.append(_minds_snapshot(world))
    log = [ev.__dict__ | {"present": list(ev.present) if ev.present else None} for ev in world.log]
    return hist, PrivilegedTrace(scenario.id, params, log, minds), world


def fixed_policy(actions: list[Action]):
    it = iter(actions)
    return lambda hist: next(it)


def episode_record(hist: VisibleHistory, trace: PrivilegedTrace) -> dict:
    agent = hist.to_agent_dict()
    priv = trace.to_dict()
    return {
        "agent_view": agent,
        "privileged": priv,
        "agent_view_sha256": hashlib.sha256(json.dumps(agent, sort_keys=True).encode()).hexdigest(),
        "return": round(sum(o.reward for _, o in hist.steps), 10),
    }


def replay(record: dict, scenarios: dict) -> dict:
    """Rebuild the world from scenario id + hidden params and re-execute the recorded actions."""
    priv = record["privileged"]
    scenario = scenarios[priv["scenario_id"]]()
    params = tuple(tuple(x) for x in priv["params"])
    actions = [_parse_action(s["action"]) for s in record["agent_view"]["steps"][1:]]
    hist, trace, _ = run_episode(scenario, params, fixed_policy(actions))
    return episode_record(hist, trace)


def _parse_action(text: str) -> Action:
    kind, _, rest = text.partition("(")
    args = [a for a in rest.rstrip(")").split(",") if a]
    return Action(kind, *args)
