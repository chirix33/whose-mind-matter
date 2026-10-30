"""Hybrid block (D-019): provenance index, referent-based joint relation engine, relation cache, decision interface.

Information boundary. Every function here reads only:
  - the robot-visible history (VisibleHistory: its observations, dev-v3 notices, answers and its own actions), and
  - the public task structure: WorldConfig (layout, roster, handoff routes, stakes, horizon) and a structured
    public model (PublicModelSpec), the disclosed task-card model in machine-readable form.
It never reads a World, a PersonMind, hidden parameters, evaluator values or generator metadata.

Representation (CONCEPT.md R1/R2, with the review's corrections):
  - a person's belief about a fact is a TERM: const(v) (heard publicly), latent(name) (a value the robot did not hear,
    e.g. the content of a quiet conversation), expr(...) (a public-model function of latents), or unknown (no belief);
    every term carries the visible event IDs it came from (provenance);
  - latent variables have the public model's (possibly conditional) prior; shared referents are SHARED latents, so
    joint relations are exact by enumeration, never a product of marginals; the product is computed only as a contrast;
  - observed answers are EVIDENCE constraints: they change the robot's estimate, never a person's term;
  - an inconsistent constraint is reported (zero mass), never forced into a confident equality.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from fractions import Fraction

from officeminds.episode import VisibleHistory
from officeminds.world import WorldConfig

UNKNOWN = "unknown"
_ANN = re.compile(r'^(\w+) announces to everyone present: "(\w+) = (\w+)"$')
_STAT = re.compile(r'^(\w+) says: "(\w+) = (\w+)"$')
_QUIET = re.compile(r"^(\w+) talks quietly to (\w+);")
_LEAVE = re.compile(r"^(\w+) leaves the lobby( and the building)?$")
_ARRIVE = re.compile(r"^(\w+) arrives in the lobby$")
_ANSWER = re.compile(r"^(\w+) = (\w+)$")


# ----------------------------------------------------------------------------- provenance index
@dataclass(frozen=True)
class VEvent:
    id: str  # the ledger's citable evidence ID (t{t}:note{i} / t{t}:said{i})
    t: int
    kind: str  # announce | quiet | statement | remark | leave | arrive | answer
    actor: str
    listener: str = ""
    fact: str = ""
    value: str = ""  # "" when the robot did not hear it (quiet)
    hearers: frozenset = frozenset()  # people (not the robot) who heard the content
    witnesses: frozenset = frozenset()  # people who saw it happen (incl. hearers)
    building: bool = False

    @property
    def changes_person_state(self) -> bool:
        return self.kind in ("announce", "quiet")  # answers/statements only update listeners' views of the speaker


@dataclass
class ProvenanceIndex:
    events: list[VEvent] = field(default_factory=list)
    robot_rooms: list[str] = field(default_factory=list)  # robot room at each observation t
    present: list[tuple] = field(default_factory=list)  # people present at each observation t
    positions: dict = field(default_factory=dict)  # last visible position per person: lobby | away | gone

    @classmethod
    def build(cls, hist: VisibleHistory) -> "ProvenanceIndex":
        idx = cls()
        for _, o in hist.steps:
            idx.add_observation(o)
        return idx

    def add_observation(self, o) -> None:
        self.robot_rooms.append(o.room)
        self.present.append(tuple(o.people_present))
        for i, (kind, actor, line, others) in enumerate(o.notices):
            eid = f"t{o.t}:note{i}"
            seen = frozenset(others) | {actor}
            if kind == "announce" and (m := _ANN.match(line)):
                self.events.append(VEvent(eid, o.t, kind, actor, "", m[2], m[3], seen, seen))
            elif kind == "statement" and (m := _STAT.match(line)):
                self.events.append(VEvent(eid, o.t, kind, actor, "", m[2], m[3], seen, seen))
            elif kind == "quiet" and (m := _QUIET.match(line)):
                self.events.append(VEvent(eid, o.t, kind, actor, m[2], "", "", frozenset({actor, m[2]}),
                                          seen | {m[2]}))
            elif kind == "leave" and (m := _LEAVE.match(line)):
                self.events.append(VEvent(eid, o.t, kind, actor, witnesses=seen, building=bool(m[2])))
                self.positions[actor] = "gone" if m[2] else "away"
            elif kind == "arrive" and _ARRIVE.match(line):
                self.events.append(VEvent(eid, o.t, kind, actor, witnesses=seen))
                self.positions[actor] = "lobby"
            elif kind == "remark":
                self.events.append(VEvent(eid, o.t, kind, actor, witnesses=seen))
            else:
                raise ValueError(f"unparsed notice: {kind!r} {line!r}")
        for i, (speaker, text) in enumerate(o.utterances):
            m = _ANSWER.match(text)
            hearers = frozenset(o.people_present)
            self.events.append(VEvent(f"t{o.t}:said{i}", o.t, "answer", speaker, "", m[1] if m else "",
                                      m[2] if m else UNKNOWN, hearers, hearers))
        for p in o.people_present:
            self.positions[p] = "lobby" if o.room == "lobby" else o.room

    def watched_lobby_at(self, t: int) -> bool:
        return t < len(self.robot_rooms) and self.robot_rooms[t] == "lobby"


# ----------------------------------------------------------------------------- terms
Term = tuple  # ("const", v) | ("latent", name) | ("expr", label, fn, deps) | ("unknown",)
CONST = lambda v: ("const", v)  # noqa: E731
LATENT = lambda n: ("latent", n)  # noqa: E731
UNK = ("unknown",)


def term_value(term: Term, assign: dict) -> str:
    k = term[0]
    if k == "const":
        return term[1]
    if k == "latent":
        return assign[term[1]]
    if k == "expr":
        return term[2](assign)
    return UNKNOWN


def term_label(term: Term) -> str:
    return {"const": lambda t: t[1], "latent": lambda t: f"<{t[1]}>", "expr": lambda t: t[1],
            "unknown": lambda t: "unknown"}[term[0]](term)


# ----------------------------------------------------------------------------- structured public models
def _uniform(vals) -> list:
    vals = list(vals)
    return [(v, Fraction(1, len(vals))) for v in vals]


class PublicModelSpec:
    """Structured form of a construction's disclosed public model (hand-compiled once per template; see cpu-gate).
    Subclasses define: query fact, which latent each quiet conversation carries, the ordered latent prior, and the
    recipient's location term."""
    family = "base"

    def __init__(self, cfg: WorldConfig):
        self.cfg = cfg
        self.R = cfg.recipient
        self.fact = cfg.query_facts[0]
        self.offices = tuple(cfg.offices)

    def quiet_fact(self, ev: VEvent) -> str:
        return self.fact

    def quiet_latent(self, k: int, ev: VEvent) -> str:
        return f"Q{k}"

    def latents(self, eng) -> list:
        raise NotImplementedError

    def recipient_loc(self, eng) -> Term:
        raise NotImplementedError

    def adjust(self, eng) -> None:
        """Hook for possible unobserved events allowed by the public model."""

    def constraints(self, eng) -> list:
        return []

    def may_change_unobserved(self, idx: ProvenanceIndex, t_from: int, t_to: int) -> bool:
        return False


