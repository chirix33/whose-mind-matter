# Round 2 summary: replicated value-of-notes diagnostic (development data; exploratory)

**Full tables:** `round2-results.md`, from `scripts/report_round2.py`, which implements the pre-registered analysis.

**Run:** `notes-value-20261028-085354-5b41df`, at clean commit `7c22105`.
- The frozen-note proof `round2-notes-freeze.json` was committed before the policy stage, and every injected payload hash was checked against it.
- 135 episodes: 9 states × 5 conditions × 3 policy draws. None blocked, 0 failed attempts.
- **API spend:** inferred notes USD 0.0610, policy USD 1.0379. Ledger total USD 2.9559 of the 5.00 cap.
- Counts are distinct: 9 scenarios, 1 frozen note per state × condition, 3 policy draws.

## What happened
1. **Ceiling.** Without notes the API policy already succeeds in 8 of 9 states (24/27 draws). Outside s9, return differences mostly reflect step counts (−0.05 per step).
2. **No condition meets the pre-registered "reliable" criterion.**

   | Condition | Mean Δ vs. none | Better / worse / tie states | Bootstrap 90% over states |
   |---|---|---|---|
   | inferred | +0.039 | 3 / 4 / 2 | [−0.035, +0.131] (reversed by dropping one draw) |
   | inferred_bare | +0.130 | 2 / 3 / 4 | — |
   | reference | +0.017 | 3 / 2 / 4 | — |
   | privileged | +0.057 | 5 / 1 / 3 | [+0.007, +0.115] |

   The inferred_bare gain is **entirely s9** (+1.30); without s9 it is −0.017. Privileged fails the useful-states test (2 of 4 positive).
3. **Privileged notes help a little, and mostly by revealing the target.**
   - Privileged episodes take 1.93 steps on average, against 3.07 without notes.
   - In s2, s4 and s5 the unit is K(recipient). The recipient's true belief about their own location **is** the delivery target, so the privileged note reveals it, and the policy acts on it at once (first action differs 3/3).
   - This is privileged-information dependence, not mental-state value.
4. **Reference notes ≈ none overall.**
   - The small gains sit in stratum B (s2 +0.10, s6 +0.13, s7 0). There the reference carries the generator's undisclosed base rates.
   - Stratum A (s3, n = 1): 0. Stratum C: −0.017.
5. **Inferred notes induce caution: it helps in one state and costs steps in confident ones.**
   - At s3, s5 and s8, inferred or inferred_bare notes change the first action or add steps where `none` acts directly (s3 −0.07/−0.10, s5 −0.08/−0.05, s8 −0.08/0).
   - Presentation matters in both directions: inferred − inferred_bare = −0.091 overall (+0.033 in A and B, −0.19 in C, driven by s9 and s8).
6. **s9, the one state with real headroom** (carryover label; K(dave)).
   - Dave saw the recipient Yara head to lab_north; Yara later moved, unseen. Dave sincerely answers "lab_north", a false belief.
   - none, reference (0.5/0.5, uncertain) and **privileged** (Dave believes lab_north, p = 1) all drop the package at lab_north: **0/3 successes each**.
   - inferred (lab_north 0.4, lab_south 0.4, unknown 0.2, with support): 1/3. inferred_bare (the same distribution, bare): **3/3**, each by checking both labs physically.
   - The true mental content did not help. It describes Dave's belief correctly, but the policy does not infer that the belief may be outdated (r5 rule 1 says it can be) and treats it as corroboration.
   - The successful notes differ from the failing reference note mainly by 0.2 mass on `unknown`. That mass is **unsupported** under the reference (posterior unknown = 0).
   - Candidate mechanism: expressed doubt about the informant triggers physical verification. The miscalibrated hedge helps because the policy fails to integrate an accurate false-belief note.
   - Evidence: one state, 3 draws per cell.
7. **Compute.**
   - Notes add decision-prompt tokens: inferred +29% (4,046 vs. 3,141 per episode); USD per episode 0.0092 vs. 0.0072.
   - Note generation (USD 0.0610 for 9 notes) is a one-time experimental cost, not free in deployment.
   - Privileged notes cut cost (0.0049) by shortening episodes.

## Pre-registered mapping
- No usable grounded value signal on these states, and no evidence of a pure inference limit: inferred ≈ reference by construction outside s2/s6, and stratum A has n = 1.
- The only consistent gain is privileged (+0.057, mostly fewer steps). It works by revealing the target through K(recipient) content: **privileged-information dependence**.
- The one large effect is a single-state, presentation- and uncertainty-driven gain (s9). Per the plan, Round 3 replicates it and runs one matched control.
- **Development-level reading:**
  - there is little headroom in 8 of 9 states (direct reasoning plus asking or physical search already succeeds);
  - the one state where mental content should matter shows **integration-limited** behaviour: accurate false-belief content is not used, while an unsupported hedge happens to help.

## Limitations
- 9 states and 3 draws. The states are a mixed diagnostic set, not certified cases of required mental reasoning.
- Single note draws.
- Presentation and status differ between inferred and computed notes; `inferred_bare` controls only part of that.
- The reference uses undisclosed generator knowledge in stratum B.
- All results are exploratory, on inspected development data.
