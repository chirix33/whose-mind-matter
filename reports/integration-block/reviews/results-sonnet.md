# Integration block results: independent numerical check (Sonnet 5.5)

**Verdict: CONSISTENT.** No discrepancy found in the reported numbers. No model calls; no repo files modified except this report. Scratch code (own implementation, `scripts/report_integration.py` not imported or run) is in the session scratchpad: `chk1.py` (contrasts and readings), `chk3.py` (raw rates), `chk4.py` (oracle and world re-check), `chk5.py` (API). Runs were in WSL (`~/venvs/officeminds`).

## 1. Contrasts (item 1)

Base unit = (seed, construction); per condition and context the value is the mean over x1/x4 stakes and 3 draws (the same 6 decisions per condition). Estimate = mean over constructions of per-construction mean differences. Bootstrap = 10,000 resamples of seeds within construction (my own RNG, seed 12345). Sign-flip = exact, all 2^16 flips.

I recomputed all **72 reported contrasts** (3 metrics x 2 pairs x t0: 3 names; post: 7 names, plus the single-condition `condition-none` and `interaction` rows that results.json carries; every `primary|...` key in `results.json` was matched, none missing).

| Quantity | Max abs difference vs reported |
|---|---|
| point estimate | 5e-5 (rounding in the stored value only) |
| exact sign-flip p | 0 (identical on all 72) |
| bootstrap CI endpoints | 0.0125 (Monte Carlo and grid effect; different RNG seed) |

Interaction convention that reproduces the reported sign: (impl − content | omitted) − (impl − content | shown).

Key contrasts recomputed (mine; the reported values agree to the displayed precision, apart from CI endpoints noted):

| Context, metric, pair | Contrast | Mine: est [95% CI], p |
|---|---|---|
| t0 wrong, neg | content−none | +0.031 [−0.062, +0.135] p=0.719 |
| t0 wrong, neg | impl−none | +0.146 [+0.042, +0.260] p=0.077 (reported lower bound +0.031) |
| t0 wrong, neg | impl−content | +0.115 [+0.031, +0.198] p=0.045 |
| t0 wrong, pos | impl−none, impl−content | +0.010 [0, +0.031] p=1.0 |
| t0 correct, pos | content−none / impl−none / impl−content | −0.104 / −0.125 [−0.229, −0.031] p=0.038 / −0.021 [−0.083, +0.042] |
| t0 gap, neg | impl−none / impl−content | +0.282 [+0.063, +0.513] / +0.243 [+0.084, +0.415] p=0.014 |
| post wrong, neg | content\|shown−none / impl\|shown−none | −0.052 [−0.219, +0.104] / +0.000 [−0.073, +0.083] |
| post wrong, neg | impl_main / omit_main / interaction | +0.083 [−0.031, +0.208] p=0.252 / +0.083 [+0.016, +0.146] p=0.043 / +0.062 |
| post wrong, neg | impl_avg−none / omit_avg−none | +0.057 / +0.057 |
| post correct, pos | impl_main / omit_main / impl_avg−none / omit_avg−none | +0.047 / +0.078 / +0.115 / +0.130 |
| post gap, neg | impl_main / omit_main | +0.117 / +0.126 |
| post gap, pos | impl_main / omit_main | +0.035 / +0.017 |

All other cells (correct_handoff and gap for both pairs, both contexts) matched in the same way. Only CI endpoints ever differed (largest 0.0125); none is near a decision threshold except the two noted in section 2.

## 2. RC5 reading rules (item 2), applied by my own code

| Reading | Rule evidence (mine) | My reading | Reported |
|---|---|---|---|
| t0 \| implication (impl−content; vs impl−none) | neg wrong CI lower = +0.031 > 0 (harm criterion 1 met); also pos correct impl−none −0.125 [−0.229, −0.031] (not the factor row; factor impl−content −0.021 [−0.083, +0.042]) | harm | harm |
| post \| implication (impl_main; vs impl_avg−none) | neg wrong +0.083 [−0.031, +0.208]: CI includes 0 and point ≥ 0, no harm trigger (pos correct CI upper +0.125 ≥ 0) | neither (practically small) | neither (practically small) |
| post \| omission (omit_main; vs omit_avg−none) | neg wrong +0.083 [+0.016, +0.146], lower > 0, so harm | harm | harm |

- Sensitivity of "condition−none" at post: using `impl|shown−none` instead of `impl_avg−none` gives the same reading (neither).
- Closest-to-threshold item: the omission harm trigger rests on a lower CI bound of +0.016 (exact sign-flip p=0.043, pre-multiplicity); reported lower bound is +0.0156. The bound is on a grid of 1/96 units and was identical in both bootstraps, but it is a small margin. The t0 harm is on lower bound +0.031.
- The reports correctly say that omission "harm" means omitted > shown on wrong rate (shown is better); the `post|both` reading is correctly absent.