class Meeting3(PublicModelSpec):
    """dev-v3 3a/3b/3c: A announced meeting office a, changed it to b (uniform over the two others) and told it only in
    the quiet conversations shown; every quiet conversation by A or F tells the CURRENT office (one shared latent b);
    R goes to where R believes the meeting is; F routes by what F thinks R believes."""
    family = "meeting3"

    def quiet_latent(self, k, ev):
        return "b"

    def latents(self, eng):
        a = eng.announced(self.fact)
        return [("b", lambda s, a=a: _uniform(o for o in self.offices if o != a))]

    def recipient_loc(self, eng):
        return eng.belief(self.R, self.fact)


class Moves2(PublicModelSpec):
    """2d: R announced a; each quiet conversation by R tells the office R is about to go to; the first move is uniform
    over the two offices other than a; the second goes to the remaining office (neither a nor the first)."""
    family = "moves2"

    def latents(self, eng):
        a = eng.announced(self.fact)
        out = [("Q1", lambda s, a=a: _uniform(o for o in self.offices if o != a))]
        if eng.n_quiet >= 2:
            out.append(("Q2", lambda s, a=a: [(next(o for o in self.offices if o not in (a, s["Q1"])), Fraction(1))]))
        return out

    def recipient_loc(self, eng):
        if self.R in eng.idx.present[-1]:
            return CONST(eng.idx.robot_rooms[-1])
        return LATENT(f"Q{eng.n_quiet}") if eng.n_quiet else CONST(eng.announced(self.fact))


