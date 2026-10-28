"""Set-valued gold allocations and allocation metrics (D-003; Stage 1 review correction 4).

All functions take ``values``: J(S) for every subset S of the candidate set U (from
``ExactOracle.subset_values``) under one declared record and continuation.

Declared conventions:
- Objective: obj(S) = J(S) - lam * cost(S), with lam stated by the caller (gross when lam = 0).
  Admissible: cost(S) <= budget (no budget = all subsets, including ∅).
- PRIMARY reference ("best"): the best admissible objective. J(all candidates) can be below the
  best subset for non-monotone bounded/LLM actors, so it is not the primary reference.
  ``reference="all"`` reproduces the Stage 0/1 J(all)-relative definition as a labeled
  historical diagnostic.
- Conditional reference for D4/STOP at state S: R(S) = best admissible objective among
  supersets of S (the controller cannot un-instantiate). At S = ∅ this is the primary reference,
  so the target never silently changes between steps; it only conditions on choices made.
  STOP(S) iff obj(S) >= R(S) - tol. Relevant(u | S) iff u is in a minimal completion C with
  S ∪ C attaining R(S).
- Gold matching: a predicted allocation A is matched to ONE reference-attaining minimal set G*,
  chosen by maximum F1, then higher recall, then smaller |G|, then lexicographic order.
  Precision, recall, and F1 are all computed against that same G*.
- Wasted unit: u in A with gross J(A) - J(A - u) <= lam * c(u) (net <= 0; the price is
  subtracted once). Missed unit: u not in A with J(A + u) - J(A) > lam * c(u).
"""

from __future__ import annotations

from dataclasses import dataclass

Values = dict[frozenset, float]


def _cost(S, costs) -> float:
    return sum(costs.get(u, 1.0) for u in S) if costs else float(len(S))


def _full(values: Values) -> frozenset:
    return max(values, key=len)


def objective(S, values: Values, lam: float = 0.0, costs: dict | None = None) -> float:
    return values[S] - lam * _cost(S, costs)


def _admissible(values, budget, costs):
    return [S for S in values if budget is None or _cost(S, costs) <= budget + 1e-12]


def reference_value(values: Values, lam: float = 0.0, costs: dict | None = None, budget: float | None = None,
                    reference: str = "best", within: frozenset = frozenset()) -> float:
    if reference == "all":
        return objective(_full(values), values, lam, costs)
    return max(objective(S, values, lam, costs) for S in _admissible(values, budget, costs) if S >= within)


def sufficient_sets(values: Values, tol: float = 1e-9, lam: float = 0.0, costs: dict | None = None,
                    budget: float | None = None, reference: str = "best", within: frozenset = frozenset()) -> list[frozenset]:
    ref = reference_value(values, lam, costs, budget, reference, within)
    return [S for S in _admissible(values, budget, costs)
            if S >= within and objective(S, values, lam, costs) >= ref - tol]


def minimal_sufficient(values: Values, tol: float = 1e-9, **kw) -> list[frozenset]:
    suff = sufficient_sets(values, tol, **kw)
    return sorted((S for S in suff if not any(T < S for T in suff)), key=lambda s: (len(s), sorted(map(str, s))))


def minimal_completions(S: frozenset, values: Values, tol: float = 1e-9, **kw) -> list[frozenset]:
    comps = [T - S for T in sufficient_sets(values, tol, within=S, **kw)]
    return sorted({C for C in comps if not any(D < C for D in comps)}, key=lambda c: (len(c), sorted(map(str, c))))


def stop(S: frozenset, values: Values, tol: float = 1e-9, lam: float = 0.0, costs: dict | None = None,
         budget: float | None = None, reference: str = "best") -> bool:
    ref = reference_value(values, lam, costs, budget, reference, within=S if reference == "best" else frozenset())
    return objective(S, values, lam, costs) >= ref - tol


def conditional_relevance(S: frozenset, values: Values, tol: float = 1e-9, minimum_cost: bool = False,
                          costs: dict | None = None, lam: float = 0.0, budget: float | None = None) -> set:
    """D4 target at state S under the conditional best reference; empty when STOP(S)."""
    if stop(S, values, tol, lam, costs, budget):
        return set()
    comps = [C for C in minimal_completions(S, values, tol, lam=lam, costs=costs, budget=budget) if C]
    if not comps:
        return set()
    if minimum_cost:
        cheapest = min(_cost(C, costs) for C in comps)
        comps = [C for C in comps if abs(_cost(C, costs) - cheapest) < 1e-12]
    return set().union(*comps)


@dataclass
class AllocationScore:
    reference: str
    lam: float
    budget: float | None
    reference_value: float
    matched_gold: list[str]
    precision: float
    recall: float
    f1: float
    regret: float  # reference objective - obj(A)
    regret_budget: float  # best objective with cost <= cost(A), minus obj(A)
    regret_vs_all_historical: float  # J(all) - J(A) (Stage 0/1 diagnostic)
    wasted: list[str]
    missed: list[str]
    missed_bundles: list[list[str]]  # minimal completions (size >= 2), positive net, all singletons non-positive


def score_allocation(A: frozenset, values: Values, lam: float = 0.0, costs: dict | None = None,
                     tol: float = 1e-9, budget: float | None = None, reference: str = "best") -> AllocationScore:
    kw = dict(lam=lam, costs=costs, budget=budget, reference=reference)
    gold = minimal_sufficient(values, tol, **kw)

    def prf(G):
        if not A and not G:
            return 1.0, 1.0, 1.0
        tp = len(A & G)
        p = tp / len(A) if A else 1.0
        r = tp / len(G) if G else 1.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        return p, r, f

    G = min(gold, key=lambda g: (-prf(g)[2], -prf(g)[1], len(g), sorted(map(str, g))))
    p, r, f = prf(G)
    ref = reference_value(values, lam, costs, budget, reference)
    obj_a = objective(A, values, lam, costs)
    budget_best = max(objective(T, values, lam, costs) for T in values if _cost(T, costs) <= _cost(A, costs) + 1e-12)
    c = lambda u: costs.get(u, 1.0) if costs else 1.0
    j_a = values[A]
    wasted = [u for u in sorted(A) if j_a - values[A - {u}] <= lam * c(u) + tol]
    missed = [u for u in sorted(_full(values) - A) if values[A | {u}] - j_a > lam * c(u) + tol]
    bundles = []
    for C in minimal_completions(A, values, tol, lam=lam, costs=costs, budget=budget):
        if len(C) >= 2 and values[A | C] - j_a > lam * _cost(C, costs) + tol \
                and all(values[A | {u}] - j_a <= lam * c(u) + tol for u in C):
            bundles.append(sorted(map(str, C)))
    return AllocationScore(reference, lam, budget, ref, sorted(map(str, G)), p, r, f, ref - obj_a, budget_best - obj_a,
                           values[_full(values)] - j_a, list(map(str, wasted)), list(map(str, missed)), bundles)
