"""Tier 1 OfficeMinds world.

Type boundaries (AGENTS.md §5.1, implementation-spec §2):

- ``WorldConfig``: public, static task structure (layout, roster, query facts,
  handoff availability, stakes, horizon). The robot may see it.
- ``World`` dynamic state: physical positions plus each person's private
  ``PersonMind``. Never serialized into agent inputs.
- ``Observation``: the only thing the robot receives after each step.
- The full event log (``World.log``) is privileged and is exported only into
  ``officeminds.episode.PrivilegedTrace``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

UNKNOWN = "unknown"
COOPERATIVE = "cooperative"
OBSTRUCTIVE = "obstructive"

STEP_PENALTY = 0.05
SUCCESS_REWARD = 1.0
ERROR_PENALTY = 0.5


@dataclass(frozen=True, order=True)
class Action:
    kind: str  # move | ask | drop | give | deliver | wait
    target: str = ""
    fact: str = ""

    def __str__(self) -> str:
        args = ",".join(x for x in (self.target, self.fact) if x)
        return f"{self.kind}({args})"


@dataclass(frozen=True)
class Event:
    """Something that happens in a room.

    kind:
      witness - everyone present learns ``fact = value``.
      tell    - sincere: ``actor`` believes and tells everyone present ``fact = value``;
                listeners adopt it and believe the actor believes it; the actor believes
                they now believe it.
      claim   - ``actor`` asserts ``fact = value`` (possibly a lie); listeners only update
                their belief about what the actor believes.
      say     - a visible utterance with no belief effect (e.g. a stated incentive).

    ``present`` overrides current positions for backstory events (t < 0), when people
    stood somewhere other than where the episode starts.
    """

    id: str
    t: int
    kind: str
    room: str
    actor: str = ""
    fact: str = ""
    value: str = ""
    text: str = ""
    present: tuple[str, ...] | None = None


@dataclass
class PersonMind:
    intent: str = COOPERATIVE
    beliefs: dict[str, str] = field(default_factory=dict)
    # (other, fact) -> value this person believes `other` believes.
    nested: dict[tuple[str, str], str] = field(default_factory=dict)
    perceived: list[str] = field(default_factory=list)

    def copy(self) -> PersonMind:
        return PersonMind(self.intent, dict(self.beliefs), dict(self.nested), list(self.perceived))

    def signature(self) -> tuple:
        return (self.intent, tuple(sorted(self.beliefs.items())), tuple(sorted(self.nested.items())))


@dataclass(frozen=True)
class Observation:
    t: int
    room: str
    people_present: tuple[str, ...]
    utterances: tuple[tuple[str, str], ...]  # (speaker, text)
    outcome: str = ""  # "" | success | error | timeout
    reward: float = 0.0
    done: bool = False

    def to_dict(self) -> dict:
        return {
            "t": self.t,
            "room": self.room,
            "people_present": list(self.people_present),
            "utterances": [list(u) for u in self.utterances],
            "outcome": self.outcome,
            "reward": round(self.reward, 10),
            "done": self.done,
        }


@dataclass(frozen=True)
class WorldConfig:
    adjacency: dict[str, tuple[str, ...]]
    offices: tuple[str, ...]
    chute_room: str | None  # rooms from which `drop(office)` is possible; None disables it
    recipient: str
    roster: tuple[str, ...]  # public names the robot may refer to
    query_facts: tuple[str, ...]  # public task-relevant fact names
    fact_domains: dict[str, tuple[str, ...]]
    # person -> (other, fact) that person routes a handed-over package by;
    # other == "" means their own belief about `fact`.
    handoff_routes: dict[str, tuple[str, str]]
    stakes: float = 1.0
    horizon: int = 8


class World:
    def __init__(
        self,
        config: WorldConfig,
        robot_room: str,
        people_rooms: dict[str, str],
        minds: dict[str, PersonMind],
        backstory: tuple[Event, ...] = (),
        timed_events: tuple[Event, ...] = (),
    ):
        self.config = config
        self.t = 0
        self.robot_room = robot_room
        self.holding = True
        self.done = False
        self.people_rooms = dict(people_rooms)
        self.minds = minds
        self.timed_events = timed_events
        self.log: list[Event] = []
        for ev in sorted(backstory, key=lambda e: e.t):
            assert ev.t < 0, "backstory events must precede the episode"
            self._apply(ev)

    # ------------------------------------------------------------------ dynamics
    def reset(self) -> Observation:
        """Apply t=0 events and return the robot's initial observation."""
        heard = self._run_timed_events(0)
        return self._observe(heard, reward=0.0, outcome="")

    def step(self, action: Action) -> Observation:
        if self.done:
            raise RuntimeError("episode already finished")
        self.t += 1
        reward = -STEP_PENALTY
        outcome = ""
        heard: list[tuple[str, str]] = []
        cfg = self.config

        if action.kind == "move":
            if action.target in cfg.adjacency[self.robot_room]:
                self.robot_room = action.target
        elif action.kind == "ask":
            p = action.target
            if self.people_rooms.get(p) == self.robot_room and action.fact in cfg.query_facts:
                value = self._answer(p, action.fact)
                text = "I don't know." if value == UNKNOWN else f"{action.fact} = {value}"
                ev = Event(f"t{self.t}-ask-{p}", self.t, "claim", self.robot_room, p, action.fact, value, text)
                self._apply(ev)
                heard.append((p, text))
        elif action.kind == "drop":
            if self.holding and self.robot_room == cfg.chute_room and action.target in cfg.offices:
                reward, outcome = self._resolve(action.target, reward)
        elif action.kind == "give":
            p = action.target
            if self.holding and p in cfg.handoff_routes and self.people_rooms.get(p) == self.robot_room:
                other, fact = cfg.handoff_routes[p]
                mind = self.minds[p]
                room = mind.beliefs.get(fact, UNKNOWN) if not other else mind.nested.get((other, fact), UNKNOWN)
                reward, outcome = self._resolve(room, reward)
        elif action.kind == "deliver":
            if self.holding and self.people_rooms.get(cfg.recipient) == self.robot_room:
                reward, outcome = self._resolve(self.robot_room, reward)
        elif action.kind != "wait":
            raise ValueError(f"unknown action {action}")

        heard.extend(self._run_timed_events(self.t))
        if not self.done and self.t >= cfg.horizon:
            self.done = True
            outcome = "timeout"
        return self._observe(heard, reward, outcome)

    def _resolve(self, room: str, reward: float) -> tuple[float, str]:
        self.holding = False
        self.done = True
        if self.people_rooms[self.config.recipient] == room:
            return reward + SUCCESS_REWARD, "success"
        return reward - ERROR_PENALTY * self.config.stakes, "error"

    def _answer(self, person: str, fact: str) -> str:
        mind = self.minds[person]
        belief = mind.beliefs.get(fact, UNKNOWN)
        if mind.intent == OBSTRUCTIVE and belief != UNKNOWN:
            # Deterministic lie: the first other value in the fact's domain.
            return next(v for v in self.config.fact_domains[fact] if v != belief)
        return belief

    def _run_timed_events(self, t: int) -> list[tuple[str, str]]:
        heard = []
        for ev in self.timed_events:
            if ev.t == t:
                self._apply(ev)
                if ev.room == self.robot_room and ev.text:
                    heard.append((ev.actor, ev.text))
        return heard

    def _apply(self, ev: Event) -> None:
        self.log.append(ev)
        present = ev.present if ev.present is not None else tuple(
            p for p, r in self.people_rooms.items() if r == ev.room
        )
        for p in present:
            self.minds[p].perceived.append(ev.id)
        listeners = [p for p in present if p != ev.actor]
        if ev.kind == "witness":
            for p in present:
                self.minds[p].beliefs[ev.fact] = ev.value
        elif ev.kind == "tell":
            self.minds[ev.actor].beliefs[ev.fact] = ev.value  # a tell is sincere
            for p in listeners:
                self.minds[p].beliefs[ev.fact] = ev.value
                self.minds[p].nested[(ev.actor, ev.fact)] = ev.value
                self.minds[ev.actor].nested[(p, ev.fact)] = ev.value
        elif ev.kind == "claim":
            for p in listeners:
                self.minds[p].nested[(ev.actor, ev.fact)] = ev.value
        elif ev.kind != "say":
            raise ValueError(f"unknown event kind {ev.kind}")

    def _observe(self, heard: list[tuple[str, str]], reward: float, outcome: str) -> Observation:
        present = tuple(sorted(p for p, r in self.people_rooms.items() if r == self.robot_room))
        return Observation(self.t, self.robot_room, present, tuple(heard), outcome, reward, self.done)

    # ------------------------------------------------------------------ utilities
    def clone(self) -> World:
        w = object.__new__(World)
        w.config = self.config
        w.t = self.t
        w.robot_room = self.robot_room
        w.holding = self.holding
        w.done = self.done
        w.people_rooms = dict(self.people_rooms)
        w.minds = {p: m.copy() for p, m in self.minds.items()}
        w.timed_events = self.timed_events
        w.log = list(self.log)
        return w

    def signature(self) -> tuple:
        """Everything that can influence the future (the log cannot)."""
        return (
            self.t,
            self.robot_room,
            self.holding,
            self.done,
            tuple(sorted(self.people_rooms.items())),
            tuple((p, m.signature()) for p, m in sorted(self.minds.items())),
        )


def legal_actions(config: WorldConfig, obs: Observation, holding: bool = True) -> list[Action]:
    """Actions available to the robot, computed from public config and its own observation only."""
    if obs.done:
        return []
    acts = [Action("move", r) for r in config.adjacency[obs.room]]
    if holding and config.chute_room == obs.room:
        acts += [Action("drop", o) for o in config.offices]
    for p in obs.people_present:
        acts += [Action("ask", p, f) for f in config.query_facts]
        if holding and p in config.handoff_routes:
            acts.append(Action("give", p))
    if holding and config.recipient in obs.people_present:
        acts.append(Action("deliver"))
    acts.append(Action("wait"))
    return sorted(set(acts))
