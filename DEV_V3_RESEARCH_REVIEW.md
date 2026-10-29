# dev-v3 research review and next-step decisions

Date: 2026-10-28. Scope: the completed dev-v3 qualification block. All results remain development findings. This review preserves the original research question and the existing USD 5 cumulative spending cap.

## 1. Where the project stands

The project is validating whether explicit mental-state computations provide a useful input to the decision policy. It has not yet demonstrated the value of learning to allocate those computations.

The original question remains: **which person, mental variable and directed perspective path should an agent compute, when, given the expected improvement in decisions and the cost of computation?**

There are three distinct requirements:

1. The task must contain decisions for which social information matters.
2. A deployable computation must produce useful mental content, and the policy must use it effectively.
3. Selecting computations must improve the return/compute tradeoff relative to the relevant baselines.

Round A makes progress on the first requirement under the declared scripted semantics. Round B finds a possible benefit from correct computed notes, but the deployable inferred-note pipeline still has problems. The third requirement has not been established: Round B used fixed allocations, not a learned router or a test of adaptive allocation.

The current result therefore supports another bounded diagnostic, not allocation training or a positive paper claim.

## 2. What the evidence establishes

### A fairer task and reference

dev-v3 discloses the public rules, priors and response model used by the reference. Visible social histories distinguish the important cases, and asking/search remain legal in the exact action-value calculations. The qualification includes same-physical-state social pairs, stakes changes, and a depth-2 contrast relative to the declared restricted policy class.

This addresses substantial fairness problems in the earlier pilot. It does not establish that a general LLM must instantiate a particular internal perspective representation, or that the declared people rules generalize to natural human behavior.

### Correct notes have a promising, uncertain signal

I independently recomputed these pooled descriptive numbers from the 192-row episode CSV:

| Condition | Mean task return | Successful episodes |
| --- | ---: | ---: |
| No separate notes | 0.668 | 44/48 |
| LLM-inferred notes | 0.700 | 45/48 |
| Public-model reference notes | 0.834 | 47/48 |
| Privileged notes | 0.865 | 48/48 |

These are raw returns, without charging note-generation compute. They come from four selected base scenarios, each expanded into stakes/name variants and repeated policy draws. They are not 48 independent scenario samples per condition. Privileged notes can reveal unavailable information and are a diagnostic only.

The report's pre-declared reading is reference headroom present and inferred inconclusive. That is a development screening rule, not a statistical demonstration of a general effect.

The reliability example is worth pursuing: the report records 5/24 errors across the no-note/inferred arms, versus 0/24 across reference/privileged. Those pooled arms differ in content and mechanism, however, and all variants share one hidden draw. Use the individual arm comparisons as the primary evidence; treat this pooled pattern as descriptive.

The gains depend heavily on a few costly failures. Removing those failures does not disprove the benefit: preventing them is potentially valuable under the original reward. It shows that this sample estimates that benefit imprecisely. Keep the failures in the primary return analysis.

### The inferred pipeline has two separable failures

- Five of 24 inferred notes failed validation after citing an invented public-model ID. Existing RULE6 citations sometimes passed, so the disclosed rates were not wholly uncitable; the interface did not provide a clear dedicated citation target.
- Six of eight reliability outputs copied prior probabilities rather than updating on the conflicting testimony. In the clearest example, cooperative probability remained 0.70 when the public-model posterior was about 0.045.

Fixing citations alone will not repair the second problem. Neither problem is evidence that a larger backbone will solve the original allocation question.

### Depth remains unresolved in the LLM experiment

In 3c, notes eliminated the three observed wrong-office visits. A first-order note about the recipient's belief could supply the same actionable content. Round B did not include that control, nor the 3a/3b certification pair. The result is consistent with correcting perspective confusion, but does not establish depth-2-specific value.

## 3. Decisions on the agent's three questions

**Q1 — Citation and inference fixes: approve one documented package revision.**

Give public-model facts stable, visible citation IDs and register them consistently in prompts, validation and rendering. Check that an unsupported invented ID is still rejected. Revise the inference instructions once to distinguish the prior from the posterior after observed testimony; preserve no-belief versus inference uncertainty/abstention. Do not supply realized hidden labels to the deployable unit.

Use the inspected cases for debugging and regression checks. Evaluate the frozen revision on fresh, preselected dev-v3 seeds. If another method component is introduced, such as an exact arithmetic tool, version and report it explicitly with its inputs and costs; do not silently replace LLM inference with the evaluator.

**Q2 — Headroom target: retain expected task return at a stated compute budget.**

Rare costly errors and unnecessary steps are two contributions to that same target. Keep return as the primary endpoint; report irreversible errors, timeouts, steps, and compute separately to explain it. Do not choose whichever secondary endpoint improves after seeing the next run.

No additional API funding is needed for the immediate repair and local diagnostic. Missing API confirmation limits the scope to the local backbone; it is not a reason to exhaust the remaining approximately USD 1.13 on an incomplete comparison. Existing discretion over local/cloud execution continues within the cumulative cap.

**Q3 — Depth controls: yes.**

Before any empirical depth claim, include the K(R) control and the 3a/3b contrast. Keep claims relative to the information and computation available to the compared policies. Do not infer an LLM's internal reasoning depth from its action alone.

## 4. Two additional controls needed in the next diagnostic

