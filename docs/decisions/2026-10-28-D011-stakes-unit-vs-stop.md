# D-011 — Stakes isolation via unit-versus-STOP (Stage 1 review Q5)

- Status: **accepted** (Stage 1 research review, 2026-10-28). Amends D-006: a two-unit grounded reversal is no longer a prerequisite.

## Ruling
- Keep the privileged-bounded two-unit reversal (R(bob) vs K(carol)) as a **diagnostic, not grounded evidence**.
- **Approved now: a grounded unit-versus-STOP isolating test.** Defer any further search for two simultaneously flipping units.
- STOP has zero incremental task value and zero incremental instantiation cost. The preferred choice can therefore switch from modeling to STOP while the unit's flip label stays fixed. This addresses part of C2 and the STOP head. It does not prove better person selection between two positive-value units.
- With an illustrative price of 0.01 return units per one-call unit, held fixed across stakes: net +0.01909 (×1) > 0 = STOP, and −0.05689 (×4) < 0. This is not a measured cost.
- Before calling the pair isolating, verify every identifier and counterfactual:
  - same visible history except the declared stakes;
  - same prior, candidate set and inference output;
  - same baseline and post-computation actions;
  - same cost and tie handling;
  - zero carryover.
- Include the posterior-to-outcome table in the next bundle.
- **Q5-B** (averaging over histories) is a separate population-level diagnostic. Call it a *frequency over histories*, and weight value and flip terms consistently.
- **Q5-C** (realized LLM values) belongs in the pilot. Inject no sampling noise for fractional flips, and do not count identical temperature-0 repeats as independent draws.
- The restricted search's zero grounded hits is **not an impossibility proof** for other task families.

## Correction recorded here
The Stage 1 reports stated that the grounded `reversal_m*` units were worth "+0.029 at ×1 and 0 at ×4". That is wrong. An exact rerun gives K(bob), K(bob→carol), R(carol) = **+0.02908828 (×1), −0.04688857 (×4)**, each flipping move(hall) → drop(office_a) at both stakes with D_memory = 0. The error came from reading J(all) = J(∅) at ×4 as singleton values. Errata were added to the Stage 1 reports.
