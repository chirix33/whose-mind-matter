# D-003 — Which gold-allocation definition drives which metric

- Status: **accepted with revision — set-valued gold; static-union D4 target REJECTED** (review 2026-10-28)
- Date: 2026-10-28
- Affects: outline §5.4 ("minimal set of units whose removal changes the oracle action"), §6.5 allocation precision/recall, D4 relevance-classifier targets; AGENTS §5.3

## Problem
The outline's wording is ambiguous, and gold sets are often not unique. The candidate definitions disagree on the tiny cases:

| Case | Minimal sufficient sets | LOO value-necessary | LOO action-changing |
|---|---|---|---|
| `substitutes` | {K(alice)}, {K(bob)}, {K(bob→alice)}, {K(alice→bob)} | none | none |
| `depth2_handoff` | {K(alice), K(rec→alice)}, {K(alice), K(alice→rec)} | K(alice) | K(alice) |
| `stakes_*` | {K(alice)}, {K(bob)}, {R(bob)} | none | none |

Under a "removal changes the action" reading:
- `substitutes` and the stakes pairs have an **empty** gold set, even though every unit has positive value. That would score any allocation as wasteful.
- In `depth2_handoff`, the gold set would be {K(alice)} alone, which misses that a depth-2 unit is required.

(Source: run `tiny-20261028-032629-565fb8`, `labels.json`. These are record-A labels; see D-001.)

## Proposal
- **Primary allocation metrics: precision and recall against the *set of* minimal sufficient sets.** For an allocation A:
  - recall = max over gold sets G of |A∩G| / |G|;
  - precision = |A ∩ (∪ of gold sets that maximize recall)| / |A|.
  - So an equivalent valid set scores 1.0.
- **Wasted units:** units with ΔJ(u | A∖u) ≤ λc (conditional, not singleton).
- **Missed units:** units u ∉ A with ΔJ(u | A) > λc.
- **D4 (relevance classifier) target:** membership in the union of minimal sufficient sets. This should be confirmed, since it decides how strong D4 is.
- Report the minimum-cost sufficient set for compute-optimal analyses. Keep LOO necessity as a diagnostic only.

## Review outcome
**Accepted with revision.** Supplied by the research review 2026-10-28 (`research-reviews/stage-0-research-review.md`, supplied by Ashraf; that folder is gitignored, so the binding points are restated here).

- Distinguish minimal sufficient sets, minimum-cost sufficient sets, and LOO necessity. Declare what sufficiency preserves. This implementation uses **reference expected task value within tol = 1e-9**. Keep budget/λ dependence explicit.
- Match each predicted allocation to **one** gold set under a declared rule, and compute P/R/F1 against that same set; the per-metric maximization proposed above is superseded.
- Also report decision-value regret against the full and the budget-feasible references, and whether the chosen action is in the optimal-action set.
- Wasted compute = conditional net value plus actual incremental cost. Distinguish missed units from missed complementary bundles.
- **D4 target: conditional relevance for completing a sufficient allocation, plus STOP. Not the static union.** Give it a fair implementation and count re-evaluation/STOP cost in its compute.
