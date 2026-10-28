# Round B summary: fresh-context value-of-notes check on dev-v3 (local backbone; development data)

**DRAFT for the Round B results gates.**

## What ran
- **Run:** `dev-v3-notes-20261028-165208-67f601`. Notes were frozen at commit `d5af211`, before any policy call. The dev-v3 freeze is at `984cb50` (generated at clean `7871e4c`); `verify` passed before each stage.
- **States and backbone:** 16 t0 states, the four variants of hash-selected groups 1c, 2a, 3c and 4b. Backbone: local gpt-oss-20b for both notes (temperature 0, max_tokens 1024, frozen) and policy (temperature 1.0, unseeded).
- **Scale:** 4 conditions × 3 draws = **192 episodes, 0 blocked**. Full tables: `roundB-results-local.md`.
- **Post-hoc descriptives** (labeled as such): `roundB-descriptive-local.md`.
- **Cost:** no paid calls; the API ledger is unchanged at USD 3.8690.
- **B2 API batch: not run.** The pre-declared condition (ledger ≥ USD 1.00 remaining) held: USD 1.1311 remained after reconciliation. But the expected cost exceeds the USD 0.80 stage allowance:
  - measured local prompts ≈ 1,490 tokens per decision call, at ≈ 3.1 decision calls per episode, for 64 episodes;
  - plus 24 note calls at the gpt-6.1-sol list price;
  - which gives ≈ USD 1.9 (estimate, not measured).
  - The ruling says to finish the local diagnostic and report the missing API confirmation when the check cannot fit, so the API confirmation is missing.

## Pipeline finding (before any policy outcome)
- 6 of 24 frozen inferred notes failed all 3 attempts, all of them reliability notes in 4b. The frozen pilot-v2.1 validator rejected them with `cites_non_visible_evidence` and `rule_citation_mismatch`.
- The likely cause: r6 adds a PUBLIC MODEL paragraph (the disclosed obstruction rates) that has **no citable evidence ID**, so a note that grounds its numbers in it cannot cite them. This is a dev-v3 ↔ pilot-v2.1 interface gap. It was not caught before the freeze.
- Per R11, those cells show no inferred note. The inferred condition in 4b is therefore partly "no note".
- In the 18 valid notes, every 1c, 2a and 3c note is correct_supported or supported_spread against the aligned public-model posterior. The two valid 4b notes split: R(uma) in ×1 perm1 is correct_supported, while R(zane) is unsupported_committed (cooperative 0.7, where the reference gives 0.045).

## Pre-declared reading (Entry 1a R10)

| condition | stratum 1 (control) | 2 | 3 | 4 | reading |
|---|---|---|---|---|---|
| inferred | inconclusive | inconclusive | positive | inconclusive | **inconclusive** |
| reference | null | inconclusive | positive | positive | **headroom present** |
| privileged | null | inconclusive | positive | positive | headroom present (never counted as deployable) |

## Why the positive reading is fragile (post-hoc, descriptive)
- **Outcomes over 48 episodes per condition:**
  - none: 3 errors and 1 timeout (2a ×4: give to the uninformed bystander, −2.05; 4b: two drops on the wrong report, −2.15 and −0.70; 3c: a timeout, −0.40);
  - reference: 1 error;
  - privileged: 0;
  - inferred: 3 errors, all in 4b, where most inferred notes were missing.

  The stratum-4 reference advantage (d_s 1.0 and 0.57 in two states) comes from those single −2.15/−0.70 `none` draws.
- **Median sensitivity:** recomputing the R10 classes with each cell's *median* of its 3 draws instead of the mean reads "no measurable explicit-note headroom" for every condition.
- **Noise floor:** in the 8 states where the reference and privileged prompts are byte-identical (1c, 3c), the per-state mean difference between them is pure policy sampling noise. It averages |0.023| (max 0.05).
- **Policy behavior:** the local policy almost always asks before acting. Its first action is in the exact Bayes-optimal set in only 6/48 (none), 9/48 (inferred), 6/48 (reference) and 3/48 (privileged) episodes, whereas the Bayes actor gives or drops at once. Success is 44–48/48 in every condition. Most of the remaining headroom is 0.05–0.15 of extra steps, not errors.
- **One mechanism-consistent pattern (3c; descriptive):** without notes, the policy often asks F and walks to F's *own* (new) meeting office, where R is not, because R was never told of the change. That costs 0.65–0.80. The K(F→R) note states R's view, which is R's location. The note is evidence-resolved under r6, so this is legitimate content, not a hidden-state leak, and it is the depth-2 inference the direct policy skipped. It rests on 4 states × 3 draws.

## Conclusion (proposed; for the gates)
- On dev-v3, with the local backbone, the pre-declared rule reads "headroom present" for the **reference** notes and "inconclusive" for the **inferred** notes.
- The reference reading depends on 3 rare catastrophic `none` episodes, and the median-of-draws sensitivity reverses it. So the result is **weak and fragile**, not a demonstrated effect.
- Inferred notes, the deployable candidate, show no reliable value. Their main measured problem is a pipeline gap: the public-model paragraph is not citable, which made 6 of 24 notes fail.
- Development data only; local backbone only; the API confirmation is missing.
