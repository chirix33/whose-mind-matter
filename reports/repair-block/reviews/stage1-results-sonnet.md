# Stage 1 results: independent numerical check (Sonnet 5.5)

Verdict: **CONSISTENT.** No numerical discrepancies. Two definitional or rounding remarks are listed at the end. No model calls were made and no repo file other than this report was changed. Scratch scripts are in the session scratchpad (`chk1.py` to `chk5.py`). All were run in WSL with `~/venvs/officeminds/bin/python`.

## 1. Stage 1 regression (`data/repair-block/regress-20261028-234117.json`, 28 rows)

| Quantity | Reported | Recomputed | Match |
|---|---|---|---|
| notes / valid / coverage | 28 / 28 / 1.0 | 28 / 28 / 1.0 | yes |
| mean TV (0.5·Σ\|p−q\|, all 28 rows) | 0.1172 | 0.117152 | yes |
| mean unsupported mass (mass on values with posterior < 0.2) | 0.1232 | 0.123236 | yes |
| per-row TV and unsupported mass vs stored values | n/a | 0 of 28 rows differ (tolerance 1e-9) | yes |
| categories | 21 correct_supported, 3 supported_spread, 4 unsupported_committed | same, derived independently from distribution, oracle truth and the 0.2 / 0.5 thresholds | yes (all 28 rows agree, not just the counts) |
| notes citing PM | 14 | 14 by `public_model_ids`; 14 by `kind == public_model` in the support lists (same notes) | yes |
| reliability prior copies | 5/8 | 5/8 | yes |
| private file vs public `stage1-regress-*.json` | n/a | rows identical apart from the omitted `call` field | yes |
| `distribution` vs the parsed hypotheses | n/a | agree on all 28 rows; every distribution sums to 1 within 1e-3 | yes |

Reference posteriors:
- I rebuilt all 28 reference posteriors with `officeminds.devgen3.generate(20261029)` and `vomi.oracle.ExactOracle`. The state IDs resolve as instance IDs of that seed.
- The maximum absolute difference from the stored `posterior` field is 0.

Hand derivations, independent of the oracle:
- **4b (R(kim), R(uma)):** the rates are r_X = 0.02 and r_Y = 0.3. The observed claims differ, and each claim is a specific office. The three consistent combinations are:
  - X obstructive, Y cooperative: 0.02·0.7/6 = 0.0023333.
  - X cooperative, Y obstructive: 0.98·0.3/6 = 0.049.
  - Both obstructive: 0.02·0.3/12 = 0.0005.
  - The total is 0.0518333.
  - P(X obstructive) = 0.054662 (stored 0.0546624). P(Y obstructive) = 0.954984 (stored 0.9549839).
- **2a, K(yara):** the history shows the announcement "office_b" and a quiet talk with yara after leo's move. The mover goes to office_a or office_c with probability ½ each. The posterior is 0.5 / 0.5, which matches the stored value. A model answer of office_b = 1.0 gives TV = 1.0 and unsupported mass = 1.0, which also matches.
- **2a, K(ravi):** ravi heard only the announcement, so the posterior is office_b = 1.0, which matches.

Prior_copy, row by row. The definition is |p_obstructive − prior| ≤ 0.02 with the reporter's own rate (X→0.02, Y→0.3):

| State | Unit | Role | p_obs | Prior | \|diff\| | Prior copy |
|---|---|---|---|---|---|---|
| 4b-s1-p0 | kim | X | 0.02 | 0.02 | 0.0000 | true |
| 4b-s1-p0 | uma | Y | 0.30 | 0.3 | 0.0000 | true |
| 4b-s4-p0 | kim | X | 0.0713 | 0.02 | 0.0513 | false |
| 4b-s4-p0 | uma | Y | 0.1765 | 0.3 | 0.1235 | false |
| 4b-s1-p1 | uma | X | 0.0297 | 0.02 | 0.0097 | true |
| 4b-s1-p1 | zane | Y | 0.30 | 0.3 | 0.0000 | true |
| 4b-s4-p1 | uma | X | 0.0001 | 0.02 | 0.0199 | true (borderline) |
| 4b-s4-p1 | zane | Y | 0.894 | 0.3 | 0.594 | false |

- The count is 5 true out of 8, as reported.
- The code also requires |p_coop − (1 − prior)| ≤ 0.02. That is equivalent here because each distribution sums to 1 within 1e-4.
- 4c has no rows in this run.

## 2. Power (`power.md` and `power.json`)

