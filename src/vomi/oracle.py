"""Exact symbolic-oracle VoMI for finite Tier 1 hypothesis sets (implementation-spec §4).

Label type: EXACT SYMBOLIC-ORACLE VoMI. Every quantity below is computed by exhaustive
enumeration of (a) the hidden worlds consistent with the robot-visible history and
(b) the robot's belief-space expectimax under the finite horizon. No sampling.

Definitions (all conditioned on the visible history h):
  b_h(w)          prior restricted to worlds that replay h exactly, renormalized.
  b_{S,w}         b_h further conditioned on unit contents c_S(w') == c_S(w).
  a_S(w)          argmax_a Q(b_{S,w}, a); ties broken by canonical action order.
  Q(b, a)         sum_w b(w) [r_w(a) + V*(b')], V* = belief-optimal finite-horizon value.
  R_w(a, b)       realized return in true world w of taking a, then following the
                  belief-optimal policy whose belief starts at b and is updated by observations.
  J(S)            sum_w b_h(w) R_w(a_S(w), b_cont), b_cont = b_{S,w} ("retain", default)
                  or b_h ("drop": the continuation forgets S's content).
  VoMI(u | S)     J(S + u) - J(S) - lambda * c(u).

These are values of an observation-limited Bayes-optimal agent, not of a fully informed
state oracle; the full-information value is reported separately as a privileged bound.
"""

from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass, field

from officeminds.episode import VisibleHistory
from officeminds.scenarios import Scenario
from officeminds.world import Action, Observation, World, WorldConfig, legal_actions

from .units import Unit, content

Items = tuple[tuple[float, World], ...]


def _normalize(items) -> Items:
    total = sum(w for w, _ in items)
    return tuple((w / total, x) for w, x in items)


def _obs_key(o: Observation) -> str:
    return json.dumps(o.to_dict(), sort_keys=True)


@dataclass
class AllocationEval:
    value: float
    actions: list[Action]  # a_S(w) per hypothesis world (same order as oracle.worlds)
    returns: list[float]  # R_w(a_S(w), b_cont) per world


@dataclass
class UnitReport:
    unit: str
    delta_j: float  # J(S+u) - J(S)
    vomi: float  # delta_j - lambda * cost
    p_flip: float
    dq_given_flip: float  # E[R(a_{S+u}) - R(a_S) | flip]; 0 if no flip
    no_flip_residual: float  # delta_j - p_flip * dq_given_flip (nonzero => outline §3.4 decomposition fails)
    content_entropy_bits: float  # H(c_u | c_S) under b_h (AutoToM-style target, D1)


@dataclass
class AllocationLabels:
    units: list[str]
    j_full: float
    j_empty: float
    minimal_sufficient: list[list[str]]
    minimum_cost_sufficient: list[list[str]]
    loo_necessary: list[str]  # J(U - u) < J(U)
    loo_action_changing: list[str]  # removing u from U changes a_U(w) in some world
    subset_values: dict[str, float] = field(default_factory=dict)


