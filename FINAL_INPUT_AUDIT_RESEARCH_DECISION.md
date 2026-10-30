# Final input-audit review and research decision

Date: 2026-10-30. Reviewed attachments: `AUDIT(1).md`, `source-ef77ad6.zip`, and `HASHES.sha256`. This closes the core input-contract question for the current templates. It does not authorize new model runs, spending, or a new environment.

## Decision in plain terms

The checker appears legitimate for the tested templates, once its task-specific engineering is disclosed. The stronger finding is that this environment admits a small exact CPU planner that performs substantially better than the reported LLM systems. We have useful evidence about protecting a weak policy from bad commitments, but we have not demonstrated the intended contribution: selecting whose mental state and which perspective path to compute at a competitive resource budget.

Stop development of this experimental configuration. Preserve its positive result and its limitations. Do not spend the remaining API budget on stronger models or another prompt revision to rescue this setup. I do not recommend presenting the current evidence as the intended spotlight-oriented allocation paper.

## What I independently verified

Both supplied files match their SHA-256 entries after accounting for the attachment rename from `AUDIT.md` to `AUDIT(1).md`.

I inspected the source and reran its CPU qualification. I also wrote a separate adapter that extracts the recipient, roster, layout, stakes and task from the rendered task-card string. It enumerates the supplied template library, retains byte-identical cards, builds a mixture model, and evaluates the regenerated frozen states. This adapter does not receive the instance's construction label, role mapping or distractor level. Hidden draws are used only to run the evaluation environment.

| Verification | Reproduced result |
|---|---:|
| Supplied relation-qualification checks | 1,008; zero mismatches |
| Supplied history-equivalence checks | 1,440; zero violations |
| Frozen states regenerated | 192 |
| Text-compiled versus instance-model initial value | Maximum absolute difference 0 |
| Initial best-action disagreements | 0 / 192 |
| Visible history identifies one surviving template pattern | 192 / 192 |
| Expected initial return under the text-compiled model | 0.884575 |
| Realized CPU-planner return on the frozen hidden draws | 0.871875 |
| Realized return, stakes ×1 / ×4 | 0.870833 / 0.872917 |

The combined qualification and text-compilation/planning run took about 27 seconds in this review environment. That includes exhaustive template matching and multiple reference calculations; it is not a deployment latency benchmark. No LLM calls were made.

This is an independent rerun and an additional input adapter, not an independently reimplemented simulator or exact planner. Both adapters use the supplied generator's template library and inference code.

## What the audit resolves

The deployed checker did receive generator metadata through `inst.scenario`. That input contract must remain disclosed. However, the reproduced initial-state equivalence shows that the same decision model can be reconstructed from the public text and history for all 192 tested states. The audit's explanation of metadata redundancy is credible for this finite template family.

Describe the system as a **symbolic checker using a hand-compiled public model of known templates**. Arbitrary language understanding, compilation of unseen templates, and its cost or reliability were not evaluated.

The realized planner figure is also confirmed, rather than merely an exact expected-value reference. Its 0.8719 return is numerically above the reported checker-gate return of 0.564, generic-gate return of 0.433, direct return of 0.303 and ask-first return of 0.270. It is a post-pilot CPU diagnostic using substantial task-specific engineering. It is not a preregistered condition or a general model benchmark. CPU time and engineering effort remain real costs.

## What remains unverified

The hash manifest names 18 exported files, but only the audit report and source archive were attached. The episode data, intervention records, per-check audit output, manifests, traces and source diff were not supplied. Therefore I have not reproduced the pilot's paired confidence intervals, the 380 logged checker comparisons, or the 384 logged episode replays. I also did not rerun the full test suite; pytest is unavailable in this review environment.

Keep those quantities labelled as agent-reported. The absent records should be retained in the project archive for any paper or external review. Their absence does not prevent the present stop decision: the independently reproduced CPU results already address the main methodological concern.

## What the research evidence supports

Retain the reported positive finding that a structured checker plus the gate intervention improves this local LLM's behavior. Retain the original fallback screening failure and the earlier clarification that its fixed cost tolerance was restrictive. Do not rewrite either outcome after seeing the data.

Do not attribute the rollout improvement to the proposed joint referent representation: the audit confirms that the deployed checker used `ExactOracle`, while `ReferentEngine` was exercised only in CPU qualification. No deployed marginal-versus-joint ablation isolates that representation's benefit.

Most importantly, this block supplies no evidence that selective mental computation beats computing and reusing the whole relevant model. The CPU findings undermine the resource premise of the current hybrid, while the planner exposes remaining weaknesses in the LLM's action selection.

## Instructions for the implementation agent

1. Record this decision and the corrected input contract in the project summary. Mark the current hybrid/fallback block closed.
2. Preserve the frozen protocol, source, pilot records, negative findings and positive checker result. Keep reported evidence distinct from reviewer-reproduced evidence.
3. Leave services stopped and the remaining API budget unspent. Do not start training, model comparisons, prompt revisions or a replacement environment under this review.
4. Before proposing another experimental block, prepare one short design argument showing why mental inference would be costly enough to allocate, why an inexpensive parse-once/dense tracker or exact planner would not remove that advantage, and how a matched-resource comparison would test the original question. Support it with explicit small examples and measurable acceptance/stop rules. A larger cast, more natural wording or a stronger model is not sufficient justification by itself.

The next research decision concerns the problem design. More runs of the present configuration will not resolve that design issue.
