# Stage 2 summary: local replication of fixed-note value on fresh dev-v3 seeds (development data)

**Gated.**
- Opus: `reviews/stage2-results-opus.md`, PASS WITH REQUIRED CHANGES 1–8. All are applied here, together with the gate's must-not-claim list.
- Sonnet: `reviews/stage2-results-sonnet.md`, CONSISTENT. Its own code reproduces every number and the classification.

## What was measured
- **Method:** fixed explicit notes given at t0 to the local gpt-oss-20b policy.
  - Notes are not refreshed and stay visible with their t0 timestamp. The graph relabels a note "stale" after the robot asks its subject.
  - Package pilot-v2.2 with r7 content-only matched rendering: value distribution plus a robot-confidence line; no citations, no correctness line, no source label.
  - One backbone at reasoning effort low and temperature 1.0; 2 policy draws per state × condition.
- **Data:** 288 independent base scenarios. Seeds 20261100–20261123, each × the 12 dev-v3 constructions, each with its ×1 and ×4 variants: 4,032 episodes, 0 blocked, 0 fallbacks. Run `repair-stage2-20261029-132459-743ace`; frozen at `27c324e`; note proof `aa75046`.
  - **These seeds are now inspected development data and must never be reused as held-out.**
- **Conditions:** none; inferred (v2.2 notes, 856/864 valid); reference (the exact public-model posterior in the same format). In stratum 3 only, depth controls with a K(R) note in place of K(F→R).
- **Estimand:** the equal-weight mean over the 12 constructions and ×1/×4 of expected return, for new draws of these constructions.

## Pre-declared result (Entry 1a RC3/RC4)

| contrast | estimate | 95% stratified CI | sign-flip p (Holm) |
|---|---|---|---|
| reference − none | −0.024 | [−0.074, **+0.028**] | 0.387 (not significant) |
| inferred − none | −0.043 | [−0.098, **+0.013**] | 0.151 (not significant) |
| inferred − reference | −0.019 | [−0.066, +0.027] | — |

- **Classification:**
  - Reference: **no practical value**, since its CI upper bound +0.028 is below δ = 0.05.
  - Inferred: **fails**, since its upper bound +0.013 is below δ.
  - Pre-declared outcome: **D-015 §5(3), reconsider method/environment fit.**
- **Scope of the reading.** It holds for the pooled 12-construction estimand only. The per-stratum CIs still include +0.05 (reference upper bound +0.107 in stratum 1 and +0.087 in stratum 2).
- **It came from a negative point estimate, not from planned resolution.** `power.md` had predicted that a true null would most likely read "unresolved" (P ≈ 0.72 under variance B).

**Secondary results:**
- Outcomes (success / error / timeout over 1,152 episodes): none 880/205/67; inferred 866/240/46; reference 871/230/51.
- Headroom (Bayes V* − condition mean) is about 0.50 in every condition.
- The losses are concentrated in 1b, 2b, 2c and 3b, especially at ×4.
- One secondary contrast: inferred is harmful in stratum 4, −0.143 [−0.249, −0.035]. This is unadjusted for multiplicity.

## Why correct notes did not help (descriptive, from the traces)

| construction | condition | first action give(F) | ask, then give at step 2 | errors |
|---|---|---|---|---|
| 3a (give(F) correct) | none | 28 | 29/56 | 0 |
| 3a | reference (K(F→R) uniform, "low") | 12 | 43/77 | 0 |
| 3b (give(F) is the error) | none | 10 | 24/84 | 37 |
| 3b | reference (K(F→R) = announced office, 1.00, "high") | 28 | 23/52 | 58 |
| 3b | reference_KR | 12 | 42/79 | 58 |

Counts are over 96 episodes per cell.
- **3b.** The correct, high-confidence note implies that give(F) is wrong: F forwards to where F thinks R will go, which is the announced office, and the card states that rule explicitly. Yet the policy gives to F *more* often with the note than without it.
  - Example trace `s20261100-dev-v3-3b-stakes4-perm0` (reference): the robot asks F, hears the new office, then gives to F, ignoring both the forwarding rule and the note. Result: an error (−2.05).
- **2b.** The correct note (K(N) = announced office, high confidence) is read as the truth about R's location.
  - Trace `s20261101-…-2b-stakes4-perm0`: "she believes that value. So Bob likely at suite_3", then a drop to suite_3, an error.
  - The note's content does not say the belief is stale. That inference has to come from the history, and the policy doesn't make it. Errors: none 56, reference 55.
- **1b.** The errors are risky drops under genuine physical uncertainty; no mental note can prevent them.
- **Possible contributors (untested hypotheses):**
  - notes are relabelled "stale" after the robot asks their subject (62 of 96 3b reference episodes);
  - r7 shows content only, so the decision implication is left to the policy.
- **Round B did not cover 1b, 2b, 2c or 3b**, so its different note format (with a correctness line) can neither be blamed nor credited here.

## Depth controls (descriptive only; no C4 statement)
- **The difference-in-differences is negative:** reference notes help less in 3b than in 3a. (cond − none)[3b] − (cond − none)[3a] = −0.42 [−0.74, −0.09] for reference and −0.38 for inferred. The correct depth-2 note goes with *worse* 3b play.
- **Label-only controls move return by about 0.07.** In 3a and 3c the K(F→R) and K(R) reference notes have identical content (byte-checked: 0 of 96 states differ beyond labels), yet they move return by about 0.03–0.07.
- **The inferred 3a contrast (+0.34) is a timeout artifact** of the inferred K(R) condition (45 timeouts).

## Note fidelity and compute
- **Fidelity:**
  - Inferred notes are exact in strata 1, 2b and 4a (TV 0). They are poor in 2c (mean TV 0.47), 3a (0.58) and 3b (0.44).
  - 4b still has **14/96 diagnosable prior copies** (R1 count).
  - 12 inferred episodes show no note, under the declared fallback for an invalid note.
  - Because reference notes also show no value, the inferred failure **cannot** be attributed to note fidelity.
- **Compute:**
  - Inferred notes cost 883 attempts: 2.42M prompt and 0.48M completion tokens, of which 0.31M are reasoning tokens. That is the deployable overhead, and it bought no return.
  - Decision attempts per condition are about 3,500–3,600 (Sonnet notes that "decision_calls" in the report counts attempts, retries included).
  - The reference oracle used 1.53 s CPU and is not deployable.
  - Wall clock: notes 9.3 min and policy 39.4 min, at concurrency 8.

## What this does NOT show
- It does not show that mental-state notes or ToM have no decision value in OfficeMinds, nor that C1 or C2 is refuted.
- It does not show that reference notes significantly harm overall; the CI includes 0. Only the 3b-specific difference-in-differences is a descriptive harm signal.
- It gives no depth (C4) evidence.
- It does not show that the inferred failure is caused by note fidelity.
- It does not show that the r7 renderer or the stale label caused the null result.
- It has no confirmatory status, and nothing here bears on Tier 2 or Menti-Bench.
