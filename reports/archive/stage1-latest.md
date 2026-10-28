> **Erratum (2026-10-28, after the Stage 1 research review).** This Stage 1 report is archived unchanged below this note. Known errors:
> 1. The grounded `reversal_m*` units K(bob), K(bob→carol) and R(carol) are **+0.02909 at ×1 and −0.04689 at ×4**, not "0 at ×4". J(all) = J(∅) at ×4 was misread as singleton values (D-011).
> 2. `nested_reliability` has required depth **1**, not 2 ({K(rec)} suffices); see spec v0.3 §8.
> 3. Values labeled "VoMI" are **gross delta_J** (no price subtracted).
> 4. Calling the K(alice) content marginal a "leak" because it helped is withdrawn: helpfulness alone is not leakage (D-007). The Stage 1 "grounded" record is now named `grounded_scalar`, a diagnostic.
> 5. The Part B intro of the tiny-case report stated the scalar's polarity backwards: the output is `p_default_holds`.

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
**Found** in the `privileged_bounded` record: the bounded actor, with the true content of the modeled unit. The conflicting-reports family, witness "Bob says office_a, Carol says office_b"; Bob {acc .8, mist .1, obs .25}, Carol {acc .1, mist .02, obs .8} (unnormalized):

| Unit (equal cost) | VoMI ×1 | VoMI ×4 | P(flip) ×1 / ×4 | D_memory | Why |
|---|---|---|---|---|---|
| U = R(bob) | +0.00724 | +0.00724 | 0.036 / 0.036 | 0 | flips walk → drop B only when Bob is obstructive; +0.2, stake-free |
| V = K(carol) | **+0.02909** | **−0.04689** | 1.0 / 1.0 | 0 | reveals Carol's belief without its accuracy; the actor blames Carol and drops A everywhere, so the error exposure scales with stakes |

- Isolation holds: identical observations, priors, costs, eligibility, base action (walk) and targets across stakes; zero carryover; actor margin ≥ 0.05 (no ties).
- The flip ranking (V > U) is fixed, while the VoMI ranking reverses.
- Every number was re-derived by hand (worlds ∝ .016/.64/.01/.025) in `tests/test_grounded.py::test_stakes_ranking_reversal_privileged_bounded`.
- This differs from the review's design table in direction: the high-flip unit loses value with stakes, rather than the low-flip unit gaining it.

**Not found in the `grounded` record.**
- Main search (run `search-20261028-042429-1e7541`, 1000 configs × 4 settings = 4000 combinations): **95 isolating hits, all in `privileged_bounded`** (81 face value, 14 hedged; most common pairs R(carol)/K(bob) 32 and R(bob)/K(carol) 31), and **0 in `grounded`**.
- Per-criterion diagnostic (300 configs × 4 record/testimony settings, run `search-diagnose-20261028-043029-c8ed60`, commit `bea0537`):

| Setting | raw VoMI reversals | pass all isolating criteria | fail: a unit never flips | fail: base action changes | fail: flip pattern changes |
|---|---|---|---|---|---|
| grounded / face value | 244 | **0** | 182 | 14 | 48 |
| grounded / hedged | 78 | **0** | 42 | 36 | 0 |
| privileged_bounded / face value | 214 | 17 | 119 | 57 | 21 |
| privileged_bounded / hedged | 530 | 1 | 59 | 127 | 343 |

Structural reason:
- Grounded outputs depend only on h, so a grounded flip at a given state has probability 0 or 1.
- Isolation then requires two units that both flip deterministically, at both stakes, to targets with different error exposure.
- Face-value trust makes the doubt-raising units share a target, or makes the riskier target stop flipping at ×4.

The grounded record does give **general** pairs: in `reversal_m*`, K(bob), K(bob→carol) and R(carol) are worth +0.029 at ×1 and 0 at ×4. Alternatives are put to review as Q5.

## Commands run and outcomes (WSL, CPU)
| Command | Commit (clean tree) | Outcome |
|---|---|---|
| `~/venvs/officeminds/bin/python -m pytest -q` | `bea0537` | **143 passed** in 37 s |
| `python scripts/run_tiny_cases.py --seed 0` | `bea0537` | run **`tiny-20261028-043121-b0040b`**: 10 legacy + 8 grounded/reversal cases; every episode replays identically and equals its label rollout; no early-failure incentive |
| `python3 scripts/search_stakes_reversal.py --samples 1000 --seed 0` | `5da73f1` (search logic identical at `bea0537`) | run `search-20261028-042429-1e7541`: 4000 combinations, 95 isolating hits (all privileged_bounded), 0 grounded |
| `python3 scripts/search_stakes_reversal.py --samples 300 --seed 0 --diagnose` | `bea0537` | run `search-diagnose-20261028-043029-c8ed60`: counts identical to the table in § D-006 (grounded: 0 isolating reversals of 322; privileged_bounded: 18 of 744) |

- Manifests: `~/officeminds-runs/{tiny,search}/<run_id>/manifest.json`.
- Review bundle: `reports/bundle/tiny-manifest.json` (copy of the tiny manifest: commit `bea0537`, `git_dirty: false`) and `reports/bundle/trace-false_belief.json`. The trace keeps the agent view (no hidden names), the privileged block, and the robot graph separate: K(rec) is created at t0 with P(accurate) = 0.7, then goes stale as rec is seen again.
- Superseded (dirty-tree or pre-fix) runs kept on disk: `tiny-20261028-041404-4acb07`, `-041847-4f924f`, `-042301-2691f6` (pre-reversal), `-042818-825622`; `search-20261028-041107-078a13` (timing); the two killed searches (pre-fix definitions).

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