## 3. Raw rates (item 3)

I regrouped all 1536 rows into the 74 keys of `results.json["rates"]` (context | construction | stakes | condition, plus the 2a asked-role split via `integration-freeze.json["asks"]`: 10 H states, 6 N states). **All 74 keys match exactly**: n, wrong, correct, mean gap, fallback count and the full action-count dicts; no keys missing or extra.

3b wrong rate (correct handoff is 0 everywhere, as designed):

| Ctx | Stakes | none | content | impl |
|---|---|---|---|---|
| t0 | x1 | 0.042 | 0.167 | 0.375 |
| t0 | x4 | 0.083 | 0.167 | 0.333 |

| Post, stakes | none | content\|shown | content\|omitted | impl\|shown | impl\|omitted |
|---|---|---|---|---|---|
| 3b x1 | 0.417 | 0.417 | 0.458 | 0.583 | 0.542 |
| 3b x4 | 0.292 | 0.458 | 0.542 | 0.333 | 0.500 |
| 2b x1 | 0.458 | 0.167 | 0.292 | 0.208 | 0.500 |
| 2b x4 | 0.333 | 0.250 | 0.208 | 0.375 | 0.417 |

2b t0 wrong (x1: none/content/impl = 0.125/0.083/0.125; x4: 0.042/0.000/0.042). Each cell is n=24 decisions.

2a post-ask by asked role (wrong; correct handoff), conditions none / content\|shown / content\|omitted / impl\|shown / impl\|omitted:
- H asked (n=30 per cell): wrong 0.000 / 0.000 / 0.000 / 0.033 / 0.067; correct 0.50 / 0.47 / 0.57 / 0.63 / 0.60.
- N asked (n=18 per cell): wrong 0.167 / 0.056 / 0.000 / 0.000 / 0.056; correct 0.06 / 0.00 / 0.06 / 0.00 / 0.06.

Fallbacks: zero in all 8 context-conditions; failed attempts per context-condition (from the attempt records) 2, 0, 4 (t0 none, content, impl) and 0, 0, 2, 1, 2 (post none, content-shown, content-omitted, impl-shown, impl-omitted), matching `results.json["fallbacks"]`. Every (state, context, condition) has exactly 3 draws (512 cells).

## 4. Oracle gap and world outcome (item 4)

Rebuilt each context from `officeminds.devgen3.generate(seed)` (`inst.scenario.build(inst.hidden)`): t0 = `reset()` history; post = history after the frozen ask action from the freeze file (stepped on a clone, full two-step history). Gap = max Q − Q(action) from `vomi.oracle.ExactOracle.ranked_actions` on the plain posterior; `wrong` and `correct_handoff` from stepping a clone of the true world.

- 10 random decisions (seed 777): 10/10 identical (gap diff 0 to 1e-9, wrong, correct_handoff, Bayes-optimal set).
- Extension: **all 1536 decisions** recomputed (1.2 s): 0 mismatches, max |gap difference| = 0, 236 `wrong` decisions all reproduced, Bayes-optimal action sets identical to the stored `bayes_optimal`.

## 5. API check (item 5)

- The selection recomputed from the sha256 rule equals the frozen selection (4 states, 8 contexts, 16 calls; one attempt each; 16/16 finish `completed`; 0 fallbacks).
- Tokens (summary and raw records agree): 25,075 input, 494 output. Cost at USD 2/M in and USD 10/M out = USD 0.05509, equal to the reported `incremental_usd` 0.05509.
- Ledger: reconciled before 3.86895 (= spent, no unresolved or reserved), after 3.92404, difference 0.05509. The live ledger file (`~/officeminds-runs/api-spend-ledger.json`) now shows spent_usd 3.92404, 1130 calls, nothing reserved or unresolved. Remaining under the USD 5 cap: 1.07596.
- Worst case 0.42 <= 0.50 and stage cap 4.36895 = before + 0.50. The actual spend (0.055) is well under the cap.
- Oracle recomputation of all 16 API decisions: 0 mismatches. All 16 actions are Bayes-optimal (gap 0.000, no wrong deliveries) with and without notes, both contexts, so this check has no discriminating power on the note effect (it only shows the API model does not reproduce the local model's failures on these 4 states).

## Items for the reader (not discrepancies)

1. CI lower bounds differ from the reported ones by up to 0.0125 for resampling reasons (largest: t0 wrong neg impl−none, mine +0.042 vs +0.031); no reading depends on this.
2. Both harm readings are evidence of "wrong rate increases", not of benefit; the pre-multiplicity p of the post-omission contrast is 0.043 and of the t0 impl−content contrast 0.045 (16 units, 8 seeds per construction, descriptive).
3. The ambiguity in RC5 about what "condition−none" means at post (impl_avg vs impl|shown) does not change any reading.
