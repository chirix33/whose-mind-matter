"""Exact symbolic evaluators for finite Tier 1 hypothesis sets (implementation-spec §4).

Every quantity is computed by exhaustive enumeration of the hidden worlds consistent with
the robot-visible history h, plus belief-space expectimax over the finite horizon. There is
no sampling. "Exact" means exact relative to the stated model, actor, and computation.

Two roles are kept apart:
- the EVALUATOR's posterior b_h(w) (prior over worlds that replay h exactly, renormalized),
  used only to take expectations of realized returns;
- the ACTOR's belief, which depends on the label record (below). The actor never sees w.

Label records (AGENTS §5.2; D-001 review outcome):
- PRIVILEGED_BAYES ("legacy privileged perfect-content reference"): Bayes-optimal actor over
  h with the TRUE contents of S revealed. These are the Stage 0 values.
- PRIVILEGED_BOUNDED ("privileged perfect-content, bounded actor"): the face-value bounded
  actor (below) with the TRUE contents of S revealed.
- GROUNDED ("grounded bounded-policy value", the main symbolic target): the face-value
  bounded actor whose modeled units carry evidence-grounded outputs (the posterior of each
  unit's default-holds cell given h: the probability its factor departs from the face-value
  default, never its content value). It is identical in every world consistent
  with h.

Bounded actor (spec §4.2): its prior is the generator prior times eps**(number of
violated face-value defaults among UNMODELED factors). eps = 1e-6 ("face_value") or 0.25
("hedged", the alternative testimony default). Grounded unit outputs enter by I-projection
(iterative proportional fitting) of that prior onto each modeled unit's cell marginal.

Definitions:
  a_m           the actor's argmax action under cognitive state m; ties broken by canonical
                action order.
  Q_ref(w,m,a)  realized return in true world w of taking a, then following the FIXED
                continuation: the same actor with state m, no new instantiations, belief
                updated by exact conditioning on new observations.
  J(S)          sum_w b_h(w) Q_ref(w, m_S, a_{m_S})     ("retain")
  D_action      E[Q_ref(m, a_y) - Q_ref(m, a_0)]         (current-action component)
  D_memory      E[Q_ref(m_y, a_y) - Q_ref(m, a_y)]       (carryover component)
  VoMI_retained = D_action + D_memory - lambda*c = J(S+u) - J(S) - lambda*c
"""

from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass, field

from officeminds.episode import VisibleHistory
from officeminds.scenarios import Scenario
from officeminds.world import Action, Observation, World, WorldConfig, legal_actions

from .units import Unit, all_factors, content, default_holds

Items = tuple[tuple[float, World], ...]

PRIVILEGED_BAYES = "privileged_bayes"
PRIVILEGED_BOUNDED = "privileged_bounded"
GROUNDED = "grounded"
RECORDS = (PRIVILEGED_BAYES, PRIVILEGED_BOUNDED, GROUNDED)
TESTIMONY_DEFAULTS = {"face_value": 1e-6, "hedged": 0.25}


def _normalize(items) -> Items:
    total = sum(w for w, _ in items)
    return tuple((w / total, x) for w, x in items)


def _obs_key(o: Observation) -> str:
    return json.dumps(o.to_dict(), sort_keys=True)


@dataclass
class AllocationEval:
    value: float
    actions: list[Action]  # actor's current action per hypothesis world (oracle.worlds order)
    returns: list[float]  # Q_ref(w, m_S, a) per world


@dataclass
class UnitReport:
    unit: str
    delta_j: float  # J(S+u) - J(S)
    vomi: float  # delta_j - lambda * cost
    p_flip: float  # current-action flip probability
    dq_given_flip: float
    no_flip_residual: float  # delta_j - p_flip * dq_given_flip
    content_entropy_bits: float  # H(c_u | c_S) under b_h (D1-style target)


@dataclass
class Decomposition:
    unit: str
    record: str
    q_m_a0: float  # E[Q_ref(m, a_0)] = J(S)
    q_m_ay: float  # E[Q_ref(m, a_y)]
    q_my_ay: float  # E[Q_ref(m_y, a_y)] = J(S+u)
    d_action: float
    d_memory: float
    total: float
    residual: float  # total - (d_action + d_memory); must be ~0
    p_flip: float
    carryover: bool  # positive value with zero current-action flips


@dataclass
class AllocationLabels:
    units: list[str]
    j_full: float
    j_empty: float
    minimal_sufficient: list[list[str]]
    minimum_cost_sufficient: list[list[str]]
    loo_necessary: list[str]
    loo_action_changing: list[str]
    subset_values: dict[str, float] = field(default_factory=dict)


