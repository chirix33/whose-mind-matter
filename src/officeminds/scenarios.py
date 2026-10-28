"""Tiny hand-checkable Tier 1 scenarios (Stage 1 smallest examples).

Each scenario is a public task (brief + config) plus a finite prior over hidden
parameters. ``build(params)`` returns the full world for one hidden assignment.
The robot never sees ``params``; oracles condition on the visible history by
replaying it in every hypothesis world (see ``vomi.oracle``).

Shared layout: lobby -- hall -- {office_a, office_b}. The robot starts in the
lobby holding Alice's package. Office doors are closed from the hall's point of
view: the robot only sees who is in a room by entering it.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable

from .world import COOPERATIVE, OBSTRUCTIVE, Event, PersonMind, World, WorldConfig

A, B = "office_a", "office_b"
OFFICES = (A, B)
LAYOUT = {"lobby": ("hall",), "hall": ("lobby", A, B), A: ("hall",), B: ("hall",)}

Params = tuple[tuple[str, str], ...]


def other(room: str) -> str:
    return B if room == A else A


@dataclass(frozen=True)
class Scenario:
    id: str
    brief: str  # public task text (robot-visible)
    purpose: str  # documentation of what the case tests (privileged; never shown to agents)
    prior: tuple[tuple[Params, float], ...]
    builder: Callable[[dict[str, str]], World]

    def build(self, params: Params | dict[str, str]) -> World:
        return self.builder(dict(params))

    @property
    def config(self) -> WorldConfig:
        return self.build(self.prior[0][0]).config


def grid(domains: dict[str, dict[str, float]], keep: Callable[[dict], bool] = lambda p: True):
    """Independent product prior over named hidden variables, optionally filtered, normalized."""
    names = sorted(domains)
    rows = []
    for combo in itertools.product(*(domains[n].items() for n in names)):
        params = {n: v for n, (v, _) in zip(names, combo)}
        weight = 1.0
        for _, w in combo:
            weight *= w
        if weight > 0 and keep(params):
            rows.append((tuple(sorted(params.items())), weight))
    total = sum(w for _, w in rows)
    return tuple((p, w / total) for p, w in rows)


HALF = {"yes": 0.5, "no": 0.5}
ROOM_HALF = {A: 0.5, B: 0.5}


def _config(roster, query_facts, chute=True, handoff=None, stakes=1.0, horizon=8, domains=None):
    return WorldConfig(
        adjacency=LAYOUT,
        offices=OFFICES,
        chute_room="lobby" if chute else None,
        recipient="alice",
        roster=tuple(roster),
        query_facts=tuple(query_facts),
        fact_domains=domains or {f: OFFICES for f in query_facts},
        handoff_routes=handoff or {},
        stakes=stakes,
        horizon=horizon,
    )


def _saw_alice(loc: str, witnesses: tuple[str, ...]) -> Event:
    """Backstory: Alice walks to her office through the hall; `witnesses` were there."""
    return Event("bs-alice-walks", -2, "witness", "hall", "alice", "alice_loc", loc, present=("alice",) + witnesses)


# --------------------------------------------------------------------- depth 0
def depth0_visible() -> Scenario:
    def build(p):
        cfg = _config(["alice", "rec"], ["alice_loc"], domains={"alice_loc": ("lobby",) + OFFICES})
        rooms = {"alice": "lobby", "rec": "lobby"}
        minds = {"alice": PersonMind(), "rec": PersonMind()}
        seen = ("rec",) if p["rec_saw"] == "yes" else ()
        bs = (Event("bs-alice-arrives", -1, "witness", "lobby", "alice", "alice_loc", "lobby", present=("alice",) + seen),)
        return World(cfg, "lobby", rooms, minds, bs)

    return Scenario(
        "depth0_visible",
        "Deliver the package to Alice.",
        "Alice is visible in the lobby: physical reasoning suffices; mental units have varying content but cannot flip the action.",
        grid({"rec_saw": HALF}),
        build,
    )


# --------------------------------------------------------------------- depth 1
def _lobby_witness_world(p, people: tuple[str, ...], timed=()) -> World:
    cfg = _config(("alice",) + people, ["alice_loc"])
    rooms = {"alice": p["alice_loc"], **{x: "lobby" for x in people}}
    minds = {"alice": PersonMind(), **{x: PersonMind() for x in people}}
    witnesses = tuple(x for x in people if p.get(f"{x}_saw") == "yes")
    return World(cfg, "lobby", rooms, minds, (_saw_alice(p["alice_loc"], witnesses),), timed)


def depth1_knowledge() -> Scenario:
    return Scenario(
        "depth1_knowledge",
        "Deliver the package to Alice.",
        "The receptionist may have seen where Alice went. K(rec) saves the ask step (exact value 0.05).",
        grid({"alice_loc": ROOM_HALF, "rec_saw": HALF}),
        lambda p: _lobby_witness_world(p, ("rec",)),
    )


def distractor_plausible() -> Scenario:
    return Scenario(
        "distractor_plausible",
        "Deliver the package to Alice.",
        "Carol is a plausible distractor: same position as rec and may also have seen Alice. Holder is symmetric.",
        grid({"alice_loc": ROOM_HALF, "rec_saw": HALF, "carol_saw": HALF}),
        lambda p: _lobby_witness_world(p, ("rec", "carol")),
    )


def distractor_obvious() -> Scenario:
    arrived = Event("t0-carol-arrived", 0, "say", "lobby", "carol", text="I just got here.")
    return Scenario(
        "distractor_obvious",
        "Deliver the package to Alice.",
        "Carol visibly just arrived, so her knowledge content is constant across consistent worlds: P1 prunes K(carol).",
        grid({"alice_loc": ROOM_HALF, "rec_saw": HALF, "carol_saw": {"no": 1.0}}),
        lambda p: _lobby_witness_world(p, ("rec", "carol"), (arrived,)),
    )


def substitutes() -> Scenario:
    def build(p):
        cfg = _config(["alice", "bob"], ["alice_loc"])
        rooms = {"alice": p["alice_loc"], "bob": "lobby"}
        minds = {"alice": PersonMind(), "bob": PersonMind()}
        bs = (
            Event("bs-alice-self", -3, "witness", p["alice_loc"], "alice", "alice_loc", p["alice_loc"], present=("alice",)),
            Event("bs-alice-tells-bob", -2, "tell", "hall", "alice", "alice_loc", p["alice_loc"], present=("alice", "bob")),
        )
        talk = Event("t0-bob-talked", 0, "say", "lobby", "bob", text="I talked with Alice earlier.")
        return World(cfg, "lobby", rooms, minds, bs, (talk,))

    return Scenario(
        "substitutes",
        "Deliver the package to Alice.",
        "Alice told Bob her location: K(alice), K(bob), K(bob->alice), K(alice->bob) each suffice alone (P3b).",
        grid({"alice_loc": ROOM_HALF}),
        build,
    )


# --------------------------------------------------------------------- depth 2
def depth2_handoff() -> Scenario:
    """Complementary pair: handing the package to rec works iff rec's belief about Alice's
    meeting room matches Alice's actual belief (which is where Alice is)."""

    def build(p):
        cfg = _config(["alice", "rec"], ["meeting_room"], chute=False, handoff={"rec": ("alice", "meeting_room")})
        initial = p["initial"]
        moved = other(initial)
        alice_room = moved if p["alice_heard_move"] == "yes" else initial
        rooms = {"alice": alice_room, "rec": "lobby"}
        minds = {"alice": PersonMind(), "rec": PersonMind()}
        bs = [Event("bs-alice-tells-rec", -4, "tell", "lobby", "alice", "meeting_room", initial, present=("alice", "rec"))]
        heard = tuple(x for x in ("alice", "rec") if p[f"{x}_heard_move"] == "yes")
        if heard:
            bs.append(Event("bs-move-announced", -2, "tell", "hall", "dave", "meeting_room", moved, present=("dave",) + heard))
            minds["dave"] = PersonMind()
        talk = Event("t0-rec-mentions", 0, "say", "lobby", "rec", text="Alice told me this morning where her meeting is.")
        return World(cfg, "lobby", rooms, minds, tuple(bs), (talk,))

    return Scenario(
        "depth2_handoff",
        "Deliver the package to Alice. The receptionist can forward packages.",
        "K(alice) and K(rec->alice) are complementary for the handoff; neither alone flips the first action (P3a).",
        grid({"initial": ROOM_HALF, "alice_heard_move": HALF, "rec_heard_move": HALF}),
        build,
    )


