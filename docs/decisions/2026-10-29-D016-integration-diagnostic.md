# D-016 — Repair-block review: one bounded integration diagnostic

- Status: **accepted** (research-driver ruling via Ashraf, 2026-10-29, `research-reviews/REPAIR_BLOCK_RESEARCH_DECISIONS.md`; repo copy `REPAIR_BLOCK_RESEARCH_DECISIONS.md`, sha256 `90b2bcfaee8dc02684be194e5238e10a30dbeed1d925dd308ca4e627e29853f9`)
- Affects: a new probe (single-decision contexts), an optional render component (an action-consequence mapping) and a status-display flag, a small API policy check, and how the repair-block result is cited.

Binding points, restated:
1. **The repair-block result stands.** Reference and inferred notes do not reach +0.05 for the tested configuration. That is not equivalence, not overall harm, and not proof that no subgroup benefits. Inference-prompt revisions and allocation training stop.
2. **The ≈ 0.50 Bayes gap is general task headroom,** not explicit-note headroom. The after-ask stale label cannot explain the increased first-action handoffs, which come before it.
3. **The approved diagnostic** keeps the environment, rewards, inference package, policy instructions, confidence wording and decoding unchanged. It has three parts:
   - (A) an audit of existing traces, with no model calls;
   - (B) a frozen probe on fresh seeds over 3b and 2b, plus positive controls 3a and 2a; 8 seeds × 2 stakes × 3 draws; exact reference notes only, frozen once and reused;
   - (C) matched decision contexts at t0 and after a standardized, predeclared ask. Conditions: t0 = none / content / content + implication; post-ask = none plus the 2×2 (implication × after-ask stale warning shown or omitted). That gives 1,536 single-decision calls.
4. **The implication line** comes only from the allocated typed content and the public transition rules, with distributions kept. It carries no hidden destination, true/false label, optimal action, Q-value or advice. It is an added, recorded reasoning component.
5. **Measures:** erroneous handoffs and drops, and the public-model action-value gap V*(h) − Q*(h, a). Results come per construction, stakes and context, with paired factor effects, interaction, and comparisons with no notes. Uncertainty is taken over independent base scenarios. The positive controls must keep correct handoffs.
6. **API check:** 8 hash-selected contexts (one t0 and one post-ask per construction), no notes vs content-only reference notes, giving 16 calls. One attempt each, no retries. At most USD 0.50 extra, and the cumulative total stays below USD 5. The worst case is verified and reserved before launch; if it can't fit, the check is skipped.
7. **Return after one consolidated report,** with the recommendation tied to §5's bullets.
8. **Corrections:**
   - the 3b example's cumulative return is −2.10 (−2.05 is its final action's reward);
   - keep exact exported bytes in hash manifests;
   - separate experimental note reuse from per-episode deployment cost.
