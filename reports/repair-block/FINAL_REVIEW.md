# Repair-and-validation block (D-015): final review for the research conversation

All results are development data on the local backbone (gpt-oss-20b). Every stage was gated: Opus checked validity, and Sonnet independently recomputed the numbers. Dates: 2026-10-28 to 2026-10-29. The work was interrupted by two machine restarts, with no data loss.

## Recommendation
1. **The pre-declared outcome is D-015 §5(3): reconsider the method/environment fit before more tuning.** On 288 fresh, independent base scenarios, correct notes matched in format (reference) gave no practical improvement in return: −0.024, 95% CI [−0.074, +0.028]. The generated notes failed: −0.043 [−0.098, +0.013]. Do not start allocation training.
2. **What the result actually points to: a gap between correct content and how the policy uses it.** The environment has plenty of headroom: the ideal Bayes actor beats the LLM policy by about 0.50 per episode, concentrated in 1b, 2b, 2c and 3b. But the policy does not turn correct mental content into the right action.
   - In 3b, a correct note saying where the courier thinks the recipient will go makes the policy hand over to the courier *more* often (28 vs 10 of 96), although the card's forwarding rule makes that an error.
   - In 2b, a correct note about a stale belief is read as the truth.
3. **Proposed diagnostic (needs review, because it changes the method).** A small 2×2 on fresh seeds, restricted to 3b and 2b:
   - factor 1: content-only rendering vs content plus a stated decision implication (for example "if handed to F, F forwards to desk_14");
   - factor 2: the after-ask "stale" relabelling on vs off.

   Each cell would be compared with the exact Bayes actor's value. This separates "the content has no value" from "the policy doesn't integrate it".
   - A zero-cost precursor can be run now from existing traces: how often step reasoning refers to the note value, and the actions taken under stale vs fresh notes.

## What was done
**Stage 1: repair and qualify** (`experiment-plan.md` Entries 1, 1a, 1b, 1c).
- **The one package revision, pilot-v2.2:**
  - citable public-model IDs `[PM<n>]`, with invented IDs rejected;
  - one prior-vs-posterior instruction section, whose worked example was replaced before any call because the gate found it isomorphic to 4b/4c;
  - an r7 matched renderer: the same template and fields for every note source, canonical ordering, confidence wording about the robot's estimate, no correctness line;
  - full-distribution scoring.
- **Regression check** on inspected states (development only): coverage rose to 28/28 (Round B: 19/24), and 2 of 4 diagnosable reliability notes still copied the prior.
- **Precision simulation:** K = 24, the largest K within the resource limit (the criterion was not met; limitations in `power.md`).
- **Symbolic qualification:** all 576 fresh-seed states pass.
- **Freeze:** `27c324e`.

**Stage 2: local replication** (`stage2-summary.md`, `stage2-results.md`).
- 4,032 episodes, 0 blocked; notes took 9.3 min and policy 39.4 min.
- The results are above under Recommendation.
- **Depth:** descriptive only. The reference difference-in-differences (3b − 3a) is −0.42 [−0.74, −0.09], so the correct depth-2 note goes with worse 3b play. There is no C4 claim.
- **Note fidelity:** good in simple cases, poor in 2c/3a/3b; 4b still shows 14/96 diagnosable prior copies.

## What the result does NOT show
- That mental-state notes or ToM have no value, or that C1/C2 is refuted.
- That reference notes significantly harm overall (the CI includes 0).
- Any depth result.
- That the inferred failure is due to note fidelity.
- That the renderer or stale label caused the null (these are untested hypotheses).
- Any confirmatory, Tier 2 or Menti-Bench result.

**Scope of "no practical value":**
- It holds only for the pooled 12-construction estimand. The CIs for strata 1 and 2 still include +0.05.
- It came from a negative point estimate, not from planned resolution: the planning simulation expected a true null to read "unresolved".
- Seeds 20261100–20261123 are now inspected development data.

## Decisions for the research review
1. Accept the §5(3) reading, and decide whether the method/environment question is about **policy integration** (the 2×2 above) or about the **environment's suitability** for explicit mental notes.
2. Approve, modify or reject the 3b/2b 2×2 diagnostic. It changes the rendering method, so it needs review.
3. Decide whether a stronger policy backbone is in scope as a separate integration check. There was no API spending in this block; the ledger is at USD 3.869 of 5.

## Status
- Code at `main` HEAD; 305 tests pass.
- No paid calls in this block.
- The vLLM server is stopped. No cloud sessions were used.
- Bundle: `evidence/README.md`.
