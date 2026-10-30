"""Hybrid block (D-019) qualification families: minimally changed dev-v3 constructions, CPU qualification only.

DEVELOPMENT DATA ONLY. These cases use the dev-v3 event semantics (world.Event, devgen3._Script notices, rules r6). The
only changes are the hidden-variable supports and the event orders listed per construction. Nothing here is shown to an
LLM in this block. Purpose (privileged documentation):

  F1 certain_wrong   3b  F's route is certain (R's public statement) but R was updated quietly: give(F) always fails
                     3c  correct-handoff control: same certain route, R not updated: give(F) always succeeds
                     3a  aligned control: F told R; route and R's office both uncertain but equal
  F2 uncertain_aligned
                     2d  two couriers with IDENTICAL destination marginals (uniform over the two non-announced offices)
                         and identical recipient marginal; H heard the first move, N the second: N always right, H always wrong
                     2e  uncertain shared provenance: H heard R's plan, R keeps it with probability 3/4; N only heard the
                         announcement (certain, never right)
  F3 stop            stop_visible    2e prologue, then R comes back to the lobby: deliver() is certain; relations idle
                     stop_announced  2e prologue, then R announces the final office to everyone: drop() is certain
  F4 reuse_refresh   seq  N heard R's move then stepped out; N returns at step 2. With probability 1/2, R comes back at
                          step 1, tells H the next office quietly and moves there (seen only from the lobby).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction

from .devgen3 import NAME_POOL, OFFICE_POOL, PublicSpec, _others, _Script, build_world
from .scenarios import Scenario, grid
from .world import PersonMind, World, WorldConfig

HORIZON = 8
FAMILIES = {"F1_certain_wrong": ("3b", "3c", "3a"), "F2_uncertain_aligned": ("2d", "2e"),
            "F3_stop": ("stop_visible", "stop_announced"), "F4_reuse_refresh": ("seq",)}
ROLES = {"3a": ("R", "A", "F"), "3b": ("R", "A", "F"), "3c": ("R", "A", "F"), "2d": ("R", "H", "N"),
         "2e": ("R", "H", "N"), "stop_visible": ("R", "H", "N"), "stop_announced": ("R", "H", "N"),
         "seq": ("R", "H", "N", "D")}
HALF = (("0", Fraction(1, 2)), ("1", Fraction(1, 2)))
KEEP = Fraction(3, 4)


@dataclass(frozen=True)
class FamilyCase:
    case_id: str
    family: str
    construction: str
    seed: int
    names: dict
    offices: tuple
    stakes: float
    scenario: Scenario  # public prior (disclosed) + builder
    hidden: tuple  # PRIVILEGED: one draw for this case


def _domains(c: str, offices) -> dict:
    a = {o: Fraction(1, 3) for o in offices}
    if c.startswith("3") or c == "2d":
        return {"a": a, "m1": dict(HALF)}
    if c in ("2e", "stop_visible", "stop_announced"):
        return {"a": a, "m1": dict(HALF), "kept": {"yes": KEEP, "no": 1 - KEEP}}
    if c == "seq":
        return {"a": a, "m1": dict(HALF), "m2": dict(HALF), "ret": {"yes": Fraction(1, 2), "no": Fraction(1, 2)}}
    raise ValueError(c)


def _third(offices, x, y):
    return next(o for o in offices if o not in (x, y))


def build(c: str, n: dict, offices, stakes: float, p: dict) -> World:
    if c.startswith("3"):
        spec = PublicSpec(f"hyb-{c}", 3, c, "none", tuple(n[r] for r in ROLES[c]), tuple(offices))
        return build_world(spec, n, stakes, p)
    R, H, N = n["R"], n["H"], n["N"]
    lf, a = f"{R}_loc", p["a"]
    s = _Script()
    people = [n[r] for r in ROLES[c]]
    rooms = {x: "lobby" for x in people}
    timed = []
    s.announce(R, lf, a)
    s.leave(R, a)
    s.self_sees(R, lf, a)
    m1 = _others(offices, a)[int(p["m1"])]
    s.arrive(R)
    if c == "seq":
        s.quiet(R, N, lf, m1)
        s.leave(R, m1)
        s.self_sees(R, lf, m1)
        s._add("enter", "outside", N, visible=("leave", f"{N} leaves the lobby"))
        if p["ret"] == "yes":  # step 1: R returns, tells H quietly, moves on (visible only from the lobby)
            m2 = _others(offices, m1)[int(p["m2"])]
            s._add("enter", "lobby", R, visible=("arrive", f"{R} arrives in the lobby"), t=1)
            s._add("tell", "lobby", R, lf, m2, present=(R, H), t=1,
                   visible=("quiet", f"{R} talks quietly to {H}; only {H} can hear it, and the robot cannot hear what is said"))
            s._add("enter", m2, R, visible=("leave", f"{R} leaves the lobby"), t=1)
            s._add("witness", m2, R, lf, m2, present=(R,), t=1)
        s._add("say", "lobby", n["D"], visible=("remark", f'{n["D"]} says: "Morning."'), t=1)  # irrelevant event, both draws
        s._add("enter", "lobby", N, visible=("arrive", f"{N} arrives in the lobby"), t=2)
    elif c == "2d":
        s.quiet(R, H, lf, m1)
        s.leave(R, m1)
        s.self_sees(R, lf, m1)
        m2 = _third(offices, a, m1)
        s.arrive(R)
        s.quiet(R, N, lf, m2)
        s.leave(R, m2)
        s.self_sees(R, lf, m2)
    else:  # 2e and the stop cases share the 2e prologue
        final = m1 if p["kept"] == "yes" else _third(offices, a, m1)
        s.quiet(R, H, lf, m1)
        s.leave(R, final)
        s.self_sees(R, lf, final)
        if c == "stop_visible":
            s.arrive(R)
        elif c == "stop_announced":
            s.arrive(R)
            s.announce(R, lf, final)
            s.leave(R, final)
    events = tuple(s.events)
    cfg = WorldConfig(adjacency={"lobby": ("hall",), "hall": ("lobby", *offices), **{x: ("hall",) for x in offices}},
                      offices=tuple(offices), chute_room="lobby", recipient=R, roster=tuple(sorted(people)),
                      query_facts=(lf,), fact_domains={lf: tuple(offices)},
                      handoff_routes={H: ("", lf), N: ("", lf)}, stakes=stakes, horizon=HORIZON)
    return World(cfg, "lobby", rooms, {x: PersonMind() for x in people}, (), events, {})


def cases(seed: int, stakes_levels=(1.0, 4.0)) -> list[FamilyCase]:
    out = []
    for fam, cons in FAMILIES.items():
        for c in cons:
            rng = random.Random(f"{seed}:hybrid-fam:public:{c}")
            names = dict(zip(ROLES[c], rng.sample(NAME_POOL, len(ROLES[c]))))
            offices = list(OFFICE_POOL[rng.randrange(len(OFFICE_POOL))])
            rng.shuffle(offices)
            prior = grid({k: {v: float(w) for v, w in d.items()} for k, d in _domains(c, offices).items()})
            hrng = random.Random(f"{seed}:hybrid-fam:hidden:{c}")
            params, weights = zip(*prior)
            hidden = hrng.choices(params, weights=weights, k=1)[0]
            for st in stakes_levels:
                sc = Scenario(f"hyb-{c}-s{seed}-x{st:g}", f"Deliver the package to {names['R'].capitalize()}.",
                              fam, prior, lambda prm, c=c, n=names, o=tuple(offices), st=st: build(c, n, o, st, prm))
                out.append(FamilyCase(sc.id, fam, c, seed, names, tuple(offices), st, sc, hidden))
    return out
