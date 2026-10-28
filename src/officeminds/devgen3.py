"""dev-v3 development generator: visible prologue + declared public model (D-014; reports/dev-v3-block).

DEVELOPMENT DATA ONLY. Design: reports/dev-v3-block/experiment-plan.md, Entry 1 (fixed before any dev-v3 output).

- 4 strata x 3 constructions = 12 base groups. Variants per group: stakes x1/x4 x name rotation = 4 instances.
- One public draw per group (names, office labels and order, disclosed rates), then ONE hidden draw from a separate
  RNG stream, shared by the group's four variants.
- The prior of every group is built from its PublicSpec, and the "PUBLIC MODEL OF THIS TASK" text in the task card
  is generated from the same spec, so every hidden variable, its support and its probabilities are disclosed. The
  realized hidden values are not.
- The robot watched a prologue in the lobby. Every lobby event is a visible notice with who else was present (see
  world.Event.visible_as); events elsewhere are not shown.
- No group is selected, replaced or dropped by method performance.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction

from .scenarios import Params, Scenario, grid
from .world import COOPERATIVE, OBSTRUCTIVE, Event, PersonMind, World, WorldConfig

DEV_VERSION = "dev-v3"
BASE_SEED = 20261029
NAME_POOL = ("alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi", "ivan", "judy", "kim", "leo",
             "mia", "nadia", "omar", "pia", "quinn", "ravi", "sara", "tomas", "uma", "vik", "wen", "yara", "zane")
OFFICE_POOL = (("office_a", "office_b", "office_c"), ("room_7", "room_12", "room_19"),
               ("lab_north", "lab_south", "lab_west"), ("suite_1", "suite_2", "suite_3"),
               ("desk_3", "desk_9", "desk_14"))
STRATA = {1: "physical_stop", 2: "first_order", 3: "depth2_relay", 4: "probabilistic"}
CONSTRUCTIONS = {1: ("1a", "1b", "1c"), 2: ("2a", "2b", "2c"), 3: ("3a", "3b", "3c"), 4: ("4a", "4b", "4c")}
LEVELS = ("none", "plausible", "obvious")
BASE_ROLES = {"1": ("R",), "1c": ("R", "C"), "2": ("R", "H", "N"), "3": ("R", "A", "F"), "4a": ("R", "W"),
              "4b": ("R", "X", "Y"), "4c": ("R", "X")}
DISTRACTOR_ROLE = {"none": (), "plausible": ("P",), "obvious": ("D",)}


def roles_for(construction: str, level: str) -> tuple[str, ...]:
    """Role order (names are assigned in this order and rotated by one for the permuted variant)."""
    base = BASE_ROLES.get(construction) or BASE_ROLES[construction[0]]
    return base + DISTRACTOR_ROLE[level]


ROLES = {c: roles_for(c, LEVELS[(g + s) % 3]) for s, cs in {1: ("1a", "1b", "1c"), 2: ("2a", "2b", "2c"),
         3: ("3a", "3b", "3c"), 4: ("4a", "4b", "4c")}.items() for g, c in enumerate(cs)}
PURPOSE = {  # privileged documentation; never shown to agents
    "1a": "physical control: announced office (drop); plausible distractor heard it too",
    "1b": "physical control: unannounced (search); obvious distractor knows nothing",
    "1c": "physical control: announced and corroborated by a colleague; zero mental value",
    "2a": "first-order: quiet update to one of two couriers (give to the informed one)",
    "2b": "first-order: informed courier departed; stale courier remains (search the other offices)",
    "2c": "first-order recency: two quiet updates; the later listener is current",
    "3a": "depth-2: organizer -> F -> R relay; F->R current (give F)",
    "3b": "depth-2: F and R told separately; F current but F->R stale (do not give F)",
    "3c": "depth-2: only F told; R uninformed; F->R = R's (stale) belief = R's location (give F)",
    "4a": "probabilistic staleness: disclosed move rate q; stakes flip drop vs walk",
    "4b": "probabilistic reliability: two conflicting reporters with disclosed obstruction rates",
    "4c": "probabilistic reliability: one reporter with a stated incentive; disclosed obstruction rate",
}
HORIZON = 8


def distractor_level(stratum: int, g: int) -> str:
    return LEVELS[(g + stratum) % 3]


# ----------------------------------------------------------------------------- public specification
@dataclass(frozen=True)
class HiddenVar:
    name: str
    description: str  # public wording used in the task card
    dist: tuple[tuple[str, Fraction], ...]  # value -> probability (exact; disclosed)


@dataclass(frozen=True)
class PublicSpec:
    group_id: str
    stratum: int
    construction: str
    distractor: str
    names: tuple[str, ...]  # role-ordered (ROLES[construction]), before any variant rotation
    offices: tuple[str, str, str]  # listing order is part of the public draw
    rates: tuple[tuple[str, Fraction], ...] = ()
    version: str = DEV_VERSION

    def rate(self, k: str) -> Fraction:
        return dict(self.rates)[k]


def _f(x) -> Fraction:
    return Fraction(x).limit_denominator(1000)


def draw_spec(stratum: int, g: int, seed: int = BASE_SEED) -> PublicSpec:
    c = CONSTRUCTIONS[stratum][g]
    level = distractor_level(stratum, g)
    rng = random.Random(f"{seed}:{DEV_VERSION}:public:{c}")
    names = tuple(rng.sample(NAME_POOL, len(roles_for(c, level))))
    offices = list(OFFICE_POOL[rng.randrange(len(OFFICE_POOL))])
    rng.shuffle(offices)
    rates = ()
    if c == "4a":
        rates = (("q_moved", _f(rng.choice(("0.05", "0.06")))),)
    elif c == "4b":
        rx, ry = rng.choice((("0.02", "0.3"), ("0.03", "0.4")))
        rates = (("r_X", _f(rx)), ("r_Y", _f(ry)))
    elif c == "4c":
        rates = (("r_incentive", _f(rng.choice(("0.05", "0.06")))),)
    return PublicSpec(f"{DEV_VERSION}-{c}", stratum, c, level, names, tuple(offices), rates)


# ----------------------------------------------------------------------------- visible event helpers
class _Script:
    """Builds an ordered t=0 prologue; lobby events carry robot-visible notices."""

    def __init__(self):
        self.events: list[Event] = []

    def _add(self, kind, room, actor="", fact="", value="", text="", present=None, visible=None, t=0):
        self.events.append(Event(f"t{t}-{len(self.events)}-{kind}", t, kind, room, actor, fact, value, text,
                                 present, visible))

    def announce(self, actor, fact, value):
        self._add("tell", "lobby", actor, fact, value,
                  visible=("announce", f'{actor} announces to everyone present: "{fact} = {value}"'))

    def statement(self, actor, fact, value):
        self._add("claim", "lobby", actor, fact, value, visible=("statement", f'{actor} says: "{fact} = {value}"'))

    def remark(self, actor, text):
        self._add("say", "lobby", actor, visible=("remark", f'{actor} says: "{text}"'))

    def quiet(self, actor, listener, fact, value):
        self._add("tell", "lobby", actor, fact, value, present=(actor, listener),
                  visible=("quiet", f"{actor} talks quietly with {listener}; the robot cannot hear what is said"))

    def leave(self, actor, dest, building=False):
        self._add("enter", dest, actor,
                  visible=("leave", f"{actor} leaves the lobby" + (" and the building" if building else "")))

    def arrive(self, actor):
        self._add("enter", "lobby", actor, visible=("arrive", f"{actor} arrives in the lobby"))

    def offscreen_move(self, actor, room):
        self._add("enter", room, actor)

    def self_sees(self, actor, fact, room):
        """The mover sees where they are (r6 rule 2); off-screen."""
        self._add("witness", room, actor, fact, room, present=(actor,))


def _others(offices, room):
    return [o for o in offices if o != room]


def _uniform(values) -> tuple[tuple[str, Fraction], ...]:
    values = list(values)
    return tuple((v, Fraction(1, len(values))) for v in values)


# ----------------------------------------------------------------------------- constructions
def hidden_vars(spec: PublicSpec, n: dict) -> list[HiddenVar]:
    """Every hidden variable of the group with its disclosed distribution (`n`: role -> name)."""
    o, c, R = spec.offices, spec.construction, n["R"]
    first = HiddenVar("a", f"the office {R} first went to / was first seen in", _uniform(o))
    other = lambda nm, desc: HiddenVar(nm, desc, (("0", Fraction(1, 2)), ("1", Fraction(1, 2))))
    yn = lambda nm, desc, p: HiddenVar(nm, desc, (("yes", p), ("no", 1 - p)))
    intent = lambda nm, desc, p: HiddenVar(nm, desc, ((OBSTRUCTIVE, p), (COOPERATIVE, 1 - p)))
    if c in ("1a", "1b", "1c"):
        return [first]
    if c in ("2a", "2b"):
        return [first, other("m1", f"which of the two other offices {R} moved to (each equally likely)")]
    if c == "2c":
        return [first, other("m1", f"which of the two other offices {R} moved to first (each equally likely)"),
                other("m2", f"which of the two offices other than that one {R} moved to next (each equally likely)")]
    if c in ("3a", "3b", "3c"):
        return [HiddenVar("a", f"the meeting office {n['A']} first announced", _uniform(o)),
                other("m1", f"which of the two other offices {n['A']} changed the meeting to (each equally likely)")]
    if c == "4a":
        return [HiddenVar("a", f"the office {n['W']} saw {R} go into", _uniform(o)),
                yn("moved", f"whether {R} has since moved to a different office", spec.rate("q_moved")),
                other("m1", f"if {R} moved, which of the two other offices (each equally likely)")]
    if c == "4b":
        x1, x2 = sorted((n["X"], n["Y"]))
        return [HiddenVar("a", f"the office {R} is in (both {x1} and {x2} saw {R} go there)", _uniform(o)),
                intent("x_intent", f"whether {n['X']} is obstructive", spec.rate("r_X")),
                intent("y_intent", f"whether {n['Y']} is obstructive", spec.rate("r_Y")),
                other("x_lie", f"the wrong office {n['X']} names if obstructive (each other office equally likely)"),
                other("y_lie", f"the wrong office {n['Y']} names if obstructive (each other office equally likely)")]
    if c == "4c":
        return [HiddenVar("a", f"the office {R} is in ({n['X']} saw {R} go there)", _uniform(o)),
                intent("x_intent", f"whether {n['X']} is obstructive", spec.rate("r_incentive")),
                other("x_lie", f"the wrong office {n['X']} names if obstructive (each other office equally likely)")]
    raise ValueError(c)


def _keep(spec: PublicSpec):
    if spec.construction != "4b":
        return lambda p: True
    o = spec.offices

    def claims_differ(p):
        a = p["a"]
        cx = a if p["x_intent"] == COOPERATIVE else _others(o, a)[int(p["x_lie"])]
        cy = a if p["y_intent"] == COOPERATIVE else _others(o, a)[int(p["y_lie"])]
        return cx != cy
    return claims_differ


def process_text(spec: PublicSpec, n: dict) -> list[str]:
    """Public description of how this task's prologue was generated (no realized hidden values)."""
    c, R = spec.construction, n["R"]
    lf = f"{R}_loc"
    coop = "Everyone in this task is cooperative: they answer questions sincerely (with what they believe)."
    if spec.stratum in (1, 4):
        coop += " Nobody accepts handed-over packages."
    quiet = (f"A quiet conversation started by {R} always tells the listener (and only the listener) the office {R} "
             f"is about to go to.")
    out = {
        "1a": [f"{R} announced the office they were going to, went there, and stays there. {coop}"],
        "1b": [f"{R} went to one of the offices without telling anyone, and stays there. {coop}"],
        "1c": [f"{R} announced the office they were going to, went there, and stays there. {coop}"],
        "2a": [f"{R} announced an office and went there. Later {R} moved to one of the two other offices, stopping in "
               f"the lobby on the way. {quiet} {R} stays in the new office. {coop}"],
        "2b": [f"{R} announced an office and went there. Later {R} moved to one of the two other offices, stopping in "
               f"the lobby on the way. {quiet} {R} stays in the new office. People who leave the building do not "
               f"come back during the task. {coop}"],
        "2c": [f"{R} announced an office and went there. Later {R} moved twice, each time to an office other than the "
               f"one they were in, stopping in the lobby before each move. {quiet} {R} stays in the last office. {coop}"],
    }.get(c)
    if out:
        c1, c2 = sorted((n.get("H", ""), n.get("N", "")))  # alphabetical: role order would mark the informed courier
        return out + [f"{c1} and {c2} accept handed-over packages and forward them to the office where they "
                      f"believe {R} is. Nobody else accepts handed-over packages."] if c.startswith("2") else out
    if c.startswith("3"):
        return [f"{n['A']} organizes a meeting that {R} attends. {n['A']} announced the meeting office, later changed "
                f"it to one of the two other offices, and conveyed the change only in the quiet conversations shown. "
                f"A quiet conversation in this task always tells the listener (and only the listener) the current "
                f"meeting office. Then {n['A']} left the building and does not come back during the task.",
                f"{R} goes to, and stays in, the office where {R} believes the meeting is.",
                f"{n['F']} accepts handed-over packages and forwards them to the office where {n['F']} thinks {R} "
                f"will go, that is, to what {n['F']} thinks {R} believes about meeting_room. Nobody else accepts "
                f"handed-over packages. There is no chute in this building. {coop}"]
    if c == "4a":
        return [f"Earlier {n['W']} saw {R} go into an office. Since then {R} may have moved to a different office "
                f"(probability below); if so, {n['W']} did not see it. {coop}"]
    lie = ("An obstructive person names a wrong office (each other office equally likely) and names the same wrong "
           "office again if asked; a cooperative person answers with what they believe.")
    if c == "4b":
        x1, x2 = sorted((n["X"], n["Y"]))
        return [f"Both {x1} and {x2} saw which office {R} went into; {R} stays there. Each of them is "
                f"obstructive independently with the probability below. {lie} This task shows a case where their "
                f"two statements differ; everyone else is cooperative."]
    if c == "4c":
        return [f"{n['X']} saw which office {R} went into; {R} stays there. A person who says they would rather keep "
                f"the package is obstructive with the probability below; everyone else is cooperative. {lie}"]
    raise ValueError(c)


