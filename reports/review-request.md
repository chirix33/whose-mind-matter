# Review request — 2026-10-29 (repair-and-validation block, D-015, final)

**Read first:** `reports/repair-block/FINAL_REVIEW.md` (recommendation first). Details are in `reports/repair-block/stage2-summary.md`; gate reports are in `reports/repair-block/reviews/`; the bundle index is `reports/repair-block/evidence/README.md`.

The previous request (the dev-v3 block) was answered by D-015.

**Pre-declared outcome: D-015 §5(3), reconsider the method/environment fit.** On 288 fresh base scenarios with the local backbone:
- reference − none is −0.024 [−0.074, +0.028], "no practical value";
- inferred − none is −0.043 [−0.098, +0.013], "fails";
- headroom against the exact Bayes actor is about 0.50.

## Decisions that need research review
1. **Accept §5(3), and decide what to reconsider:**
   - policy integration: the policy does not turn correct notes into correct actions. In 3b a correct note *increases* the wrong handoff, 28 vs 10 of 96;
   - or the environment's suitability for explicit mental notes.
2. **The proposed 3b/2b 2×2 diagnostic** on fresh seeds: content-only vs content plus decision-implication rendering, × the after-ask stale relabel on vs off, compared with the exact Bayes actor. It changes the rendering method, so it needs approval, modification or rejection.
3. **Whether a stronger policy backbone is in scope** as a separate integration check. The ledger stands at USD 3.869 of 5; no spending is proposed without a decision.