class ExactOracle:
    def __init__(self, scenario: Scenario, hist: VisibleHistory, tol: float = 1e-9,
                 testimony: str = "face_value"):
        self.config: WorldConfig = scenario.config
        self.tol = tol
        self.testimony = testimony
        self.eps = TESTIMONY_DEFAULTS[testimony]
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
        # Face-value default violations, evaluated on each hypothesis world's current minds.
        self.violations = [frozenset(f for f in all_factors(x) if not default_holds(x, f)) for x in self.worlds]
        self._v: dict = {}
        self._alloc: dict = {}
        self._grounded: dict = {}

    # ------------------------------------------------------------ belief-space expectimax
    def _key(self, items: Items) -> tuple:
        return tuple(sorted(("%.12g" % w, x.signature()) for w, x in items))

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

    def ranked_actions(self, items: Items, obs: Observation) -> list[tuple[Action, float]]:
        return [(a, self.q(items, obs, a)) for a in legal_actions(self.config, obs)]

    def best_action(self, items: Items, obs: Observation) -> Action:
        best, best_q = None, -math.inf
        for a, qa in self.ranked_actions(items, obs):  # canonical order => deterministic ties
            if qa > best_q + self.tol:
                best, best_q = a, qa
        return best

    def decision_margin(self, items: Items, obs: Observation) -> float:
        """Actor's own top-1 minus top-2 action value (no true values involved)."""
        qs = sorted((qa for _, qa in self.ranked_actions(items, obs)), reverse=True)
        return qs[0] - qs[1] if len(qs) > 1 else math.inf

    def realized_return(self, world: World, items: Items, obs: Observation, first: Action) -> float:
        """Q_ref: take `first` in the true world, then follow the fixed actor with belief `items`."""
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

    # ------------------------------------------------------------ actor beliefs per record
    def contents(self, world: World, S) -> tuple:
        return tuple(content(world, u) for u in sorted(S))

    def cell(self, world: World, u: Unit) -> bool:
        """Grounded output support: does u's factor satisfy its face-value default?

        Deliberately NOT the content value. Knowledge outputs assess information access and the
        possibility of a false belief; Reliability outputs assess intent; nested outputs assess
        whether j's model of k is accurate. If the content marginal were exposed, a unit such as
        K(alice), whose belief equals the target, would hand the actor the whole-scene posterior
        over the answer (seen in stakes_m4_q0.95 before this restriction)."""
        return default_holds(world, u)

    def condition(self, world: World, S) -> Items:
        c = self.contents(world, S)
        return _normalize([(w, x) for w, x in self.belief if self.contents(x, S) == c])

    def _bounded_prior(self, S) -> list[float]:
        S = frozenset(S)
        return [p * self.eps ** len(v - S) for (p, _), v in zip(self.belief, self.violations)]

    def grounded_output(self, u: Unit) -> dict[tuple, float]:
        """Evidence-grounded unit output: posterior P(default holds | h) for u's factor."""
        out: dict[tuple, float] = {}
        for p, x in self.belief:
            c = self.cell(x, u)
            out[c] = out.get(c, 0.0) + p
        return dict(sorted(out.items(), key=lambda kv: repr(kv[0])))

    def _grounded_items(self, S) -> Items:
        S = frozenset(S)
        if S not in self._grounded:
            weights = self._bounded_prior(S)
            targets = {u: self.grounded_output(u) for u in sorted(S)}
            cells = {u: [self.cell(x, u) for x in self.worlds] for u in targets}
            for _ in range(1000):  # I-projection by iterative proportional fitting
                worst = 0.0
                for u, tgt in targets.items():
                    total = sum(weights)
                    cur: dict[tuple, float] = {}
                    for wt, c in zip(weights, cells[u]):
                        cur[c] = cur.get(c, 0.0) + wt / total
                    worst = max(worst, max(abs(cur[c] - tgt[c]) for c in tgt))
                    weights = [wt * tgt[c] / cur[c] for wt, c in zip(weights, cells[u])]
                if worst < 1e-14:
                    break
            self._grounded[S] = _normalize(list(zip(weights, self.worlds)))
        return self._grounded[S]

    def actor_items(self, S, record: str, i: int) -> Items:
        S = frozenset(S)
        if record == PRIVILEGED_BAYES:
            return self.condition(self.worlds[i], S)
        if record == GROUNDED:
            return self._grounded_items(S)
        if record == PRIVILEGED_BOUNDED:
            c = self.contents(self.worlds[i], S)
            prior = self._bounded_prior(S)
            return _normalize([(wt, x) for wt, x in zip(prior, self.worlds) if self.contents(x, S) == c])
        raise ValueError(record)

    # ------------------------------------------------------------ allocations and VoMI
    def evaluate(self, S=frozenset(), continuation: str = "retain", record: str = PRIVILEGED_BAYES) -> AllocationEval:
        key = (frozenset(S), continuation, record)
        if key not in self._alloc:
            actions, returns, total = [], [], 0.0
            for i, (p, w) in enumerate(self.belief):
                items = self.actor_items(S, record, i)
                a = self.best_action(items, self.obs)
                cont = items if continuation == "retain" else self.actor_items(frozenset(), record, i)
                r = self.realized_return(w, cont, self.obs, a)
                actions.append(a)
                returns.append(r)
                total += p * r
            self._alloc[key] = AllocationEval(total, actions, returns)
        return self._alloc[key]

    def decompose(self, u: Unit, S=frozenset(), record: str = GROUNDED) -> Decomposition:
        """D-002: current-action and carryover components under the fixed continuation."""
        S = frozenset(S)
        q_m_a0 = q_m_ay = q_my_ay = p_flip = 0.0
        for i, (p, w) in enumerate(self.belief):
            m, my = self.actor_items(S, record, i), self.actor_items(S | {u}, record, i)
            a0, ay = self.best_action(m, self.obs), self.best_action(my, self.obs)
            q_m_a0 += p * self.realized_return(w, m, self.obs, a0)
            q_m_ay += p * self.realized_return(w, m, self.obs, ay)
            q_my_ay += p * self.realized_return(w, my, self.obs, ay)
            p_flip += p * (a0 != ay)
        d_action, d_memory, total = q_m_ay - q_m_a0, q_my_ay - q_m_ay, q_my_ay - q_m_a0
        return Decomposition(str(u), record, q_m_a0, q_m_ay, q_my_ay, d_action, d_memory, total,
                             total - d_action - d_memory, p_flip,
                             carryover=p_flip == 0 and d_memory > self.tol)

    def actor_rollout(self, i: int, S=frozenset(), record: str = GROUNDED) -> tuple[list[Action], float]:
        """Actions the actor with state m_S takes in hypothesis world i under the fixed continuation
        (the same policy whose realized return defines J); returns (actions, return)."""
        items, w = self.actor_items(S, record, i), self.worlds[i].clone()
        o, actions, total = self.obs, [], 0.0
        while not o.done:
            a = self.best_action(items, o)
            o = w.step(a)
            actions.append(a)
            total += o.reward
            items = _normalize(self._transition(items, a)[_obs_key(o)][1])
        return actions, total

    def optimal_action_set(self, S, record: str = GROUNDED) -> list[Action]:
        """Actions whose evaluator-expected Q_ref under state m_S is maximal (within tol)."""
        qs = {}
        for a in legal_actions(self.config, self.obs):
            qs[a] = sum(p * self.realized_return(w, self.actor_items(S, record, i), self.obs, a)
                        for i, (p, w) in enumerate(self.belief))
        best = max(qs.values())
        return [a for a, v in qs.items() if v >= best - self.tol]

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
                    continuation: str = "retain", record: str = PRIVILEGED_BAYES) -> UnitReport:
        e0 = self.evaluate(S, continuation, record)
        e1 = self.evaluate(frozenset(S) | {u}, continuation, record)
        dj = e1.value - e0.value
        p_flip = gain = 0.0
        for (p, _), a0, a1, r0, r1 in zip(self.belief, e0.actions, e1.actions, e0.returns, e1.returns):
            if a0 != a1:
                p_flip += p
                gain += p * (r1 - r0)
        dq = gain / p_flip if p_flip > 0 else 0.0
        return UnitReport(str(u), dj, dj - lam * cost, p_flip, dq, dj - gain, self.entropy(u, S))

    def subset_values(self, units: list[Unit], continuation: str = "retain",
                      record: str = PRIVILEGED_BAYES) -> dict[frozenset, float]:
        return {frozenset(c): self.evaluate(frozenset(c), continuation, record).value
                for r in range(len(units) + 1) for c in itertools.combinations(sorted(units), r)}

    def allocation_labels(self, units: list[Unit], costs: dict[Unit, float] | None = None,
                          continuation: str = "retain", record: str = PRIVILEGED_BAYES) -> AllocationLabels:
        costs = costs or {u: 1.0 for u in units}
        U = frozenset(units)
        values = self.subset_values(units, continuation, record)
        j_full = values[U]
        sufficient = [S for S, v in values.items() if v >= j_full - self.tol]
        minimal = [S for S in sufficient if not any(T < S for T in sufficient)]
        min_cost = min(sum(costs[u] for u in S) for S in sufficient)
        cheapest = [S for S in sufficient if abs(sum(costs[u] for u in S) - min_cost) < 1e-12]
        full_actions = self.evaluate(U, continuation, record).actions
        loo_nec = [u for u in sorted(units) if values[U - {u}] < j_full - self.tol]
        loo_act = [u for u in sorted(units) if self.evaluate(U - {u}, continuation, record).actions != full_actions]
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
    def effective_depth(self, units: list[Unit], continuation: str = "retain", record: str = PRIVILEGED_BAYES) -> int:
        """Smallest d such that the depth<=d units reach J(U), relative to this record's actor class."""
        j_full = self.evaluate(frozenset(units), continuation, record).value
        for d in (0, 1, 2):
            if self.evaluate(frozenset(u for u in units if u.depth <= d), continuation, record).value >= j_full - self.tol:
                return d
        return 3

    def indistinguishable_pairs(self, units: list[Unit], below_depth: int) -> list[tuple[int, int]]:
        """(Legacy record) world pairs identical in history and in all units of depth < ``below_depth``
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