class Plan2e(PublicModelSpec):
    """2e / stop cases: R's quiet conversation tells the addressee R's planned office (uniform over the two offices other
    than a); R keeps the plan with probability 3/4, otherwise goes to the remaining office. stop_visible: R is back in
    the lobby; stop_announced: R then announced the final office to everyone and went there."""
    family = "plan2e"

    def latents(self, eng):
        a = eng.announced(self.fact)
        return [("Q1", lambda s, a=a: _uniform(o for o in self.offices if o != a)),
                ("kept", lambda s: [("yes", Fraction(3, 4)), ("no", Fraction(1, 4))])]

    def _final(self, eng):
        a = eng.announced(self.fact)
        return ("expr", "final(Q1,kept)",
                lambda s, a=a: s["Q1"] if s["kept"] == "yes" else next(o for o in self.offices if o not in (a, s["Q1"])),
                ("Q1", "kept"))

    def recipient_loc(self, eng):
        if self.R in eng.idx.present[-1]:
            return CONST(eng.idx.robot_rooms[-1])
        anns = [e for e in eng.idx.events if e.kind == "announce" and e.actor == self.R]
        if len(anns) >= 2:
            return CONST(anns[-1].value)
        return self._final(eng)

    def constraints(self, eng):
        anns = [e for e in eng.idx.events if e.kind == "announce" and e.actor == self.R]
        return [(self._final(eng), anns[-1].value, anns[-1].id)] if len(anns) >= 2 else []


class Seq4(PublicModelSpec):
    """F4 seq: R announced a, told N quietly its next office Q1 (uniform over the two others) and moved there; N stepped
    out and returns at step 2. With probability 1/2, at step 1 R comes back to the lobby, tells H quietly its next office
    Q2 (uniform over the two offices other than Q1) and moves there; this is visible only from the lobby."""
    family = "seq4"
    RETURN_STEP = 1

    def latents(self, eng):
        a = eng.announced(self.fact)
        out = [("Q1", lambda s, a=a: _uniform(o for o in self.offices if o != a))]
        if eng.n_quiet >= 2 or not self._observed(eng):
            out.append(("Q2", lambda s: _uniform(o for o in self.offices if o != s["Q1"])))
        if not self._observed(eng):
            out.append(("ret", lambda s: [("yes", Fraction(1, 2)), ("no", Fraction(1, 2))]))
        return out

    def _observed(self, eng) -> bool:
        return len(eng.idx.robot_rooms) <= self.RETURN_STEP or eng.idx.watched_lobby_at(self.RETURN_STEP)

    def adjust(self, eng):
        if self._observed(eng) or len(eng.idx.robot_rooms) <= self.RETURN_STEP:
            return
        H = next(p for p in self.cfg.handoff_routes if p != self._n(eng))
        before = eng.beliefs.get((H, self.fact), (UNK, ()))
        eng.beliefs[(H, self.fact)] = (("expr", f"ret?<Q2>:{term_label(before[0])}",
                                        lambda s, b=before[0]: s["Q2"] if s["ret"] == "yes" else term_value(b, s),
                                        ("ret", "Q2")), before[1] + ("unobserved:t1",))

    def _n(self, eng):
        q = next(e for e in eng.idx.events if e.kind == "quiet")
        return q.listener

    def recipient_loc(self, eng):
        if self.R in eng.idx.present[-1]:
            return CONST(eng.idx.robot_rooms[-1])
        if not self._observed(eng):
            return ("expr", "ret?<Q2>:<Q1>", lambda s: s["Q2"] if s["ret"] == "yes" else s["Q1"], ("ret", "Q1", "Q2"))
        return LATENT(f"Q{eng.n_quiet}")

    def may_change_unobserved(self, idx, t_from, t_to):
        return any(t_from < t <= t_to and t == self.RETURN_STEP and not idx.watched_lobby_at(t)
                   for t in range(t_from + 1, t_to + 1))


SPECS = {"3a": Meeting3, "3b": Meeting3, "3c": Meeting3, "2d": Moves2, "2e": Plan2e, "stop_visible": Plan2e,
         "stop_announced": Plan2e, "seq": Seq4}


