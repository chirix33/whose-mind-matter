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
        return World(cfg, "lobby", rooms, minds, tuple(bs), (talk,), facts={"meeting_room": moved})

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


# ===================================================================== Stage 1 (grounded record)
# Generators below are built so the face-value defaults are POSSIBLE but not ENTAILED:
# every default violation that matters has a world where it does not occur, otherwise the
# bounded actor's hypothesis space (the generator support) would leak structure.

def _moved_world(p, people: tuple[str, ...], holder: str, timed=(), alice_returns=False) -> World:
    """Alice first walked to `initial` (seen by `holder`); with p['moved'] she later switched
    offices unseen. The holder's belief is then outdated (mistaken = cooperative + false belief)."""
    cfg = _config(("alice",) + people, ["alice_loc"])
    initial = p["initial"]
    final = other(initial) if p["moved"] == "yes" else initial
    rooms = {"alice": final, **{x: "lobby" for x in people}}
    minds = {"alice": PersonMind(), **{x: PersonMind() for x in people}}
    bs = [Event("bs-alice-walks", -3, "witness", "hall", "alice", "alice_loc", initial, present=("alice", holder))]
    if p["moved"] == "yes":
        bs.append(Event("bs-alice-switches", -1, "witness", final, "alice", "alice_loc", final, present=("alice",)))
    timed = tuple(timed)
    if alice_returns:
        timed += (Event("t1-alice-returns", 1, "enter", "lobby", "alice"),)
    return World(cfg, "lobby", rooms, minds, tuple(bs), timed)


def false_belief(p_moved: float = 0.3) -> Scenario:
    seen = Event("t0-rec-saw", 0, "say", "lobby", "rec", text="I saw Alice head to her office earlier.")
    return Scenario(
        "false_belief",
        "Deliver the package to Alice.",
        "Rec saw Alice's first office; Alice may have switched unseen (outdated belief). Face value trusts rec; "
        "K(rec) supplies the possibility of a false belief.",
        grid({"initial": ROOM_HALF, "moved": {"yes": p_moved, "no": 1 - p_moved}}),
        lambda p: _moved_world(p, ("rec",), "rec", (seen,)),
    )


def holder_permutation(holder: str) -> Scenario:
    """Same scene; only WHO visibly holds the (possibly outdated) observation differs."""
    seen = Event("t0-holder-saw", 0, "say", "lobby", holder, text="I saw Alice head to her office earlier.")
    return Scenario(
        f"holder_{holder}",
        "Deliver the package to Alice.",
        "Information-holder permutation: rec and carol swap roles with layout and wording fixed.",
        grid({"initial": ROOM_HALF, "moved": {"yes": 0.3, "no": 0.7}}),
        lambda p: _moved_world(p, ("carol", "rec"), holder, (seen,)),
    )


def relevance_shift() -> Scenario:
    seen = Event("t0-rec-saw", 0, "say", "lobby", "rec", text="I saw Alice head to her office earlier.")
    return Scenario(
        "relevance_shift",
        "Deliver the package to Alice.",
        "F3: Alice may walk into the lobby at t=1; once she is visible, K(rec) stops mattering.",
        grid({"initial": ROOM_HALF, "moved": {"yes": 0.3, "no": 0.7}, "returns": HALF}),
        lambda p: _moved_world(p, ("rec",), "rec", (seen,), alice_returns=p["returns"] == "yes"),
    )


def nested_reliability(p_naive: float = 0.5, q_coop: float = 0.5) -> Scenario:
    """R(rec->bob): rec forwards packages by her own belief, which she got from Bob. If Bob is
    obstructive he lied to her; a warned rec sees through it, a naive rec does not."""

    def build(p):
        cfg = _config(["alice", "bob", "rec"], ["alice_loc"], chute=False, handoff={"rec": ("", "alice_loc")})
        loc, obstructive = p["alice_loc"], p["bob_intent"] == OBSTRUCTIVE
        rooms = {"alice": loc, "bob": "lobby", "rec": "lobby"}
        minds = {"alice": PersonMind(), "bob": PersonMind(intent=p["bob_intent"]), "rec": PersonMind(), "dave": PersonMind()}
        if p["rec_naive"] == "yes":
            vouch = Event("bs-bob-vouches", -3, "assess", "lobby", "bob", "bob", COOPERATIVE, present=("bob", "rec"))
        else:
            vouch = Event("bs-dave-warns", -3, "assess", "hall", "dave", "bob", p["bob_intent"], present=("dave", "rec"))
        claimed = other(loc) if obstructive else loc
        bs = (
            Event("bs-bob-sees", -4, "witness", "hall", "bob", "alice_loc", loc, present=("alice", "bob")),
            vouch,
            Event("bs-bob-tells-rec", -2, "assert", "lobby", "bob", "alice_loc", claimed, present=("bob", "rec")),
        )
        incentive = Event("t0-bob-incentive", 0, "say", "lobby", "bob", text="I'd rather keep that package myself.")
        return World(cfg, "lobby", rooms, minds, bs, (incentive,))

    return Scenario(
        "nested_reliability",
        "Deliver the package to Alice. The receptionist can forward packages.",
        "Nested R: forwarding fails iff Bob lied and rec misjudges Bob (naive). R(rec->bob) or K(rec) exposes it.",
        grid({"alice_loc": ROOM_HALF, "bob_intent": {COOPERATIVE: q_coop, OBSTRUCTIVE: 1 - q_coop},
              "rec_naive": {"yes": p_naive, "no": 1 - p_naive}}),
        build,
    )


