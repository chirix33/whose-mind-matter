# Review request — 2026-10-29 (method review, D-017)

**Read first:** `reports/method-review/METHOD_REVIEW.md`.

Supporting evidence (CPU-only, no model calls):
- `reports/method-review/audit.md` / `audit.json`: symbolic relationship audit and unit values under three actor definitions;
- `reports/method-review/selector-headroom.md` / `.json`: allocation headroom in the existing repair-block episodes;
- `reports/integration-block/INTERPRETATION-D017.md`: the corrected post-ask reading, with the hash-pinned files unchanged.

## Summary
- **Notes have zero value for a Bayes actor that reasons from the full history**, by proposition and checked numerically on 36 construction × stakes × actor rows. Any value must be a bounded-actor effect.
- **Free correct notes give the local actor no practical headroom.** Even with zero instantiation cost and a per-construction oracle choice, the gain is +0.044 in-sample and −0.001 cross-fitted. One instantiated unit costs about +63% of a no-note episode's tokens.
- **Notes expose only marginals; give(c)'s outcome depends on their joint.**
  - The robot's confidence in a destination is anti-aligned with handoff success across the constructions.
  - The pair K(F→R)+K(R) is the only representation that determines the 3b outcome. It does not determine 3a.
  - The typed "default holds" field equals the handoff's success probability, so rendering it would amount to action advice.

## Decisions requested
1. **Accept the recommendation to stop optimizing the current implementation** (dev-v3 + full-history LLM policy + per-unit LLM calls) for C1, or reject it.
2. **The optional closure test (§3–§5): approve, modify or reject.**
   - It is local, USD 0, about 1.5 h, 64 fresh seeds and 6,144 episodes.
   - Conditions: pair vs singletons, a redundant and an irrelevant control, an exact history digest, and a "think longer" control.
   - The stop rule is pre-declared, and a stop is the expected outcome.
3. **Whether any versioned redesign (V1–V4, §6) should be scoped later.** The candidates are a bounded decision context, relational unit content, long-history environments, and non-LLM unit computation. None is proposed for execution now.
4. **Accept the §1.2 compute definition and budget grid** as the accounting contract for any future run.