# ----------------------------------------------------------------------------- referent engine
class ReferentEngine:
    """Compiles the index under r6 belief rules into terms; answers joint queries by exact enumeration of latents."""

    def __init__(self, pm: PublicModelSpec, idx: ProvenanceIndex):
        self.pm, self.idx, self.cfg = pm, idx, pm.cfg
        self.beliefs: dict = {}  # (person, fact) -> (term, provenance ids)
        self.nested: dict = {}  # (person, other, fact) -> (term, provenance ids)
        self.evidence: list = []  # (term, observed value, evidence id): robot-estimate updates only
        self.n_quiet = 0
        for ev in idx.events:
            self._apply(ev)
        pm.adjust(self)
        self._joint = None

    # -- compilation (r6 rules 1, 3, 5)
    def _apply(self, ev: VEvent) -> None:
        if ev.kind == "announce":
            for p in ev.hearers:
                self.beliefs[(p, ev.fact)] = (CONST(ev.value), (ev.id,))
                if p != ev.actor:
                    self.nested[(p, ev.actor, ev.fact)] = (CONST(ev.value), (ev.id,))
                    self.nested[(ev.actor, p, ev.fact)] = (CONST(ev.value), (ev.id,))
        elif ev.kind == "quiet":
            self.n_quiet += 1
            f = self.pm.quiet_fact(ev)
            t = LATENT(self.pm.quiet_latent(self.n_quiet, ev))
            for p in (ev.actor, ev.listener):
                self.beliefs[(p, f)] = (t, (ev.id,))
            self.nested[(ev.listener, ev.actor, f)] = (t, (ev.id,))
            self.nested[(ev.actor, ev.listener, f)] = (t, (ev.id,))
        elif ev.kind in ("statement", "answer"):
            for p in ev.hearers - {ev.actor}:
                self.nested[(p, ev.actor, ev.fact)] = (CONST(ev.value), (ev.id,))
            if ev.kind == "answer" and ev.fact:  # cooperative public model: the answer reports the speaker's own belief
                self.evidence.append((self.belief(ev.actor, ev.fact), ev.value, ev.id))
            elif ev.kind == "answer":
                self.evidence.append(("unknown-answer", ev.actor, ev.id))

    def announced(self, fact: str) -> str:
        """The FIRST public announcement of `fact` (the public models' reference value a)."""
        anns = [e for e in self.idx.events if e.kind == "announce" and e.fact == fact]
        return anns[0].value if anns else ""

    def belief(self, p: str, fact: str) -> Term:
        return self.beliefs.get((p, fact), (UNK, ()))[0]

    def nested_belief(self, p: str, other: str, fact: str) -> Term:
        return self.nested.get((p, other, fact), (UNK, ()))[0]

    def provenance(self, p: str, fact: str, other: str = "") -> tuple:
        rec = self.nested.get((p, other, fact)) if other else self.beliefs.get((p, fact))
        return rec[1] if rec else ()

    def route(self, courier: str) -> Term:
        other, fact = self.cfg.handoff_routes[courier]
        return self.nested_belief(courier, other, fact) if other else self.belief(courier, fact)

    # -- exact joint over latents
    def joint(self) -> list[tuple[dict, Fraction]]:
        if self._joint is None:
            rows = [({}, Fraction(1))]
            for name, dist in self.pm.latents(self):
                rows = [({**s, name: v}, w * pv) for s, w in rows for v, pv in dist(s) if pv > 0]
            cons = self.pm.constraints(self)
            keep = []
            for s, w in rows:
                ok = all(term_value(t, s) == v for t, v, _ in cons)
                for e in self.evidence:
                    if e[0] == "unknown-answer":
                        continue  # an "I don't know" answer is checked separately (see inconsistent())
                    ok = ok and term_value(e[0], s) == e[1]
                if ok:
                    keep.append((s, w))
            total = sum(w for _, w in keep)
            self._joint = [(s, w / total) for s, w in keep] if total else []
        return self._joint

    def inconsistent(self) -> list[str]:
        """Evidence the public model gives zero probability (exposed, never forced into a confident answer)."""
        out = [] if self.joint() else ["joint: zero mass"]
        for e in self.evidence:
            if e[0] == "unknown-answer" and self.belief(e[1], self.fact)[0] != "unknown":
                out.append(f"{e[2]}: {e[1]} said 'I don't know' but holds a belief under the public model")
        return out

    def dist(self, term: Term) -> dict[str, Fraction]:
        out: dict[str, Fraction] = {}
        for s, w in self.joint():
            v = term_value(term, s)
            out[v] = out.get(v, Fraction(0)) + w
        return out

    def p_equal(self, t1: Term, t2: Term) -> Fraction:
        return sum((w for s, w in self.joint() if term_value(t1, s) == term_value(t2, s) != UNKNOWN), Fraction(0))

    def p_equal_product(self, t1: Term, t2: Term) -> Fraction:
        """CONTRAST ONLY: the independence reading of the two marginals (what marginal-only notes imply)."""
        d1, d2 = self.dist(t1), self.dist(t2)
        return sum((p * d2.get(v, 0) for v, p in d1.items() if v != UNKNOWN), Fraction(0))

    def frechet(self, t1: Term, t2: Term) -> tuple[Fraction, Fraction]:
        """Bounds on P(equal) from the marginals alone (any coupling)."""
        d1, d2 = self.dist(t1), self.dist(t2)
        vals = [v for v in d1 if v != UNKNOWN]
        hi = sum((min(d1[v], d2.get(v, 0)) for v in vals), Fraction(0))
        lo = max([Fraction(0)] + [d1[v] + d2.get(v, 0) - 1 for v in vals])
        return lo, hi


