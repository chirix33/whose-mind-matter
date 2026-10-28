# D-006 — Stakes-pair construction for P5 / RQ2(b)

- Status: **accepted — isolating vs general subsets; ranking reversal REQUIRED** (review 2026-10-28)
- Date: 2026-10-28
- Affects: outline §3.5 P5, §5.3 F5, RQ2(b); AGENTS §5.4 P5

## Finding
Multiplying the error penalty ×4 with identical observations does **not** generally leave flip probability unchanged:
- `stakes_m*_q0.95`: P(flip) of R(bob) is 0.05 at ×1 but 1.0 at ×4, because the base action switches from drop to walk.
- `stakes_m*_q0.975`: P(flip) = 0.025 at both, content entropy equal, ΔJ 0.0375 vs 0.075. This is a valid isolating pair.

## Proposal
1. Generate stakes pairs, then **keep a pair for the P5-isolating subset only if** the base action a(S) and the per-world flip pattern are identical across stakes. Verify this numerically for each pair, as `tests/test_oracle.py::test_stakes_pairs` does.
2. Report non-isolating pairs as a separate subset. There the competitors' own stakes sensitivity, via the changed base action, is genuine and must not be suppressed.
3. A pair should show a **ranking** change, not only a magnitude change. In the current pair, K(alice), K(bob) and R(bob) move together. A ranking-change construction needs one unit whose value comes from averting an error and one whose value comes from saving steps, with equal flip probability. That is TODO.

## Review outcome
**Accepted.** Supplied by the research review 2026-10-28 (`research-reviews/stage-0-research-review.md`, supplied by Ashraf; that folder is gitignored, so the binding points are restated here).

- Maintain (1) **isolating pairs**, where observations, priors, available computations, inference outputs, costs, eligibility and action-change probabilities are fixed while consequences scale, and (2) **general stakes pairs**, reported separately.
- Do not force policies to ignore stakes.
- Add a **ranking-reversal** construction at equal unit cost. The target table (U: P(flip) 0.025, gain 1.5/3.0; V: P(flip) 0.05, gain 1.0) is a design target only. Implement a feasible world and derive its values independently; if the target is infeasible, propose an alternative.
- Carryover must be zero or equal; avoid ties. Check the invariance of the entropy objective as implemented.
- Do not require learned flip-controller outputs to be numerically identical across stakes.

## Implementation status (Stage 1)
- **Ranking reversal found** in the `privileged_bounded` record: `reversal_m1`/`reversal_m4`. U = R(bob) +0.00724 at both stakes (P(flip) 0.036); V = K(carol) +0.02909 → −0.04689 (P(flip) 1.0). Zero carryover, no ties, hand-derived in tests.
- No isolating reversal exists in the `grounded` record within the searched family; a per-criterion diagnostic explains why. Alternatives are put to review as Q5 in `reports/review-request.md`.
