# Review request — 2026-10-28 (dev-v3 qualification block, final)

**Read first:** `reports/dev-v3-block/FINAL_REVIEW.md` (recommendation first). Per-round gated conclusions: `reports/dev-v3-block/roundA-summary.md` and `roundB-summary.md`. Reviewer reports: `reports/dev-v3-block/reviews/`. Bundle index: `reports/dev-v3-block/evidence/README.md`.

The previous block's request (`reports/autonomous-block/FINAL_REVIEW.md`) was answered by D-014.

## Decisions that need research review
1. **Package revision.** Give the public-model block citable IDs, and make reliability notes integrate conflicting testimony with the disclosed rates. Then validate on fresh dev-v3 seeds. Measured on dev-v3: 5 of 24 notes failed because the model invented a `PUBLIC_MODEL` ID, and 6 of 8 4b outputs copied the prior.
2. **Headroom target and design.**
   - The local policy succeeds in 44–48 of 48 episodes in every condition.
   - The reference reading "headroom present" rests on 3 rare `none` failures and is inconclusive without them.
   - The clearest pattern is single-group: in 4b, 0 errors in 24 episodes with a correct reliability posterior vs 5 in 24 without.

   Choose whether to target the error tail (rare costly errors at ×4 stakes) or step efficiency, and approve a design powered for it. That includes whether to fund the missing API backbone check; about USD 1.13 of the original cap remains.
3. **Depth-2 evidence.** Should any depth-2 claim require a K(R) depth-1 control? (In 3c the useful note content equals R's own belief.)
