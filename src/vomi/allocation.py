"""Set-valued gold allocations and allocation metrics (D-003 review outcome).

All functions take ``values``: J(S) for every subset S of the candidate set U (from
``ExactOracle.subset_values``) under one declared record and continuation.

Declared conventions:
- Sufficiency preserves the reference expected task value: J(S) >= J(U) - tol.
- Unit costs are equal (1 instantiation each) unless ``costs`` says otherwise.
- Gold matching: a predicted allocation A is matched to ONE minimal sufficient set G* that
  maximizes F1(A, G); ties go to higher recall, then smaller |G|, then lexicographic order.
  Precision, recall, and F1 are all computed against that same G*.
- D4 conditional-relevance target: given the current allocation S, a unit is relevant iff it
  belongs to some minimal completion C (S ∪ C sufficient, no proper subset of C suffices).
  STOP(S) = S is already sufficient. These replace the static union of gold sets.
"""

from __future__ import annotations

from dataclasses import dataclass

Values = dict[frozenset, float]


def _cost(S, costs) -> float:
    return sum(costs.get(u, 1.0) for u in S) if costs else float(len(S))


def sufficient_sets(values: Values, tol: float = 1e-9) -> list[frozenset]:
    j_full = max(values.items(), key=lambda kv: len(kv[0]))[1]
    return [S for S, v in values.items() if v >= j_full - tol]


def minimal_sufficient(values: Values, tol: float = 1e-9) -> list[frozenset]:
    suff = sufficient_sets(values, tol)
    return sorted((S for S in suff if not any(T < S for T in suff)), key=lambda s: (len(s), sorted(map(str, s))))


def minimal_completions(S: frozenset, values: Values, tol: float = 1e-9) -> list[frozenset]:
    suff = set(sufficient_sets(values, tol))
    comps = [T - S for T in values if T >= S and T in suff]
    return sorted({C for C in comps if not any(D < C for D in comps)}, key=lambda c: (len(c), sorted(map(str, c))))


def stop(S: frozenset, values: Values, tol: float = 1e-9) -> bool:
    return S in set(sufficient_sets(values, tol))


def conditional_relevance(S: frozenset, values: Values, tol: float = 1e-9, minimum_cost: bool = False,
                          costs: dict | None = None) -> set:
    """D4 target at state S. With ``minimum_cost``, only cheapest completions count."""
    if stop(S, values, tol):
        return set()
    comps = minimal_completions(S, values, tol)
    if minimum_cost:
        cheapest = min(_cost(C, costs) for C in comps)
        comps = [C for C in comps if abs(_cost(C, costs) - cheapest) < 1e-12]
    return set().union(*comps)


@dataclass
class AllocationScore:
    matched_gold: list[str]
    precision: float
    recall: float
    f1: float
    regret_full: float  # J(U) - J(A)
    regret_budget: float  # max_{cost(T) <= cost(A)} J(T) - J(A)
    wasted: list[str]  # u in A with J(A) - J(A - u) <= lam * c(u)
    missed: list[str]  # u not in A with J(A + u) - J(A) > lam * c(u)
    missed_bundles: list[list[str]]  # minimal completions (size >= 2) with positive net value
    #                                  whose every singleton is individually non-positive


def score_allocation(A: frozenset, values: Values, lam: float = 0.0, costs: dict | None = None,
                     tol: float = 1e-9) -> AllocationScore:
    gold = minimal_sufficient(values, tol)

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
    j_full = max(values.items(), key=lambda kv: len(kv[0]))[1]
    j_a = values[A]
    budget = max(v for T, v in values.items() if _cost(T, costs) <= _cost(A, costs) + 1e-12)
    c = lambda u: costs.get(u, 1.0) if costs else 1.0
    wasted = [u for u in sorted(A) if j_a - values[A - {u}] <= lam * c(u) + tol]
    missed = [u for u in sorted(set().union(*values) - A) if values[A | {u}] - j_a > lam * c(u) + tol]
    bundles = []
    for C in minimal_completions(A, values, tol):
        if len(C) >= 2 and values[A | C] - j_a > lam * _cost(C, costs) + tol \
                and all(values[A | {u}] - j_a <= lam * c(u) + tol for u in C):
            bundles.append(sorted(map(str, C)))
    return AllocationScore(sorted(map(str, G)), p, r, f, j_full - j_a, budget - j_a,
                           list(map(str, wasted)), list(map(str, missed)), bundles)