def _fmt(p: Fraction) -> str:
    return f"{float(p):.4g}"


def public_model_text(spec: PublicSpec, n: dict) -> str:
    lines = ["PUBLIC MODEL OF THIS TASK (shared by everyone; describes how this situation was generated):"]
    lines += [f"- {s}" for s in process_text(spec, n)]
    lines.append("- After the prologue shown in the history, nobody but the robot moves, and people's beliefs change "
                 "only through what is said in answer to the robot's questions. Everyone shown in the lobby at the end "
                 "of the prologue stays there.")
    if spec.distractor == "obvious":
        lines.append(f"- {n['D']} was elsewhere during everything before arriving and saw and heard nothing about it.")
    lines.append("- Hidden quantities and their probabilities (the robot does not see the realized values):")
    for hv in hidden_vars(spec, n):
        lines.append(f"  - {hv.description}: " + ", ".join(f"{v} {_fmt(p)}" for v, p in hv.dist)
                     if hv.name not in ("m1", "m2", "x_lie", "y_lie") else
                     f"  - {hv.description}")
    return "\n".join(lines)


def build_world(spec: PublicSpec, n: dict, stakes: float, p: dict) -> World:
    o, c, R = spec.offices, spec.construction, n["R"]
    lf = f"{R}_loc"
    s = _Script()
    people = [n[r] for r in roles_for(c, spec.distractor)]
    rooms = {x: "lobby" for x in people}
    minds = {x: PersonMind() for x in people}
    facts, handoff, chute, query = {}, {}, True, [lf]
    backstory: list[Event] = []
    a = p["a"]
    if spec.distractor == "obvious":
        rooms[n["D"]] = "outside"

    if c in ("1a", "1c"):
        s.announce(R, lf, a)
        s.leave(R, a)
        s.self_sees(R, lf, a)
        if c == "1c":
            s.statement(n["C"], lf, a)
    elif c == "1b":
        s.leave(R, a)
        s.self_sees(R, lf, a)
    elif c in ("2a", "2b", "2c"):
        s.announce(R, lf, a)
        s.leave(R, a)
        s.self_sees(R, lf, a)
        m1 = _others(o, a)[int(p["m1"])]
        s.arrive(R)
        s.quiet(R, n["H"], lf, m1)
        s.leave(R, m1)
        s.self_sees(R, lf, m1)
        if c == "2b":
            s.leave(n["H"], "outside", building=True)
        if c == "2c":
            m2 = _others(o, m1)[int(p["m2"])]
            s.arrive(R)
            s.quiet(R, n["N"], lf, m2)
            s.leave(R, m2)
            s.self_sees(R, lf, m2)
        handoff = {n["H"]: ("", lf), n["N"]: ("", lf)}
    elif c in ("3a", "3b", "3c"):
        A, F = n["A"], n["F"]
        b = _others(o, a)[int(p["m1"])]
        query, chute, facts = ["meeting_room"], False, {"meeting_room": b}
        s.announce(A, "meeting_room", a)
        s.statement(R, "meeting_room", a)
        s.quiet(A, F, "meeting_room", b)
        if c == "3a":
            s.quiet(F, R, "meeting_room", b)
        elif c == "3b":
            s.quiet(A, R, "meeting_room", b)
        s.leave(A, "outside", building=True)
        s.leave(R, a if c == "3c" else b)
        handoff = {F: (R, "meeting_room")}
    elif c == "4a":
        W = n["W"]
        final = _others(o, a)[int(p["m1"])] if p["moved"] == "yes" else a
        rooms[R] = final
        backstory = [Event("bs-0-sees", -3, "witness", "hall", R, lf, a, present=(R, W))]
        if p["moved"] == "yes":
            backstory.append(Event("bs-1-moves", -1, "witness", final, R, lf, final, present=(R,)))
        s.statement(W, lf, a)
        s.remark(W, f"I saw {R} go into {a} earlier.")
    elif c in ("4b", "4c"):
        rooms[R] = a
        reporters = [n["X"], n["Y"]] if c == "4b" else [n["X"]]
        backstory = [Event("bs-0-sees", -3, "witness", "hall", R, lf, a, present=(R, *reporters))]
        for who, key in zip(reporters, ("x", "y")):
            minds[who] = PersonMind(intent=p[f"{key}_intent"])
            minds[who].lies[lf] = _others(o, a)[int(p[f"{key}_lie"])]
        for who in sorted(reporters):  # alphabetical speaking order: role order would mark the low-rate reporter
            s.statement(who, lf, a if minds[who].intent == COOPERATIVE else minds[who].lies[lf])
        if c == "4c":
            s.remark(n["X"], "I'd rather keep that package myself.")
    if spec.distractor == "obvious":
        s.arrive(n["D"])
        s.remark(n["D"], "I just got here.")
    roster = tuple(sorted(people))
    cfg = WorldConfig(adjacency={"lobby": ("hall",), "hall": ("lobby", *o), **{x: ("hall",) for x in o}},
                      offices=tuple(o), chute_room="lobby" if chute else None, recipient=R, roster=roster,
                      query_facts=tuple(query), fact_domains={f: tuple(o) for f in query}, handoff_routes=handoff,
                      stakes=stakes, horizon=HORIZON, public_model=public_model_text(spec, n))
    return World(cfg, "lobby", rooms, minds, tuple(backstory), tuple(s.events), facts)