| Item | Reported | Recomputed | Match |
|---|---|---|---|
| `power.md` table (54 rows) vs `power.json` cells | n/a | 0 mismatches (rounding tolerance); probabilities sum to 1 in every cell | yes |
| RC5 rule | criterion met for no K; chosen K = 24 | feasible K are those with 8·K ≤ 240, so every grid value up to 24 is feasible. Under B, the best P(helps \| Δ=0.10) is 0.68 and the best P(no practical value \| Δ=0) is 0.265, both at K = 24 and both below 0.8. Largest feasible K = 24, i.e. 288 base scenarios and 3.2 h | yes |
| SE (A), eff 0.1 / null at K = 24 | 0.0229 / 0.0247 | 0.02285 / 0.02466 | yes |
| SE (B), eff 0.1 / null at K = 24 | 0.0352 / 0.0368 | 0.03523 / 0.03684 | yes |
| MDE at K = 24, A | ≈ 0.07 | (2.2414 + 0.8416)·0.02285 = 0.0705 | yes |
| MDE at K = 24, B | ≈ 0.109 | 3.083·0.03523 = 0.1086 | yes |
| K for P(helps \| Δ=0.10) ≥ 0.8, A | ≈ 12 | 24·(3.083·SE/0.10)² = 11.91 | yes |
| K for P(helps \| Δ=0.10) ≥ 0.8, B | ≈ 28 | 28.31 | yes (see remark 2) |
| K for P(no practical value \| Δ=0) ≥ 0.8, A | ≈ 46 | 24·((1.96 + 0.8416)·SE_null/0.05)² = 45.83 | yes |
| K for P(no practical value \| Δ=0) ≥ 0.8, B | ≈ 102 | 102.27 | yes (see remark 2) |
| Hours at 8 min per seed, A / B | 6.1 / 13.6 | 6.11 / 13.64 | yes |
| P(no practical value) and P(unresolved) under the null at K = 24, A / B | 0.5425 and 0.4525 / 0.265 and 0.715 | read directly from the cells | yes |

The method is z = 2.2414 (Holm p < 0.025, two-sided) plus 0.8416 for MDE and for the "helps" K. The "no practical value" K uses 1.96 + 0.8416 against the 0.05 margin. SE = half-width / 1.96, scaled by sqrt(24/K). The MDE and the "helps" K use the Δ = 0.10 cell's half-width. The "no practical value" K uses the Δ = 0 cell's half-width.

Cross-check of the normal approximation against the simulation:
- P(helps | Δ = 0.10, K = 24) is 0.984 (A) and 0.725 (B) under the normal approximation.
- The simulation gives 0.9625 (A) and 0.68 (B). It is lower because the simulation also requires a point estimate of at least δ.
- P(no practical value | Δ = 0) is 0.527 (A) and 0.273 (B) under the normal approximation. The simulation gives 0.5425 and 0.265.
- The extrapolations are therefore slightly optimistic for "helps" but otherwise sensible.

I did not re-run the Monte Carlo (400 simulations) itself. I only checked the stated extrapolation and the K-selection logic.

## 3. Worked example in `prompts/pilot-v2.2/unit_system.txt`

| Quantity | Stated | Recomputed |
|---|---|---|
| shelf_2 and truthful (0.25 × 0.65) | 0.1625 | 0.1625 |
| shelf_1 and misreporting (0.75 × 0.35) | 0.2625 | 0.2625 |
| total | 0.425 | 0.425 |
| P(obstructive \| "box = shelf_2") | 0.62 | 0.6176 |
| P(cooperative \| "box = shelf_2") | 0.38 | 0.3824 |
| for "box = shelf_1": truthful 0.75 × 0.65 | 0.4875 | 0.4875 |
| for "box = shelf_1": misreporting 0.25 × 0.35 | 0.0875 | 0.0875 |
| total | 0.575 | 0.575 |
| P(obstructive \| "box = shelf_1") | 0.15 | 0.1522 |
| uniform shelves: cooperative / obstructive after a statement | 0.65 / 0.35 | 0.65 / 0.35 |

All figures are correct at the stated 2-dp rounding. The Pat and Sam examples in the text state probabilities directly; they involve no calculation to check.

## Remarks (not discrepancies)

1. **Prior-copy definition.** The borderline "true" row (4b-s4-p1, uma: p_obstructive = 0.0001) is 200 times below the prior of 0.02. It passes the absolute ±0.02 tolerance (difference 0.0199) only because the X prior is itself tiny. It is a near-zero answer rather than a copy of the prior. Without this row the count is 4/8, so the tolerance rule is lenient for low-prior reporters. A relative rule, or a rule that also requires the posterior to differ from the prior, would not flag this row. The statistic therefore cannot separate near-correct answers from prior copying for low-rate reporters (the reference posterior for X is 0.0547, only 0.035 above its prior).
2. **K rounding in `power.md` and `power.json`.** The reported "K ≈ 28" (B, helps) and "K ≈ 102" (B, no practical value) are rounded values of 28.31 and 102.27. The smallest integer K satisfying the inequality is 29 and 103 respectively. For A, 46 comes from 45.83, which rounds and ceils to 46. These are labeled approximations, so this is a presentation point only.
