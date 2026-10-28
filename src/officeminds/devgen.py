"""Stage 2 pilot development scenario generator (dev-v1).

DEVELOPMENT DATA ONLY: these groups may never become confirmatory test cases.

Design (frozen before any LLM output is inspected; Stage 1 review, D-008):
- 9 families x GROUPS_PER_FAMILY groups. A group is one public scenario draw (names, office
  labels, family probabilities) plus its variants. Variants stay inside their group.
- The PUBLIC prior of a group depends only on the group draw. Hidden parameters are sampled
  afterwards from a separate RNG stream, ONCE per group, and shared by all variants (paired).
- Variant knobs per family:
    stakes   x1 / x4                 false_belief, conflict, relevance_shift
    evidence absent / present        ambiguity, false_belief, corroborated
    permuted names swapped           distractors, nested_reliability, directed_perspective
    bystander absent / present       stop
- Names are drawn per group from NAME_POOL and office labels from OFFICE_POOL (this also varies
  canonical tie-break order). Intent is never encoded in names, wording or order.
- No scenario is accepted or rejected by method performance. Exclusion rules are declared in
  scripts/freeze_dev_groups.py and applied identically to every group.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .scenarios import Params, Scenario, grid
from .world import COOPERATIVE, OBSTRUCTIVE, Event, PersonMind, World, WorldConfig

DEV_VERSION = "dev-v2"  # current; dev-v1 stays regenerable with generate(version="dev-v1")
# dev-v1 emitted evidence only when its hidden condition was true, so in worlds where it was false the
# evidence variant was visibly identical to the no-evidence variant (found by the pilot input check).
# dev-v2 always emits a visible, informative statement in the evidence variant.
EVIDENCE_MODE = {"dev-v1": "conditional", "dev-v2": "always"}
BASE_SEED = 20261028
GROUPS_PER_FAMILY = 4
NAME_POOL = ("alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi", "ivan", "judy", "kim", "leo",
             "mia", "nadia", "omar", "pia", "quinn", "ravi", "sara", "tomas", "uma", "vik", "wen", "yara", "zane")
OFFICE_POOL = (("office_a", "office_b"), ("room_7", "room_12"), ("lab_north", "lab_south"),
               ("suite_east", "suite_west"), ("desk_3", "desk_9"))
FAMILIES = ("stop", "ambiguity", "false_belief", "distractors", "conflict", "nested_reliability",
            "directed_perspective", "relevance_shift", "corroborated")
KNOBS = {
    "stop": ("bystander",), "ambiguity": ("evidence",), "false_belief": ("stakes", "evidence"),
    "distractors": ("permuted",), "conflict": ("stakes",), "nested_reliability": ("permuted",),
    "directed_perspective": ("permuted",), "relevance_shift": ("stakes",), "corroborated": ("evidence",),
}
FACTORS = {  # outline factor / phenomenon each family is meant to exercise (documentation)
    "stop": "no mental model needed (STOP); physical reasoning only",
    "ambiguity": "informant may or may not know; evidence variant reveals access",
    "false_belief": "outdated cooperative informant (mistaken); stakes F5; evidence variant",
    "distractors": "F1/F1b plausible vs obvious distractor; F4 holder permutation",
    "conflict": "conflicting reports or stated incentive (Reliability); stakes F5",
    "nested_reliability": "R(j->k): forwarder's assessment of a possibly lying source",
    "directed_perspective": "F2/F6 directed path (forwarder -> recipient), depth 2",
    "relevance_shift": "F3 relevance changes when the recipient may appear",
    "corroborated": "resolved/corroborated evidence vs single report",
}


@dataclass(frozen=True)
class Variant:
    stakes: float = 1.0
    evidence: bool = False
    permuted: bool = False
    bystander: bool = True

    def tag(self, family: str) -> str:
        parts = []
        for k in KNOBS[family]:
            v = getattr(self, k)
            parts.append(f"{k}{v:g}" if k == "stakes" else f"{k}{int(v)}")
        return "-".join(parts)


@dataclass(frozen=True)
class GroupDraw:
    family: str
    index: int
    names: tuple[str, ...]  # role-ordered; names[0] is always the recipient
    offices: tuple[str, str]
    knobs: tuple[tuple[str, float | str], ...] = field(default_factory=tuple)
    version: str = DEV_VERSION

    @property
    def group_id(self) -> str:
        return f"{self.version}-{self.family}-g{self.index}"

    @property
    def evidence_always(self) -> bool:
        return EVIDENCE_MODE[self.version] == "always"

    @property
    def sorted_roster(self) -> bool:
        """dev-v2+: the public roster is sorted, so its order cannot encode roles (found by the input
        check: dev-v1 listed the holder before the distractor)."""
        return self.version != "dev-v1"

    def knob(self, k):
        return dict(self.knobs)[k]


def variants_for(family: str) -> list[Variant]:
    knobs = KNOBS[family]
    out = [Variant()]
    for k in knobs:
        nxt = []
        for v in out:
            if k == "stakes":
                nxt += [Variant(1.0, v.evidence, v.permuted, v.bystander), Variant(4.0, v.evidence, v.permuted, v.bystander)]
            elif k == "evidence":
                nxt += [Variant(v.stakes, False, v.permuted, v.bystander), Variant(v.stakes, True, v.permuted, v.bystander)]
            elif k == "permuted":
                nxt += [Variant(v.stakes, v.evidence, False, v.bystander), Variant(v.stakes, v.evidence, True, v.bystander)]
            elif k == "bystander":
                nxt += [Variant(v.stakes, v.evidence, v.permuted, False), Variant(v.stakes, v.evidence, v.permuted, True)]
        out = nxt
    return out


def draw_group(family: str, index: int, seed: int = BASE_SEED, version: str = DEV_VERSION) -> GroupDraw:
    """Public draw only (names, labels, probabilities). Uses its own RNG stream."""
    rng = random.Random(f"{seed}:public:{family}:{index}")
    names = tuple(rng.sample(NAME_POOL, 4))
    offices = OFFICE_POOL[rng.randrange(len(OFFICE_POOL))]
    if rng.random() < 0.5:
        offices = (offices[1], offices[0])  # vary which label is listed first
    pick = lambda xs: xs[rng.randrange(len(xs))]
    knobs = {
        "stop": {"p_saw": pick((0.3, 0.5, 0.7))},
        "ambiguity": {"p_saw": pick((0.3, 0.5, 0.7))},
        "false_belief": {"p_moved": pick((0.2, 0.3, 0.4))},
        "distractors": {"p_saw_holder": pick((0.5, 0.7)), "distractor": "plausible" if index % 2 == 0 else "obvious",
                        "p_saw_distractor": pick((0.3, 0.5))},
        "conflict": {"subtype": "two_reporters" if index % 2 == 0 else "one_reporter",
                     "q_coop": pick((0.9, 0.95, 0.975)),
                     "x_acc": pick((0.5, 0.8)), "x_mist": pick((0.05, 0.1)), "x_obs": pick((0.1, 0.25)),
                     "y_acc": pick((0.1, 0.5)), "y_mist": pick((0.02, 0.1)), "y_obs": pick((0.5, 0.8))},
        "nested_reliability": {"p_naive": pick((0.3, 0.5, 0.7)), "q_coop": pick((0.5, 0.7))},
        "directed_perspective": {"p_not_heard": pick((0.4, 0.5, 0.6)), "p_told": pick((0.3, 0.5)),
                                 "p_rec_heard": pick((0.3, 0.5))},
        "relevance_shift": {"p_moved": pick((0.2, 0.3)), "p_returns": pick((0.3, 0.5))},
        "corroborated": {"p_mistaken": pick((0.1, 0.2, 0.3))},
    }[family]
    return GroupDraw(family, index, names, offices, tuple(sorted(knobs.items())), version)


# ----------------------------------------------------------------------------- helpers
def _layout(offices):
    a, b = offices
    return {"lobby": ("hall",), "hall": ("lobby", a, b), a: ("hall",), b: ("hall",)}


def _cfg(g, roster, recipient, offices, facts, chute=True, handoff=None, stakes=1.0, horizon=8):
    roster = tuple(sorted(roster)) if g.sorted_roster else tuple(roster)
    return WorldConfig(adjacency=_layout(offices), offices=tuple(offices), chute_room="lobby" if chute else None,
                       recipient=recipient, roster=roster, query_facts=tuple(facts),
                       fact_domains={f: tuple(offices) for f in facts}, handoff_routes=handoff or {},
                       stakes=stakes, horizon=horizon)


def _other(room, offices):
    return offices[1] if room == offices[0] else offices[0]


def _half(offices):
    return {offices[0]: 0.5, offices[1]: 0.5}


def _yn(p):
    return {"yes": p, "no": 1 - p}


def _roles(g: GroupDraw, v: Variant, swap: tuple[int, int] | None = None) -> list[str]:
    names = list(g.names)
    if swap and v.permuted:
        i, j = swap
        names[i], names[j] = names[j], names[i]
    return names


# ----------------------------------------------------------------------------- families
def _stop(g, v):
    R, B = g.names[:2]
    loc_fact = f"{R}_loc"

    def build(p):
        people = (R, B) if v.bystander else (R,)
        offices = g.offices
        cfg = _config_with_lobby(g, people, R, offices, loc_fact, v.stakes)
        rooms = {x: "lobby" for x in people}
        minds = {x: PersonMind() for x in people}
        seen = (B,) if v.bystander and p["B_saw"] == "yes" else ()
        bs = (Event("bs-arrives", -1, "witness", "lobby", R, loc_fact, "lobby", present=(R,) + seen),)
        return World(cfg, "lobby", rooms, minds, bs)

    return grid({"B_saw": _yn(g.knob("p_saw"))}), build


def _config_with_lobby(g, people, R, offices, loc_fact, stakes):
    cfg = _cfg(g, people, R, offices, [loc_fact], stakes=stakes)
    return WorldConfig(**{**cfg.__dict__, "fact_domains": {loc_fact: ("lobby",) + tuple(offices)}})


def _ambiguity(g, v):
    R, I = g.names[:2]
    loc_fact = f"{R}_loc"

    def build(p):
        cfg = _cfg(g, (R, I), R, g.offices, [loc_fact], stakes=v.stakes)
        rooms, minds = {R: p["loc"], I: "lobby"}, {R: PersonMind(), I: PersonMind()}
        seen = (I,) if p["I_saw"] == "yes" else ()
        bs = (Event("bs-walks", -2, "witness", "hall", R, loc_fact, p["loc"], present=(R,) + seen),)
        timed = ()
        if v.evidence and p["I_saw"] == "yes":
            timed = (Event("t0-access", 0, "say", "lobby", I, text="I was at the front desk all morning."),)
        elif v.evidence and g.evidence_always:
            timed = (Event("t0-access", 0, "say", "lobby", I, text="I was out of the building all morning."),)
        return World(cfg, "lobby", rooms, minds, bs, timed)

    return grid({"loc": _half(g.offices), "I_saw": _yn(g.knob("p_saw"))}), build


def _moved(g, v, R, holders, others, p, timed=(), returns=False):
    loc_fact = f"{R}_loc"
    people = (R,) + tuple(holders) + tuple(others)
    cfg = _cfg(g, people, R, g.offices, [loc_fact], stakes=v.stakes)
    final = _other(p["initial"], g.offices) if p["moved"] == "yes" else p["initial"]
    rooms = {R: final, **{x: "lobby" for x in people[1:]}}
    minds = {x: PersonMind() for x in people}
    bs = [Event("bs-walks", -3, "witness", "hall", R, loc_fact, p["initial"], present=(R,) + tuple(holders))]
    if p["moved"] == "yes":
        bs.append(Event("bs-switches", -1, "witness", final, R, loc_fact, final, present=(R,)))
    timed = tuple(timed) + ((Event("t1-returns", 1, "enter", "lobby", R),) if returns else ())
    return World(cfg, "lobby", rooms, minds, tuple(bs), timed)


def _false_belief(g, v):
    R, I, C = g.names[:3]

    def build(p):
        timed = [Event("t0-saw", 0, "say", "lobby", I, text=f"I saw {R.capitalize()} head to the office earlier.")]
        if v.evidence and p["moved"] == "yes":
            timed.append(Event("t0-switch", 0, "say", "lobby", C, text=f"{R.capitalize()} mentioned switching offices today."))
        elif v.evidence and g.evidence_always:
            timed.append(Event("t0-switch", 0, "say", "lobby", C, text=f"{R.capitalize()} said they are keeping the same office today."))
        return _moved(g, v, R, (I,), (C,), p, timed)

    return grid({"initial": _half(g.offices), "moved": _yn(g.knob("p_moved"))}), build


def _relevance_shift(g, v):
    R, I = g.names[:2]

    def build(p):
        timed = [Event("t0-saw", 0, "say", "lobby", I, text=f"I saw {R.capitalize()} head to the office earlier.")]
        return _moved(g, v, R, (I,), (), p, timed, returns=p["returns"] == "yes")

    return grid({"initial": _half(g.offices), "moved": _yn(g.knob("p_moved")), "returns": _yn(g.knob("p_returns"))}), build


def _distractors(g, v):
    R, H, D = _roles(g, v, swap=(1, 2))[:3]
    loc_fact = f"{R}_loc"
    plausible = g.knob("distractor") == "plausible"

    def build(p):
        cfg = _cfg(g, (R, H, D), R, g.offices, [loc_fact], stakes=v.stakes)
        rooms, minds = {R: p["loc"], H: "lobby", D: "lobby"}, {x: PersonMind() for x in (R, H, D)}
        seen = tuple(x for x, k in ((H, "H_saw"), (D, "D_saw")) if p[k] == "yes")
        bs = (Event("bs-walks", -2, "witness", "hall", R, loc_fact, p["loc"], present=(R,) + seen),)
        timed = () if plausible else (Event("t0-arrived", 0, "say", "lobby", D, text="I just got here."),)
        return World(cfg, "lobby", rooms, minds, bs, timed)

    d_prior = _yn(g.knob("p_saw_distractor")) if plausible else {"no": 1.0}
    return grid({"loc": _half(g.offices), "H_saw": _yn(g.knob("p_saw_holder")), "D_saw": d_prior}), build


def _conflict(g, v):
    R, X, Y = g.names[:3]
    loc_fact = f"{R}_loc"
    two = g.knob("subtype") == "two_reporters"

    def build(p):
        people = (R, X, Y) if two else (R, X)
        cfg = _cfg(g, people, R, g.offices, [loc_fact], stakes=v.stakes)
        loc = p["loc"]
        rooms = {R: loc, **{x: "lobby" for x in people[1:]}}
        minds, bs, timed = {R: PersonMind()}, [Event("bs-self", -4, "witness", loc, R, loc_fact, loc, present=(R,))], []
        for i, who in enumerate(people[1:]):
            kind = p[f"{'x' if who == X else 'y'}_type"]
            minds[who] = PersonMind(intent=OBSTRUCTIVE if kind == "obstructive" else COOPERATIVE)
            believed = _other(loc, g.offices) if kind == "mistaken" else loc
            bs.append(Event(f"bs-{i}-sees", -2 - i, "witness", "hall", who, loc_fact, believed, present=(who,)))
            said = _other(believed, g.offices) if kind == "obstructive" else believed
            timed.append(Event(f"t0-{i}-claims", 0, "claim", "lobby", who, loc_fact, said, f"{loc_fact} = {said}"))
        if not two:
            timed.insert(0, Event("t0-incentive", 0, "say", "lobby", X, text="I'd rather keep that package myself."))
        return World(cfg, "lobby", rooms, minds, tuple(bs), tuple(timed))

    if two:
        types = lambda pre: {"accurate": g.knob(f"{pre}_acc"), "mistaken": g.knob(f"{pre}_mist"), "obstructive": g.knob(f"{pre}_obs")}
        prior = grid({"loc": _half(g.offices), "x_type": types("x"), "y_type": types("y")})
    else:
        q = g.knob("q_coop")
        prior = grid({"loc": _half(g.offices), "x_type": {"accurate": q, "obstructive": 1 - q}, "y_type": {"accurate": 1.0}})
    return prior, build


def _nested(g, v):
    R, L, F, W = _roles(g, v, swap=(1, 2))
    loc_fact = f"{R}_loc"

    def build(p):
        cfg = _cfg(g, (R, L, F), R, g.offices, [loc_fact], chute=False, handoff={F: ("", loc_fact)}, stakes=v.stakes)
        loc, obstructive = p["loc"], p["L_intent"] == OBSTRUCTIVE
        rooms = {R: loc, L: "lobby", F: "lobby"}
        minds = {R: PersonMind(), L: PersonMind(intent=p["L_intent"]), F: PersonMind(), W: PersonMind()}
        if p["F_naive"] == "yes":
            vouch = Event("bs-vouch", -3, "assess", "lobby", L, L, COOPERATIVE, present=(L, F))
        else:
            vouch = Event("bs-warn", -3, "assess", "hall", W, L, p["L_intent"], present=(W, F))
        claimed = _other(loc, g.offices) if obstructive else loc
        bs = (Event("bs-sees", -4, "witness", "hall", L, loc_fact, loc, present=(R, L)), vouch,
              Event("bs-tells", -2, "assert", "lobby", L, loc_fact, claimed, present=(L, F)))
        incentive = Event("t0-incentive", 0, "say", "lobby", L, text="I'd rather keep that package myself.")
        return World(cfg, "lobby", rooms, minds, bs, (incentive,))

    q = g.knob("q_coop")
    return grid({"loc": _half(g.offices), "L_intent": {COOPERATIVE: q, OBSTRUCTIVE: 1 - q},
                 "F_naive": _yn(g.knob("p_naive"))}), build


def _directed(g, v):
    R, F, A = _roles(g, v, swap=(0, 1))[:3]

    def build(p):
        cfg = _cfg(g, (R, F), R, g.offices, ["meeting_room"], chute=False, handoff={F: (R, "meeting_room")}, stakes=v.stakes)
        initial = p["initial"]
        moved = _other(initial, g.offices)
        heard, told = p["story"] != "not_heard", p["story"] == "heard_told"
        rooms = {R: moved if heard else initial, F: "lobby"}
        minds = {R: PersonMind(), F: PersonMind(), A: PersonMind()}
        bs = [Event("bs-tells", -4, "tell", "lobby", R, "meeting_room", initial, present=(R, F))]
        hearers = ((R,) if heard else ()) + ((F,) if p["F_heard"] == "yes" else ())
        if hearers:
            bs.append(Event("bs-moved", -3, "tell", "hall", A, "meeting_room", moved, present=(A,) + hearers))
        if told:
            bs.append(Event("bs-update", -2, "claim", "lobby", R, "meeting_room", moved, present=(R, F)))
        talk = Event("t0-mentions", 0, "say", "lobby", F, text=f"{R.capitalize()} told me this morning where the meeting is.")
        return World(cfg, "lobby", rooms, minds, tuple(bs), (talk,), facts={"meeting_room": moved})

    pn, pt = g.knob("p_not_heard"), g.knob("p_told")
    return grid({"initial": _half(g.offices),
                 "story": {"not_heard": pn, "heard_told": (1 - pn) * pt, "heard_not_told": (1 - pn) * (1 - pt)},
                 "F_heard": _yn(g.knob("p_rec_heard"))}), build


def _corroborated(g, v):
    R, I1, I2 = g.names[:3]
    loc_fact = f"{R}_loc"

    def build(p):
        people = (R, I1, I2) if v.evidence else (R, I1)
        cfg = _cfg(g, people, R, g.offices, [loc_fact], stakes=v.stakes)
        loc = p["loc"]
        rooms = {R: loc, **{x: "lobby" for x in people[1:]}}
        minds = {x: PersonMind() for x in people}
        bs, timed = [Event("bs-self", -4, "witness", loc, R, loc_fact, loc, present=(R,))], []
        for i, who in enumerate(people[1:]):
            believed = _other(loc, g.offices) if p[f"m{i}"] == "yes" else loc
            bs.append(Event(f"bs-{i}-sees", -2 - i, "witness", "hall", who, loc_fact, believed, present=(who,)))
            timed.append(Event(f"t0-{i}-claims", 0, "claim", "lobby", who, loc_fact, believed, f"{loc_fact} = {believed}"))
        return World(cfg, "lobby", rooms, minds, tuple(bs), tuple(timed))

    pm = g.knob("p_mistaken")
    return grid({"loc": _half(g.offices), "m0": _yn(pm), "m1": _yn(pm)}), build


BUILDERS = {"stop": _stop, "ambiguity": _ambiguity, "false_belief": _false_belief, "distractors": _distractors,
            "conflict": _conflict, "nested_reliability": _nested, "directed_perspective": _directed,
            "relevance_shift": _relevance_shift, "corroborated": _corroborated}


@dataclass(frozen=True)
class DevInstance:
    instance_id: str
    group_id: str
    family: str
    variant: Variant
    scenario: Scenario
    hidden: Params  # PRIVILEGED: sampled once per group, shared by its variants


def make_instance(g: GroupDraw, v: Variant) -> Scenario:
    prior, build = BUILDERS[g.family](g, v)
    R = _roles(g, v, swap=(0, 1) if g.family == "directed_perspective" else None)[0]
    iid = f"{g.group_id}-{v.tag(g.family)}"
    return Scenario(iid, f"Deliver the package to {R.capitalize()}.", FACTORS[g.family], prior, build)


def sample_hidden(prior, family: str, index: int, seed: int = BASE_SEED) -> Params:
    rng = random.Random(f"{seed}:hidden:{family}:{index}")
    params, weights = zip(*prior)
    return rng.choices(params, weights=weights, k=1)[0]


def generate(seed: int = BASE_SEED, groups_per_family: int = GROUPS_PER_FAMILY, version: str = DEV_VERSION) -> list[DevInstance]:
    out = []
    for family in FAMILIES:
        for index in range(groups_per_family):
            g = draw_group(family, index, seed, version)
            scenarios = [(v, make_instance(g, v)) for v in variants_for(family)]
            priors = {tuple(sc.prior) for _, sc in scenarios}
            assert len(priors) == 1, f"variants of {g.group_id} must share one public prior"
            hidden = sample_hidden(scenarios[0][1].prior, family, index, seed)
            out += [DevInstance(sc.id, g.group_id, family, v, sc, hidden) for v, sc in scenarios]
    return out


def registry(seed: int = BASE_SEED, version: str = DEV_VERSION) -> dict:
    """scenario_id -> factory, for episode replay."""
    return {inst.instance_id: (lambda s=inst.scenario: s) for inst in generate(seed, version=version)}