def prior_of(spec: PublicSpec, n: dict) -> tuple[tuple[Params, float], ...]:
    domains = {hv.name: {v: float(pr) for v, pr in hv.dist} for hv in hidden_vars(spec, n)}
    return grid(domains, _keep(spec))


# ----------------------------------------------------------------------------- superset public models (R1, R2)
SUPERSET_PATTERNS = {2: [(c, sw) for c in ("2a", "2b", "2c") for sw in (False, True)],  # H<->N swap: both couriers
                     3: [(c, False) for c in ("3a", "3b", "3c")]}  # the courier is public, so no A<->F swap


def pattern_names(n: dict, stratum: int, swap: bool) -> dict:
    if not swap:
        return dict(n)
    m = dict(n)
    m["H"], m["N"] = n["N"], n["H"]
    return m


def superset_scenario(spec: PublicSpec, n: dict, stakes: float, strip_notices: bool = False) -> Scenario:
    """Stratum-level public model for qualification only (never shown to agents): the communication pattern
    (construction, holder swap) is uniform over SUPERSET_PATTERNS[stratum], times that pattern's own disclosed hidden
    variables. With strip_notices, every prologue notice is removed from the robot's observations (card-only check)."""
    from dataclasses import replace
    rows = []
    pats = SUPERSET_PATTERNS[spec.stratum]
    for c, sw in pats:
        sp = replace(spec, construction=c)
        for params, w in prior_of(sp, pattern_names(n, spec.stratum, sw)):
            rows.append(((("pattern", f"{c}:{int(sw)}"),) + params, w / len(pats)))

    def build(p: dict) -> World:
        c, sw = p["pattern"].split(":")
        sp = replace(spec, construction=c)
        w = build_world(sp, pattern_names(n, spec.stratum, sw == "1"), stakes,
                        {k: v for k, v in p.items() if k != "pattern"})
        if strip_notices:
            w.timed_events = tuple(replace(e, visible_as=None) for e in w.timed_events)
        return w
    return Scenario(f"{spec.group_id}-superset", f"Deliver the package to {n['R'].capitalize()}.", "superset",
                    tuple(rows), build)