def engine_for(construction: str, cfg: WorldConfig, hist: VisibleHistory) -> ReferentEngine:
    return ReferentEngine(SPECS[construction](cfg), ProvenanceIndex.build(hist))


# ----------------------------------------------------------------------------- relation cache (reuse / refresh)
@dataclass
class RelationRecord:
    courier: str
    p: Fraction  # P(route(courier) == recipient location | h)
    route_term: str
    loc_term: str
    provenance: tuple
    computed_t: int
    n_events: int  # index length when computed
    deps: frozenset


class RelationCache:
    """Reuse a relation until a visible event touches one of its people, or the public model allows an unobserved change
    while the robot was not watching. Mere sightings of unrelated people do not invalidate."""

    def __init__(self):
        self.records: dict[str, RelationRecord] = {}
        self.log: list[dict] = []

    def status(self, courier: str, idx: ProvenanceIndex, pm: PublicModelSpec) -> str:
        r = self.records.get(courier)
        if r is None:
            return "not_computed"
        new = idx.events[r.n_events:]
        # a person's state changes only through what they hear (announce / quiet) or, for the recipient, by moving;
        # an arrival or departure of a courier, a remark or a third person's sighting changes no dependency
        if any(e.changes_person_state and (e.hearers & r.deps or e.actor in r.deps) for e in new) or \
                any(e.kind in ("leave", "arrive") and e.actor == pm.R for e in new):
            return "stale_person_state"
        if any(e.kind == "answer" for e in new):  # changes only the robot's estimate (evidence on shared latents)
            return "stale_estimate"
        if pm.may_change_unobserved(idx, r.computed_t, len(idx.robot_rooms) - 1):
            return "stale_unobserved"
        return "fresh"

    def get(self, courier: str, eng: ReferentEngine) -> tuple[RelationRecord, str]:
        st = self.status(courier, eng.idx, eng.pm)
        if st == "fresh":
            self.log.append({"t": len(eng.idx.robot_rooms) - 1, "courier": courier, "op": "reuse"})
            return self.records[courier], "reuse"
        rt, lt = eng.route(courier), eng.pm.recipient_loc(eng)
        other, fact = eng.cfg.handoff_routes[courier]
        prov = eng.provenance(courier, fact, other)
        rec = RelationRecord(courier, eng.p_equal(rt, lt), term_label(rt), term_label(lt), tuple(prov),
                             len(eng.idx.robot_rooms) - 1, len(eng.idx.events), frozenset({courier, eng.pm.R}))
        op = "compute" if st == "not_computed" else "refresh"
        self.records[courier] = rec
        self.log.append({"t": rec.computed_t, "courier": courier, "op": op, "reason": st, "p": str(rec.p)})
        return rec, op


# ----------------------------------------------------------------------------- decision interface
STEP = 0.05


def j_commit(p: float, stakes: float) -> float:
    """Immediate expected return of a one-step terminal commitment with success probability p."""
    return -STEP + p - (1 - p) * 0.5 * stakes


def _dist_to(room: str, office: str) -> int:
    if room == office:
        return 0
    return 1 if room == "hall" else 2  # lobby -> hall -> office; office -> hall -> office


def search_value(loc: dict, room: str, remaining: int, offices, excluded=()) -> float:
    """Declared feasible alternative: search the offices in person in descending probability (ties: config order),
    deliver on sight; exact expected return under `loc` within the remaining steps (timeouts carry no penalty)."""
    cand = [o for o in offices if o not in excluded]
    order = sorted(cand, key=lambda o: (-float(loc.get(o, 0)), offices.index(o)))
    total, steps, here = 0.0, 0, room
    covered = 0.0
    for o in order:
        steps += _dist_to(here, o)
        here = o
        p = float(loc.get(o, 0))
        if steps + 1 <= remaining:
            total += p * (1 - STEP * (steps + 1))
        else:
            total += p * (-STEP * remaining)
        covered += p
    return total + (1 - covered) * (-STEP * remaining)


@dataclass
class GateVerdict:
    action: str
    p: float
    j_commit: float
    v_alt: float
    allow: bool
    source: str


def gate(action: str, p: float, loc: dict, room: str, remaining: int, cfg: WorldConfig, excluded=(),
         source: str = "") -> GateVerdict:
    v_alt = search_value(loc, room, remaining, tuple(cfg.offices), excluded)
    j = j_commit(p, cfg.stakes)
    return GateVerdict(action, p, j, v_alt, j >= v_alt, source)