# --------------------------------------------------------------------- stakes
def reliability_stakes(stakes: float, q_coop: float) -> Scenario:
    """Bob states an incentive and claims Alice is in office_a. Only his intent is uncertain."""

    def build(p):
        cfg = _config(["alice", "bob"], ["alice_loc"], stakes=stakes)
        rooms = {"alice": p["alice_loc"], "bob": "lobby"}
        minds = {"alice": PersonMind(), "bob": PersonMind(intent=p["bob_intent"])}
        bs = (_saw_alice(p["alice_loc"], ("bob",)),)
        claimed = p["alice_loc"] if p["bob_intent"] == COOPERATIVE else other(p["alice_loc"])
        timed = (
            Event("t0-bob-incentive", 0, "say", "lobby", "bob", text="I'd rather keep that package myself."),
            Event("t0-bob-claim", 0, "claim", "lobby", "bob", "alice_loc", claimed, f"alice_loc = {claimed}"),
        )
        return World(cfg, "lobby", rooms, minds, bs, timed)

    return Scenario(
        f"stakes_m{stakes:g}_q{q_coop:g}",
        "Deliver the package to Alice.",
        "Stakes pair: identical observations, penalty x1 vs x4. Tests P5 numerically.",
        grid({"alice_loc": ROOM_HALF, "bob_intent": {COOPERATIVE: q_coop, OBSTRUCTIVE: 1 - q_coop}}),
        build,
    )


TINY_CASES: dict[str, Callable[[], Scenario]] = {
    "depth0_visible": depth0_visible,
    "depth1_knowledge": depth1_knowledge,
    "distractor_plausible": distractor_plausible,
    "distractor_obvious": distractor_obvious,
    "substitutes": substitutes,
    "depth2_handoff": depth2_handoff,
    "stakes_m1_q0.975": lambda: reliability_stakes(1.0, 0.975),
    "stakes_m4_q0.975": lambda: reliability_stakes(4.0, 0.975),
    "stakes_m1_q0.95": lambda: reliability_stakes(1.0, 0.95),
    "stakes_m4_q0.95": lambda: reliability_stakes(4.0, 0.95),
}
