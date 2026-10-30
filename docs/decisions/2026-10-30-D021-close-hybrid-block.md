# D-021: Close the hybrid/fallback block; next decision is problem design

- Status: **accepted** (research-driver ruling via Ashraf, 2026-10-30).
  - `research-reviews/FINAL_INPUT_AUDIT_RESEARCH_DECISION.md`; repo copy `FINAL_INPUT_AUDIT_RESEARCH_DECISION.md`, sha256 `bd75840a168b3f01d9a485fe203aef1b06c3061788ee556449f99204168e1ae9`.
- **Closes** D-019 and D-020. No new model runs, spending, training, model comparisons, prompt revisions or replacement environment.

## Binding points, restated
1. **Corrected input contract.** Describe the deployed checker as a **symbolic checker using a hand-compiled public model of known templates**.
   - It received generator metadata (`inst.scenario`), which the audit shows is output-equivalent to compiling the LLM's own task card for these templates.
   - Arbitrary language understanding, and compiling unseen templates, were not evaluated.
2. **Findings to keep, without rewriting outcomes:**
   - the positive checker+gate result;
   - the failed fallback screen, with the clarification that its cost tolerance was restrictive;
   - all negative findings.

   The rollout gain is **not** credited to the joint referent representation: the pilot used `ExactOracle`, and no marginal-vs-joint ablation was deployed.
3. **The intended contribution is not demonstrated.** This block gives no evidence that selective mental computation beats computing and reusing the whole relevant model. A small exact CPU planner reaches 0.8719 realized return, against 0.564 for checker+LLM.
4. **Evidence status.**
   - **Reviewer-reproduced:** 1,008 qualification checks; 1,440 history-equivalence checks; a text-compiled model equal to the instance model on 192/192 states (value and best action); planner 0.884575 expected and 0.871875 realized (×1 0.870833, ×4 0.872917).
   - **Agent-reported only:** the pilot CIs, the 380 logged checker comparisons, the 384 episode replays and the test suite (the episode records were not attached).
5. **Services and budget.** vLLM stays stopped. About USD 1.076 stays unspent.
6. **Before any new block:** one short problem-design argument. It must show:
   - why mental inference would be costly enough to allocate;
   - why a parse-once/dense tracker or an exact planner would not remove that advantage;
   - how a matched-resource comparison tests the original question.

   It needs small explicit examples and measurable acceptance/stop rules. A larger cast, more natural wording or a stronger model is not enough on its own.

## Delivered (2026-10-30)
- `reports/PROJECT_SUMMARY.md`: the project-level record, including the corrected contract and evidence status.
- `reports/design-argument/DESIGN_ARGUMENT.md`: a proposal only, with nothing started.
