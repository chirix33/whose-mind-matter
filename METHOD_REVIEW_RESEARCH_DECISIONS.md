# Method-review research decisions

Date: 2026-10-29. Review of METHOD_REVIEW.md, selector-headroom.md, audit.md and INTERPRETATION-D017.md. Retain development-only status and the original question: choosing whose mind, which variable and which directed perspective path to compute by decision value under compute constraints.

## 1. Stop optimizing this implementation

Accept the operational recommendation: stop optimization of dev-v3 + full-history local policy + separate LLM calls per unit. Keep allocation training on hold. Do not launch the proposed 6,144-episode closure test, another prompt variant, seed sweep or backbone comparison.

This is a resource and research decision supported by repeated unsuccessful tests, substantial inference cost, and no demonstrated deployable allocation benefit. It is not an impossibility theorem and does not close the original research question.

The pair hypothesis remains untested. An untested hypothesis need not receive another experiment merely for closure. The proposed perfect-note test also uses imputed instantiation costs rather than measuring an implemented matched-compute system. Even a pass would require more method and deployment work. Its expected information value is insufficient to justify extending this optimization sequence now.

No further LLM calls or paid spending follow from this review. Preserve the remaining approximately USD 1.076.

## 2. Correct the scope of the arguments

### Bayes proposition: accept with precise wording

A reference note that is a deterministic function of the visible history and declared public model supplies no new external information to an ideal reasoner already conditioning on both. This is a basic information-boundary observation, not a newly discovered reason that computational assistance cannot work.

Distinguish the **computed posterior distribution** from the **person's realized mental state**. The former can be a deterministic function of h; the latter is often unresolved by h in these tasks. Do not write that all realized unit contents are determined by the history. Privileged revelation of a realized value is a different operation.

For a bounded policy, deterministic processing of h can improve decisions. Its value must be measured for that policy with its cost, rather than inferred from the Bayes proposition.

### Selector headroom: restricted diagnostic, not a ceiling

I independently reproduced the in-sample +0.04405 gain using the existing repair-block CSV and selecting among the tested conditions within each of 24 construction/stakes cells. The reported cross-fitted estimate is -0.0012.

This provides no convincing evidence for useful selection in that restricted class. However:

- The selector chooses once per cell, not separately for every visible state/history.
- It considers only the recorded conditions, not all unit subsets, pairs, refresh schedules or conditional allocations. Some recorded main conditions already contain multiple focal notes; do not label the entire analysis a single-unit experiment.
- A selector using visible state differences can perform differently from a cell-level selector. The latter is not an upper bound on the former.
- The cross-fitted interval includes gains exceeding +0.05, and the report acknowledges leakage in the bootstrap procedure. It cannot establish practical equivalence to no gain.

Revise “free correct notes have no practical headroom” to “the tested cell-level selection procedure has not demonstrated a practical gain.” Preserve the estimates and report the interval limitations; no new model run is needed.

### Cost: correct the denominator

From the repair-block freeze and compute records:

| Quantity | Recorded/recomputed value |
| --- | ---: |
| Requested primary inferred units | 720 |
| Attempts, including retries/failures | 883 |
| Note prompt + completion tokens | 2,899,389 |
| Tokens per attempt | 3,283.57 |
| Tokens per requested unit | 4,026.93 |
| No-note decision tokens per episode | 5,230.43 |
| Per-requested-unit cost / baseline episode cost | 77.0% |

The approximately 63% figure compares **one attempt**, not a complete requested unit, with a baseline episode. Charge all attempts to the request, then add retained-note rendering. Do not amortize note generation across experimental policy draws as if they were independent deployment episodes.

This cost is a substantial practical disadvantage. It does not mathematically prove that the method cannot win at matched compute: a note could change decision-call count, reasoning length, success or return. The bounded-context estimate likewise assumes behavior/call counts rather than measuring the redesigned policy. Treat the 56% estimate and break-even history length as conditional planning estimates, not performance bounds. Use the actual tokenizer before any future cost claim based on character counts.

### Symbolic labels and memory effects

Accept that the existing symbolic actor is not a validated allocation-label source for this implementation. Its arbitrary face-value default should not be used to manufacture a positive training signal.

Do not redefine D_memory as episode return difference minus a single-decision probe effect. Probe Q-values use a declared continuation policy; episode returns include subsequent policy changes. The earlier action/memory decomposition requires matched interventions and a common continuation definition. Without those, report first-action and episode effects separately, without a causal residual labelled memory value.

## 3. Accept accounting principles, not a blanket matched-compute claim

Accept all-call accounting: decision, inference, controller, summary, retries, failures, retained rendering, and feature-extraction calls. Keep prompt, completion/reasoning tokens, calls and latency separately visible.

Total processed tokens are a useful within-backbone budget proxy. They are not interchangeable with wall-clock time or hardware cost, and equal total tokens need not imply equal runtime. Keep caching and prefill/decode distinctions visible where they affect the claim.

B0, 2B0 and 3B0 may be retained as provisional planning points. The ±10% matching tolerance needs to be justified against the intended comparison; it is not a general permission to call arbitrary operating points matched. Perfect reference notes charged a proxy cost belong in a labelled sensitivity analysis, not an empirical matched-compute result for deployable inferred notes.

## 4. Scope a redesign concept only

Do not launch V1–V4. If the project continues, the next deliverable is one research concept, with the original objective retained, that addresses both:

1. **Decision-relevant relations.** Specify how the perspective representation exposes or permits computation of dependencies between people's beliefs, rather than only unrelated marginals. A fact derived from legal history is not privileged information merely because it helps choose an action. Nevertheless, inserting evaluator-computed success probabilities would be a different method component requiring explicit provenance, cost and comparison; it must not be silently introduced as ordinary belief content.
2. **A meaningful computation constraint.** Specify why selective perspective computation should beat dense processing or generic extra reasoning at the declared budget. Longer history is a possible regime, but should arise from a substantive sequential task, not padding chosen to make the method favorable. Cheap symbolic tracking does not automatically make dense processing dominant for a bounded actor: rendering, attention, refresh and interference can still matter and must be assessed.

Do not hide the history from the direct baseline to create a win. If the proposed system uses compressed memory or bounded context, retain credible full-history and generic-memory baselines with complete costs. Distinguish information access from resources consumed to process it.

State exactly which original definitions remain and which change. Retain return at matched compute as primary, legitimate ask/search actions, informative STOP cases, and controls for redundant/complementary computations. Do not replace the project with a study of coaching a weak policy through selected examples.

The concept should include a small comparison matrix, a causal explanation of the proposed value, a resource forecast and explicit reasons to abandon it. It should not contain a new experiment authorization or claim that a positive outcome is expected.

If no convincing concept meets these requirements, freeze and document the current negative development findings rather than force a positive allocation paper.

## 5. Review limits

The symbolic audit tables and cross-fit results are supplied by the implementation agent; their scripts and raw JSON outputs were not attached in this turn. I independently checked the cell-selector point estimate and the retry-inclusive cost using the earlier repair-block CSV, freeze and compute records. I did not independently execute the new symbolic audit or reconstruct its cross-fit splits.

The D-017 interpretation correction is appropriate. Preserve the earlier frozen outputs and their corrected interpretation side by side. No confirmatory, allocation, depth or transfer claim follows from these analyses.