class ExactOracle:
    def __init__(self, scenario: Scenario, hist: VisibleHistory, tol: float = 1e-9):
        self.config: WorldConfig = scenario.config
        self.tol = tol
        target = [_obs_key(o) for _, o in hist.steps]
        kept = []
        for params, weight in scenario.prior:
            world = scenario.build(params)
            keys = [_obs_key(world.reset())]
            for a in hist.actions:
                if world.done:
                    break
                keys.append(_obs_key(world.step(a)))
            if keys == target:
                kept.append((weight, world, params))
        if not kept:
            raise ValueError("visible history is inconsistent with every hypothesis world")
        self.params = [p for _, _, p in kept]
        self.belief: Items = _normalize([(w, x) for w, x, _ in kept])
        self.worlds = [x for _, x in self.belief]
        self.obs = hist.last
        self._v: dict = {}
        self._alloc: dict = {}

    # ------------------------------------------------------------ belief-space expectimax
    def _key(self, items: Items) -> tuple:
        return tuple(sorted((round(w, 12), x.signature()) for w, x in items))

    def _transition(self, items: Items, a: Action) -> dict[str, tuple[Observation, list]]:
        groups: dict[str, tuple[Observation, list]] = {}
        for w, x in items:
            nx = x.clone()
            o = nx.step(a)
            groups.setdefault(_obs_key(o), (o, []))[1].append((w, nx))
        return groups

    def value(self, items: Items, obs: Observation) -> float:
        if obs.done:
            return 0.0
        key = self._key(items)
        if key not in self._v:
            self._v[key] = max(self.q(items, obs, a) for a in legal_actions(self.config, obs))
        return self._v[key]

    def q(self, items: Items, obs: Observation, a: Action) -> float:
        total = 0.0
        for o2, members in self._transition(items, a).values():
            pw = sum(w for w, _ in members)
            total += pw * (o2.reward + self.value(_normalize(members), o2))
        return total

    def best_action(self, items: Items, obs: Observation) -> Action:
        best, best_q = None, -math.inf
        for a in legal_actions(self.config, obs):  # canonical order => deterministic ties
            qa = self.q(items, obs, a)
            if qa > best_q + self.tol:
                best, best_q = a, qa
        return best

    def realized_return(self, world: World, items: Items, obs: Observation, first: Action) -> float:
        w = world.clone()
        o = w.step(first)
        total = o.reward
        b = _normalize(self._transition(items, first)[_obs_key(o)][1])
        while not o.done:
            a = self.best_action(b, o)
            o = w.step(a)
            total += o.reward
            b = _normalize(self._transition(b, a)[_obs_key(o)][1])
        return total

    # ------------------------------------------------------------ allocations and VoMI
    def contents(self, world: World, S) -> tuple:
        return tuple(content(world, u) for u in sorted(S))

    def condition(self, world: World, S) -> Items:
        c = self.contents(world, S)
        return _normalize([(w, x) for w, x in self.belief if self.contents(x, S) == c])

    def evaluate(self, S=frozenset(), continuation: str = "retain") -> AllocationEval:
        key = (frozenset(S), continuation)
        if key not in self._alloc:
            actions, returns, total = [], [], 0.0
            for p, w in self.belief:
                bS = self.condition(w, S)
                a = self.best_action(bS, self.obs)
                cont = bS if continuation == "retain" else self.belief
                r = self.realized_return(w, cont, self.obs, a)
                actions.append(a)
                returns.append(r)
                total += p * r
            self._alloc[key] = AllocationEval(total, actions, returns)
        return self._alloc[key]

    def entropy(self, u: Unit, S=frozenset()) -> float:
        """H(c_u | c_S) in bits under b_h."""
        h = 0.0
        groups: dict[tuple, dict[tuple, float]] = {}
        for p, w in self.belief:
            g = groups.setdefault(self.contents(w, S), {})
            g[content(w, u)] = g.get(content(w, u), 0.0) + p
        for g in groups.values():
            mass = sum(g.values())
            h -= sum(q * math.log2(q / mass) for q in g.values() if q > 0)
        return h

    def unit_report(self, u: Unit, S=frozenset(), lam: float = 0.0, cost: float = 1.0,
                    continuation: str = "retain") -> UnitReport:
        e0 = self.evaluate(S, continuation)
        e1 = self.evaluate(frozenset(S) | {u}, continuation)
        dj = e1.value - e0.value
        p_flip = gain = 0.0
        for (p, _), a0, a1, r0, r1 in zip(self.belief, e0.actions, e1.actions, e0.returns, e1.returns):
            if a0 != a1:
                p_flip += p
                gain += p * (r1 - r0)
        dq = gain / p_flip if p_flip > 0 else 0.0
        return UnitReport(str(u), dj, dj - lam * cost, p_flip, dq, dj - gain, self.entropy(u, S))

    def allocation_labels(self, units: list[Unit], costs: dict[Unit, float] | None = None,
                          continuation: str = "retain") -> AllocationLabels:
        costs = costs or {u: 1.0 for u in units}
        U = frozenset(units)
        j_full = self.evaluate(U, continuation).value
        values = {}
        sufficient = []
        for r in range(len(units) + 1):
            for combo in itertools.combinations(sorted(units), r):
                S = frozenset(combo)
                v = self.evaluate(S, continuation).value
                values[S] = v
                if v >= j_full - self.tol:
                    sufficient.append(S)
        minimal = [S for S in sufficient if not any(T < S for T in sufficient)]
        min_cost = min(sum(costs[u] for u in S) for S in sufficient)
        cheapest = [S for S in sufficient if abs(sum(costs[u] for u in S) - min_cost) < 1e-12]
        full_actions = self.evaluate(U, continuation).actions
        loo_nec = [u for u in sorted(units) if values[U - {u}] < j_full - self.tol]
        loo_act = [u for u in sorted(units) if self.evaluate(U - {u}, continuation).actions != full_actions]
        fmt = lambda sets: [sorted(str(u) for u in S) for S in sorted(sets, key=lambda s: (len(s), sorted(s)))]
        return AllocationLabels(
            units=[str(u) for u in sorted(units)],
            j_full=j_full,
            j_empty=values[frozenset()],
            minimal_sufficient=fmt(minimal),
            minimum_cost_sufficient=fmt(cheapest),
            loo_necessary=[str(u) for u in loo_nec],
            loo_action_changing=[str(u) for u in loo_act],
            subset_values={"{" + ",".join(sorted(str(u) for u in S)) + "}": round(v, 10) for S, v in values.items()},
        )

    # ------------------------------------------------------------ depth certification
    def effective_depth(self, units: list[Unit], continuation: str = "retain") -> int:
        """Smallest d such that the depth<=d units reach J(U), relative to this oracle's policy class."""
        j_full = self.evaluate(frozenset(units), continuation).value
        for d in (0, 1, 2):
            if self.evaluate(frozenset(u for u in units if u.depth <= d), continuation).value >= j_full - self.tol:
                return d
        return 3

    def indistinguishable_pairs(self, units: list[Unit], below_depth: int) -> list[tuple[int, int]]:
        """World pairs identical in history and in all units of depth < ``below_depth``
        whose fully-allocated optimal first actions differ."""
        shallow = [u for u in units if u.depth < below_depth]
        acts = self.evaluate(frozenset(units)).actions
        pairs = []
        for i, j in itertools.combinations(range(len(self.worlds)), 2):
            same = self.contents(self.worlds[i], shallow) == self.contents(self.worlds[j], shallow)
            if same and acts[i] != acts[j]:
                pairs.append((i, j))
        return pairs


def brute_force_best_return(world: World, obs: Observation) -> float:
    """Privileged full-information bound for ONE known world: exhaustive search over action
    sequences, independent of the belief machinery above."""
    if obs.done:
        return 0.0
    best = -math.inf
    for a in legal_actions(world.config, obs):
        w = world.clone()
        o = w.step(a)
        best = max(best, o.reward + brute_force_best_return(w, o))
    return best
