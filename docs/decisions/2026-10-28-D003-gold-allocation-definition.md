# D-003 — Which gold-allocation definition drives which metric

- Status: **proposed**
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

(Source: run `tiny-20261028-031743-88659e`, `labels.json`. These are record-A labels; see D-001.)

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
_(pending)_
