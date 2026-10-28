# Milestone report — Stage 1: semantics and counterexamples (2026-10-28)

**Scope.** Implements the Stage 0 research review: D-001…D-006 are recorded as accepted with constraints. No bulk labels, training, LLM labels or confirmatory runs. The model server was not needed. It was stopped at 04:01 on the workstation (GPU back to 2.1 GB used), and the smoke test was not repeated because no serving code or environment changed.

**Claims/RQs addressed:** none evaluated. This milestone delivers definitions plus checked constructions for RQ6 (P1/P2/P3), C4 groundwork (directed paths, certification), C2 groundwork (stakes pairs, D4 target), and C3 groundwork (bounded actors harmed by partial information).

**Environment:** workstation, WSL2 Ubuntu 24.04, CPU only for everything in this report.

## Review steps → what was done
| # | Review step | Status | Where |
|---|---|---|---|
| 1 | Record rulings; relabel legacy values without overwriting provenance | done | `docs/decisions/` (all six accepted), `docs/decisions/discrepancy-log.md` (16 rows), spec v0.2; legacy values in Part A of `reports/tiny-cases.md` |
| 2 | Grounded bounded-policy label path + graph retention | done | `src/vomi/oracle.py` (`GROUNDED`, bounded actor, I-projection), `src/vomi/graph.py` |
| 3 | Invisible-world invariance pair; direct-testimony baseline; false-belief/reliability case; nested-R case | done | `tests/test_grounded.py`; cases `false_belief`, `nested_reliability` |
| 4 | Retention counterexample with D_action / D_memory; identity check | done | `depth2_handoff`: E[Q(m,a0)] = 0.80, E[Q(m,ay)] = 0.80, E[Q(my,ay)] = 0.85 → D_action 0, D_memory 0.05, residual 0 (carryover). Identity < 1e-12 for every unit × case × record |
| 5 | Non-unique gold sets; conditional D4 relevance / STOP on substitutes and complements | done | `src/vomi/allocation.py`, `tests/test_allocation_theory.py` |
| 6 | Holder permutations, relevance shifts, directed-path asymmetry, P2 boundary checks, reward/horizon tests, stakes ranking reversal | done, except the ranking reversal (§ D-006) | cases `holder_*`, `relevance_shift`, `path_asymmetry`; P2 and D-005 tests |
| 7 | Clean-commit rerun; a non-degenerate posterior with hand-worked values | done | hand values for 5 non-degenerate cases (spec §6.2); run IDs below |

## Key results (exact, symbolic; face-value testimony unless noted)
| Case | J(∅) | Gold (grounded) | J(gold) | D_action / D_memory of the gold unit | Hedged J(∅) → J(gold) |
|---|---|---|---|---|---|
| false_belief | 0.450 | {K(rec)} | 0.800 | +0.35 / 0 | 0.80 → 0.80 |
| holder_rec / holder_carol | 0.450 | {K(holder)} | 0.800 | +0.35 / 0 (name-symmetric) | 0.80 → 0.80 |
| relevance_shift | 0.675 | {K(rec)} | 0.835 | 0 / +0.16 (carryover); after Alice appears: 0 | 0.835 → 0.835 |
| nested_reliability | 0.575 | {K(rec)}, {K(rec→bob)}, **{R(rec→bob)}**, {K(bob→rec), R(bob)} | 0.800 | −0.10 / +0.325 | 0.575 → 0.80 |
| path_asymmetry (F6) | 0.575 | **{K(rec→alice)}** only; K(alice→rec), K(rec), K(alice) = 0 | 0.800 | −0.10 / +0.325 | 0.80 → 0.80 |
| stakes_m4_q0.95 | 0.800 | {R(bob)} | 0.845 | +0.045 / 0 | same |
| legacy cases (depth0/1, distractors, substitutes, depth2_handoff, other stakes) | — | ∅ | — | all units 0 under grounded | — |

Values that differ from the legacy record, as the review predicted:
- `depth1_knowledge` K(alice): **0.125 legacy → 0 grounded**. Uninferable content no longer earns value.
- Every grounded value in this table has a hand derivation in spec §6.2 and is asserted in tests.

## D-006 stakes ranking reversal
_(filled in below once the search finishes)_

## Commands run and outcomes
_(filled in at the clean-commit rerun)_

## Failures and problems found (all fixed or flagged)
1. **Leak in my first grounded-output definition.** Unit outputs initially included the content marginal. K(alice), whose belief equals the target, then handed the actor the whole-scene posterior (+0.045 in `stakes_m4_q0.95`). Fixed: outputs are now P(default holds | h) only. A regression test covers it.
2. **Undeclared truth.** Legacy `depth2_handoff` never declared the truth of `meeting_room`, so every belief counted as a default violation. Fixed: the truth is declared, and `World.truth` now raises on undeclared facts. Legacy values are unchanged.
3. **Spurious substitute.** In my first `path_asymmetry`, rec's own belief was coupled to what Alice told her, which made K(rec) a fake substitute. Fixed by decoupling the channels.
4. **Wrong expectation in a test.** I expected the privileged content of K(rec) to differ across the invariance pair. It cannot (rec's belief is the same in both worlds), so the test now uses K(alice).
5. **Structural leakage (OPEN Q2).** Generators that entail default violations make the bounded actor hedge for free. All legacy cases have zero grounded value for this reason, or because they contain no false beliefs.
6. **Bounded actors can be hurt by information (OPEN Q3):** privileged_bounded K(alice) −0.60 in `depth2_handoff`; grounded hedged K(alice) −0.225 in `path_asymmetry`.

## Limitations
- Tiny hand-built cases only, with no balanced generator.
- The bounded actor plans physically by exact expectimax; only mental modeling is bounded.
- Cost c(u) = 1 is a placeholder. No LLM records exist yet.
- Graph contradiction detection covers location claims refuted by the robot's own observations only.
- The P4 greedy theory is not implemented.

## Next action
1. Research review of Q1–Q6 (`reports/review-request.md`).
2. After that, the small local end-to-end pilot (30–50 dev scenario groups, gpt-oss-20b) as the review directs. This requires a balanced generator that obeys the Q2 generator rule.