def path_asymmetry() -> Scenario:
    """F6: forwarding works iff rec's belief about Alice's meeting room matches Alice's. Alice may
    have heard that the meeting moved, and may or may not have told rec. Directed (rec->alice)
    matters; the reverse direction (alice->rec) and rec's own knowledge do not."""

    def build(p):
        cfg = _config(["alice", "rec"], ["meeting_room"], chute=False, handoff={"rec": ("alice", "meeting_room")})
        initial = p["initial"]
        moved = other(initial)
        heard, told = p["story"] != "not_heard", p["story"] == "heard_told_rec"
        rooms = {"alice": moved if heard else initial, "rec": "lobby"}
        minds = {"alice": PersonMind(), "rec": PersonMind(), "dave": PersonMind()}
        bs = [Event("bs-alice-tells-rec", -4, "tell", "lobby", "alice", "meeting_room", initial, present=("alice", "rec"))]
        # Rec's OWN knowledge of the move comes from an independent channel (decoupled from routing).
        hearers = (("alice",) if heard else ()) + (("rec",) if p["rec_heard"] == "yes" else ())
        if hearers:
            bs.append(Event("bs-move-announced", -3, "tell", "hall", "dave", "meeting_room", moved, present=("dave",) + hearers))
        if told:  # Alice tells rec where SHE is going: updates rec's model of Alice, not rec's own belief
            bs.append(Event("bs-alice-updates-rec", -2, "claim", "lobby", "alice", "meeting_room", moved,
                            present=("alice", "rec")))
        talk = Event("t0-rec-mentions", 0, "say", "lobby", "rec", text="Alice told me this morning where her meeting is.")
        return World(cfg, "lobby", rooms, minds, tuple(bs), (talk,), facts={"meeting_room": moved})

    return Scenario(
        "path_asymmetry",
        "Deliver the package to Alice. The receptionist can forward packages.",
        "F6 directed path: K(rec->alice) carries the decision; K(alice->rec), K(rec) do not.",
        grid({"initial": ROOM_HALF, "story": {"not_heard": 0.5, "heard_told_rec": 0.25, "heard_not_told": 0.25},
              "rec_heard": HALF}),
        build,
    )


REPORTER_TYPES = ("accurate", "mistaken", "obstructive")  # mistaken = cooperative + false belief


def conflicting_reports(bob: dict[str, float], carol: dict[str, float], stakes: float = 1.0,
                        p_office_a: float = 0.5) -> Scenario:
    """Stakes family for D-006: Bob and Carol each report Alice's office at t=0. Each reporter is
    accurate, mistaken (believes the wrong office, says it sincerely) or obstructive (knows, lies)."""

    def build(p):
        cfg = _config(["alice", "bob", "carol"], ["alice_loc"], stakes=stakes)
        loc = p["alice_loc"]
        rooms = {"alice": loc, "bob": "lobby", "carol": "lobby"}
        minds, bs, timed = {"alice": PersonMind()}, [], []
        for i, who in enumerate(("bob", "carol")):
            kind = p[f"{who}_type"]
            minds[who] = PersonMind(intent=OBSTRUCTIVE if kind == "obstructive" else COOPERATIVE)
            believed = other(loc) if kind == "mistaken" else loc
            bs.append(Event(f"bs-{who}-sees", -2 - i, "witness", "hall", who, "alice_loc", believed, present=(who,)))
            said = other(believed) if kind == "obstructive" else believed
            timed.append(Event(f"t0-{who}-claims", 0, "claim", "lobby", who, "alice_loc", said, f"alice_loc = {said}"))
        bs.append(Event("bs-alice-self", -4, "witness", loc, "alice", "alice_loc", loc, present=("alice",)))
        return World(cfg, "lobby", rooms, minds, tuple(bs), tuple(timed))

    return Scenario(
        f"conflict_m{stakes:g}",
        "Deliver the package to Alice.",
        "Two reporters disagree; units resolve whom to believe. Used to search for stakes ranking reversals.",
        grid({"alice_loc": {A: p_office_a, B: 1 - p_office_a}, "bob_type": bob, "carol_type": carol}),
        build,
    )


GROUNDED_CASES: dict[str, Callable[[], Scenario]] = {
    "false_belief": false_belief,
    "holder_rec": lambda: holder_permutation("rec"),
    "holder_carol": lambda: holder_permutation("carol"),
    "relevance_shift": relevance_shift,
    "nested_reliability": nested_reliability,
    "path_asymmetry": path_asymmetry,
}

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

ALL_CASES: dict[str, Callable[[], Scenario]] = {**TINY_CASES, **GROUNDED_CASES}