# ----------------------------------------------------------------------------- instances
@dataclass(frozen=True)
class Variant3:
    stakes: float
    permuted: bool

    @property
    def tag(self) -> str:
        return f"stakes{self.stakes:g}-perm{int(self.permuted)}"


VARIANTS = (Variant3(1.0, False), Variant3(4.0, False), Variant3(1.0, True), Variant3(4.0, True))


def role_names(spec: PublicSpec, permuted: bool) -> dict[str, str]:
    names = list(spec.names)
    if permuted:
        names = names[1:] + names[:1]
    return dict(zip(roles_for(spec.construction, spec.distractor), names))


@dataclass(frozen=True)
class Instance3:
    instance_id: str
    group_id: str
    stratum: int
    construction: str
    distractor: str
    variant: Variant3
    roles: tuple[tuple[str, str], ...]
    scenario: Scenario
    hidden: Params  # PRIVILEGED: sampled once per group, shared by its variants
    spec: PublicSpec = field(compare=False)

    @property
    def role(self) -> dict[str, str]:
        return dict(self.roles)


def make_scenario(spec: PublicSpec, v: Variant3) -> tuple[Scenario, dict]:
    n = role_names(spec, v.permuted)
    prior = prior_of(spec, n)
    iid = f"{spec.group_id}-{v.tag}"
    return Scenario(iid, f"Deliver the package to {n['R'].capitalize()}.", PURPOSE[spec.construction], prior,
                    lambda prm, n=n: build_world(spec, n, v.stakes, prm)), n