**Match the note interface.** The computed knowledge notes contain an extra probability that the belief or nested view is correct now. Inferred notes need not contain an equivalent estimate. Their content, evidence display and wording also differ. This was disclosed in the plan, but it means the reference-versus-inferred difference cannot be attributed entirely to inference accuracy.

For the primary typed-content comparison, render inferred and reference hypotheses through the same template with the same fields. Do not add the exact correctness probability only to the reference. Keep any correctness-augmented reference as a separately labelled diagnostic if needed. Retain citations for audit, with a consistent policy-visible display. No privileged or reference source label should function as an authority cue.

**Score the complete distribution.** A note labelled correct_supported can still assign substantial mass to impossible alternatives. The bundle contains 2a examples with about one-third unsupported probability mass despite that category. Report total variation against the aligned posterior, unsupported mass and valid-note coverage alongside categorical scores. A correct top guess is insufficient evidence of a faithful distribution.

## 5. Proposed next bounded block

At most two stages; no allocation learning, reward changes, new task templates, or model shopping in this block.

### Stage 1: repair and qualify the interface/package

Make the citation fix and one inference-package revision. Check visible inputs, citation validation, posterior scoring, and the matched typed-content renderer. Use old inspected cases only as development/debugging material. Freeze the package, prompts, model/decoding settings and evaluation protocol before generating fresh evaluation outputs.

### Stage 2: one local replication across fresh independent base scenarios

Predeclare the seed list, all included constructions, stratum weights, number of policy draws, local resource limit, and analysis before calling the model. Use the existing dev-v3 generator without changing its semantics or rates to favor notes. Include the STOP controls, first-order cases, the depth contrast and probabilistic cases.

Prioritize more independent base worlds over many repetitions of the same world. Pair conditions on the same underlying scenario and exogenous draws; pair stakes/name variants where used. These are scenario pairs, not a guarantee that LLM sampling randomness is shared or that repeated outputs are independent. Keep decoder settings fixed and justified for the intended policy. Model-sampling repeats remain nested within base scenarios.

Primary conditions are no notes, revised inferred typed notes, and matched public-model reference typed notes. Add only the declared first-order versus nested-note controls needed for the depth question. Privileged notes need not be repeated throughout the batch; earlier privileged gains do not establish deployable value.

Freeze inferred payloads before policy continuations. This estimates policy value conditional on the sampled notes; disclose that it does not measure repeated inference variability. Record all note failures, policy failures and retries. Do not drop difficult scenarios or replace failed outputs selectively.

Choose the sample size using an explicit precision/power calculation or simulation under stated assumptions and the local resource limit. The old four scenarios can inform exploratory planning, but do not treat their observed rates as known population rates. If the feasible design cannot resolve a practically meaningful effect, report that limitation rather than label it powered. If latent rare cases are deliberately oversampled, predeclare their sampling probabilities and the weights needed for the stated target distribution.

Analyze paired return differences across independent base scenarios, with appropriate grouping of variants and policy draws. Keep the error tail in the primary analysis. Report error rates and steps as secondary outcomes, and show results separately by construction and stakes. Do not use the four variants of one scenario as four independent scenarios.

Charge actual note-generation and decision compute, including failures and retries. Report raw return with tokens, latency and calls. Any scalar cost penalty must be fixed before outcomes; otherwise report the return/compute tradeoff directly. Equal task return at greater compute is not evidence for C1.

Before claiming that person-specific inference beats additional generic computation, include an appropriate budget-matched reasoning/summary baseline in the subsequent allocation study. The present fixed-note diagnostic alone cannot establish that claim.

### Stop and return

Return after this block without automatic training or another prompt revision. Provide the frozen protocol, independent scenario count, full paired results, note-fidelity distributions, compute accounting, representative traces, and a recommendation tied to these possibilities:

- Reference helps and inferred notes approximate it and help: propose a small allocation feasibility study, including unit/STOP value variation.
- Reference helps but inference fails: identify the bounded inference bottleneck; do not train the router to compensate for invalid content.
- Matched reference notes show no practically useful value within the achieved precision: report that outcome and reconsider the method/environment fit before more tuning.
- Uncertainty remains too large: report what effect sizes remain unresolved and the additional resources a resolving test would require.

A positive fixed-note result is still only a prerequisite. Allocation subsequently needs unit-specific and conditional values, informative STOP cases, and comparison against dense/random and other relevant selectors at matched compute.

## 6. Evidence reviewed and review limits

Read: FINAL_REVIEW, both round summaries, the experiment plan and amendments, qualification tables, reviewer reports, episode CSV, note-fidelity results, frozen-note metadata, example episodes, matched traces, and the supplied generator/pilot sources and source diff. The bundle also supplies the earlier block's requested evidence.

I independently reproduced pooled returns, outcome counts, step averages and policy-token totals from the episode CSV. Both bundled source files match their source hashes in the freeze. Of 23 bundled report/evidence hashes, 22 match byte-for-byte; the CSV hash matches exactly after converting its LF line endings back to CRLF. This is an export line-ending difference, not a numerical discrepancy. Preserve byte-level consistency in the next export; no rerun is warranted for that issue.

The 298 passing tests and exhaustive oracle checks are reported by the implementation agent and its reviewers. I did not rerun the full test suite or independently reproduce the complete oracle from this compact bundle. Review gates performed by other LLMs are useful checks, not external scientific validation.

A separate literature/deep-research agent is not needed to resolve the measured citation, posterior-update and sampling issues. A later targeted literature review can help position allocation baselines and the formal perspective-depth claim, after the empirical mechanism is stable.
