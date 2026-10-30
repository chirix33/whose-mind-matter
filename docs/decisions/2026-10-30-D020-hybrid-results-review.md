# D-020: Results review of the hybrid block; close it with an evidence audit

- Status: **accepted** (research-driver ruling via Ashraf, 2026-10-30).
  - `research-reviews/HYBRID_FALLBACK_RESULTS_REVIEW.md`; repo copy `HYBRID_FALLBACK_RESULTS_REVIEW.md`, sha256 `3b41ed1436de73c92ac1e40c5c7090f704b0f13d5639df8ccbc45a04c46d1d25`.
- Closes D-019. **No new model runs, seed sweeps, prompt changes, environment builds or paid calls.** About USD 1.076 stays unspent.

## Binding points, restated
1. **Hybrid:** closed in this regime. Shared enumeration makes every tested relation inexpensive.
2. **Fallback:** keep the frozen *failed* classification (criterion (b) vs ask-first). It is not reinterpreted as a pass.
   - The rule was a restrictive screen. +0.294 for 1.26× tokens may be a worthwhile tradeoff, so the failure is not evidence that the checker lacks efficiency value.
   - Future protocols should use a predeclared return/resource frontier or a justified fixed budget. This study is not rerun to obtain a pass.
3. **Positive finding kept separately:** a public-model symbolic checker plus an action gate improves the local policy and beats its generic LLM checker. These are different operating points, not matched compute.
   - No deployed marginal-vs-joint ablation was run, so the gain is not attributed to the joint relational representation.
4. **Bayes reference:** it is an expectation and reference calculation, not a head-to-head rollout. Before any claim, verify the input contract, distinguishing:
   - a public model compiled from the same task card and history the LLM sees;
   - task-specific engineering supplied in advance;
   - simulator Scenario objects, role mappings, construction IDs or priors unavailable to the agent.
5. **No regime change yet:** natural-language role-play does not automatically create an allocation bottleneck, and a parse-once tracker may still suffice. Evidence of that bottleneck must come first.
6. **Deliver an evidence bundle from existing artifacts:**
   - protocol, configuration, prompts, seeds, manifests, source/diff;
   - engine, gate, input adapter, qualification script, planner, tests;
   - per-episode CSV/JSON with analysis;
   - veto records with evaluator-only fields separated;
   - representative traces;
   - Bayes-reference inputs and the input-contract explanation;
   - exported-byte hashes and the ledger.
7. **Wording correction for 3c:** "consistent with sampling variability; no check fired in the cited failing checker episodes."

Services stay stopped.

## Outcome (2026-10-30; awaiting research review)

Delivered `reports/hybrid-block/audit/AUDIT.md` with an exported evidence bundle (`HASHES.sha256`).
- **Input contract:** the checker and the Bayes reference received the per-instance generator Scenario object (construction ID, role mapping).
- **Equivalence:** a model compiled from the LLM's own task card gives identical outputs (380/380 checks; 192/192 t0 values and actions), and the history always pins one pattern. This relies on hand-compiled templates (task-specific engineering).
- **Planner:** realized deterministic return on the same hidden draws is 0.872 (expectation 0.885). This is a CPU evaluation, not a pilot condition.
- **Wording:** the 3c sentence is corrected.
- **Ledger:** unchanged at USD 3.924.