def sample_hidden(spec: PublicSpec, prior, seed: int = BASE_SEED) -> Params:
    rng = random.Random(f"{seed}:{DEV_VERSION}:hidden:{spec.construction}")
    params, weights = zip(*prior)
    return rng.choices(params, weights=weights, k=1)[0]


def generate(seed: int = BASE_SEED) -> list[Instance3]:
    out = []
    for stratum, cons in CONSTRUCTIONS.items():
        for g in range(len(cons)):
            spec = draw_spec(stratum, g, seed)
            made = [(v, *make_scenario(spec, v)) for v in VARIANTS]
            # the prior depends only on the public spec: identical across variants up to role names
            hidden = sample_hidden(spec, made[0][1].prior, seed)
            assert all(sc.prior == made[0][1].prior for _, sc, _ in made), spec.group_id
            out += [Instance3(sc.id, spec.group_id, stratum, spec.construction, spec.distractor, v,
                              tuple(sorted(n.items())), sc, hidden, spec) for v, sc, n in made]
    return out


def access_status(world: World, u) -> str:
    """Evidence-resolution label of a unit in one world: no belief / correct now / incorrect now (the unit's
    face-value default: a K belief matches the truth; a K(j->k) view matches k's actual belief)."""
    from vomi.units import content, default_holds
    if content(world, u)[0] == "unknown":
        return "no_belief"
    return "correct" if default_holds(world, u) else "incorrect"


def focal_units(inst: Instance3):
    """Fixed allocation for Round B (experiment-plan Entry 1, A.2), from the construction only."""
    from vomi.units import K, R as Rel  # local import: officeminds must not depend on vomi at import time
    n, c = inst.role, inst.construction
    if inst.stratum == 1:
        return [K(n[r]) for r in roles_for(c, inst.distractor)[1:]]
    if c in ("2a", "2c"):
        return [K(n["H"]), K(n["N"])]
    if c == "2b":
        return [K(n["N"])]
    if inst.stratum == 3:
        return [K(n["F"], n["R"])]
    if c == "4a":
        return [K(n["W"])]
    if c == "4b":
        return [Rel(n["X"]), Rel(n["Y"])]
    if c == "4c":
        return [Rel(n["X"])]
    raise ValueError(c)


def registry(seed: int = BASE_SEED) -> dict:
    return {i.instance_id: (lambda s=i.scenario: s) for i in generate(seed)}
