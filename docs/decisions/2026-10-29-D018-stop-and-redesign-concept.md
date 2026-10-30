# D-018 — Method-review ruling: stop optimizing this implementation; scope one redesign concept

- Status: **accepted** (research-driver ruling via Ashraf, 2026-10-29, `research-reviews/METHOD_REVIEW_RESEARCH_DECISIONS.md`; repo copy `METHOD_REVIEW_RESEARCH_DECISIONS.md`, sha256 `b22014600431317b8fd07e623a382532433f7e2d45ce5c9bec9c6186468822f9`)
- Affects: everything after D-017.
  - `reports/method-review/METHOD_REVIEW.md` is corrected in place.
  - The deliverable is `reports/redesign-concept/CONCEPT.md`, a concept only.

Binding points, restated:
1. **Stop optimizing the implementation:** dev-v3 + full-history local policy + per-unit LLM calls.
   - Allocation training stays on hold.
   - The 6,144-episode closure test is not launched.
   - No prompt variant, seed sweep, backbone comparison, LLM call or paid spending. About USD 1.076 is preserved.
   - This is a resource and research decision, not an impossibility result. The pair hypothesis stays untested.
2. **Corrections to the arguments:**
   - (a) The Bayes proposition concerns the *computed posterior*, not a person's realized state. A bounded policy can benefit from deterministic processing of h, and that value must be measured with its cost.
   - (b) The selector result is a restricted cell-level diagnostic. It is not a ceiling for state-level selection or for untested subsets. Its interval cannot establish equivalence to zero gain.
   - (c) Charge all attempts per requested unit: 4,026.93 tokens, which is 77.0% of the 5,230.43-token no-note episode. Add retained rendering, and do not amortize across experimental draws.
   - (d) Bounded-context cost figures are conditional planning estimates. Use the actual tokenizer before any cost claim.
   - (e) Do not define D_memory as an episode-minus-probe residual. Without matched interventions under one common continuation, report first-action and episode effects separately.
   - (f) The existing symbolic actor is not a validated label source here.
3. **Accounting principles:**
   - All-call accounting, with prompt, completion/reasoning, calls and latency each visible.
   - Total tokens are a within-backbone proxy. They are not time or hardware cost, and caching must stay visible.
   - B0/2B0/3B0 are provisional planning points, and a matching tolerance must be justified per comparison.
   - Perfect notes with a proxy cost belong only in a labeled sensitivity analysis.
4. **Redesign concept only:** V1–V4 are not launched. If the project continues, deliver one concept that addresses:
   - decision-relevant relations between beliefs, without silently inserting evaluator-computed success probabilities;
   - a meaningful computation constraint arising from a substantive task, not padding, without hiding history from direct baselines. Full-history and generic-memory baselines stay, with complete costs, and information access is kept distinct from processing resources.

   The concept states what is retained and what changes, includes a small matrix, a causal explanation, a resource forecast and reasons to abandon, and makes no authorization and no expected-positive claim. If no convincing concept exists, freeze and document the negative findings.
5. **Review limits:** the reviewer reproduced the selector point estimate and the cost figures, but not the new symbolic audit.
