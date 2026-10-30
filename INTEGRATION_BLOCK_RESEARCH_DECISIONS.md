# Integration-block research decisions

Date: 2026-10-29. Research review of D-016. All findings remain development results. The original objective is decision-value allocation over people, mental variables, and directed perspective paths under compute constraints.

## Decision

**Stop the present content/display tuning sequence. Do not train an allocation controller, expand this probe, start a new backbone comparison, or redesign the environment yet.** Complete a method-level specification review before proposing another LLM experiment.

The completed block follows the planned stopping branch: neither intervention demonstrated useful repair. The unresolved post-ask effect does not, by itself, justify resolving it with another 45–50 seeds per construction. There is no supported practical integration component to validate at episode level.

## What the evidence says

The local experiment contains 1,536 single-decision probes, with four constructions, eight seeds per construction, two stakes levels, and three policy draws per prompt. It does not estimate rollout return.

In the problematic 3b case, immediate wrong handoffs were:

| Input | Wrong handoffs |
| --- | ---: |
| No notes | 3/48 |
| Correct typed notes | 8/48 |
| Correct typed notes plus forwarding implication | 17/48 |

I reproduced these counts and the main paired effects from the CSV. Across the negative pair, adding the implication raised the t0 wrong-action rate by 0.1146 relative to content only. Omitting the stale warning raised the post-ask wrong-action rate by 0.0833, averaged over the presentation factor.

The reported harm readings remain descriptive. They do not survive the reported Holm correction across the three readings, and the experiment has only sixteen independent base scenarios per construction pair. Do not describe either intervention as generally harmful or beneficial.

The post-ask implication estimate, +0.083 wrong rate with CI [-0.036, +0.208], is unresolved. The generated results.md still calls its reading “neither (practically small)”; preserve that as the historical classifier output and add the corrected interpretation: **no demonstrated help; harm not excluded; magnitude unresolved**. Do not silently rewrite the frozen classifier.

The positive controls did not establish selective improvement. Omitting the warning increased correct handoffs as well as wrong ones, consistent with a broad action/caution effect rather than improved discrimination. More correct handoffs alone would not establish better decisions: the evaluator's action-value gap also matters, and asking may be a low-cost legal alternative.

The API check used eight contexts, one response for each no-note/reference pair. All sixteen actions were Bayes-optimal and each pair selected the same action. I verified those recorded counts and the USD 0.05509 cost. This is consistent with a limitation of the local policy configuration, but not a model benchmark: sampling, caps, effort semantics and attempts differed. It supplies no evidence of a note benefit at the observed ceiling and no full-episode result.

## Answers to the three research questions

### 1. Complements, backbone, or environment?

Review the **relationship between representation, actor and computation budget** before selecting one of these explanations.

The current evidence brackets the problem: the local configuration fails to use correct partial mental content reliably, while the small API sample solves the selected decisions without separate notes. Neither observation establishes useful adaptive computation. Do not respond by searching for a backbone or task variant on which the method wins.

The report describes K(R) as missing in 3b. It is missing from the allocated notes, **not from the information available to the policy**: the full visible history and public rules already support the relevant inference. The API policy solved the checked contexts without that note. Thus K(F→R) and K(R) being useful computational complements is a legitimate hypothesis, not a demonstrated necessity or a measured allocation benefit.

The experiment did not test the pair against its individual units. It cannot establish complementarity or explain the failure causally by that untested omission.

### 2. Resolve the post-ask implication effect with more seeds?

**No, not now.** Precision on this particular display effect is not the project's central bottleneck. Even a precisely estimated display effect would not establish return improvement, unit selection value or efficiency at matched compute. Preserve the uncertainty and close this intervention branch.

### 3. Fund a larger backbone comparison?

**Not yet.** Preserve the remaining approximately USD 1.07596 under the original USD 5 cap. No new paid calls are authorized by this review. A future backbone comparison must answer a specified allocation or compute-efficiency question, rather than merely reproduce the fact that a different policy handles these examples.

The stronger no-note policy must remain a credible baseline. If it succeeds at the target compute budget, a method may still be useful by reducing cost at comparable quality; that possibility has not been measured here. Do not claim it as an existing result.

## Required method review before another run

Prepare one short specification and experiment proposal, using existing evidence and CPU-only symbolic checks where necessary. No further LLM data collection, prompt tuning, training, new seed sweep or task modification during this review.

### A. Define the bounded actor and the value being allocated

State the policy configuration, history h, retained memory m, budget, unit output, and all charged computation. A unit's value must be its effect on that actual actor's decisions and continuation, relative to its cost. Keep action-choice and retained-memory effects distinct where relevant.

A deterministic computation of h supplies no new external evidence to an ideal Bayes actor already reasoning from h. The relevant claim is improvement for a bounded actor, or equal quality at lower compute. The approximately 0.50 gap to Bayes from the repair block is not automatically recoverable through mental notes.

Retain better return at matched compute as the primary operational target, consistent with the original study. Define the compute budget and accounting before proposing experiments. Preserve the original reward and legitimate ask/search alternatives. Report lower compute at matched return as a secondary efficiency target rather than switching targets after results.

### B. Audit whether the note representation preserves decision-relevant relationships

Separate uncertainty in the robot's estimate from uncertainty, false belief or lack of belief in a person. Do not equate destination confidence with handoff success.

An illustrative structural check: both a courier's believed location and the recipient's location can have marginal distribution {A: 0.5, B: 0.5}. If they are always equal, the handoff succeeds; if always opposite, it fails. The marginals alone are identical in those cases. This does not show that the current full-history policy lacks information, but it shows why standalone belief distributions need not expose the relationship a bounded policy must use.

Using the declared public model, document the relevant relationships for the existing constructions: the courier's own belief, its view of the recipient, the recipient's belief/location, and what each action depends on. Identify what the current typed notes expose and what still must be computed from history. Do not immediately add an oracle success/correctness field as a solution.

### C. Specify a genuine complementarity test without running it

If the proposed next method uses multiple units together, define comparisons for no notes, each individual unit, and the pair, with the same actor, visible information and continuation. Include irrelevant and redundant-unit controls. Define the interaction, for example:

I(u,v) = J({u,v}) - J({u}) - J({v}) + J(empty).

Explain how extra compute is accounted for. A positive interaction alone is not sufficient: the pair must also offer useful value relative to its total cost and the relevant alternatives. Include a matched generic-reasoning or history-summary computation before attributing a gain specifically to perspective allocation.

Keep this a proposal. Do not manufacture training labels from a symbolic actor that is forced to ignore evidence the LLM baseline receives. Do not prune a pair solely because its isolated units have zero value unless the required assumptions are established; preserve the earlier cautions about complementary computations and retained memory.

### D. Give an explicit feasibility and stopping decision

The proposal must explain why the chosen actor/budget is scientifically meaningful and which observation would justify an allocation study. It must also specify an outcome that stops the approach. Avoid a design in which every negative result triggers another renderer, backbone, or generator revision.

If the proposed representation and actor leave no plausible, measurable value at a justified budget, recommend revising or stopping this implementation rather than continuing to optimize it. That is a finding about this approach, not a general rejection of theory of mind.

## What comes back

Return one method-review document containing the actor/value definition, relationship audit, a proposed minimal comparison matrix, resource forecast, and explicit proceed/stop criteria. State which parts retain the original method and which would constitute a versioned change. Do not launch the proposal automatically.

The central objective remains choosing which mental computations are worth performing. Coaching one weak policy through selected examples or demonstrating that another model solves them does not satisfy it.

## Evidence and provenance

Reviewed the consolidated report, numerical results, plan, gate reviews, qualification summaries, API records, source/analysis files and decision CSV. Independently reproduced the key wrong-handoff counts and paired factor point estimates. All seventeen report/evidence file hashes match the exported bytes. Full oracle reconstruction and repository tests were not rerun in this review.

LLM review gates are useful consistency checks, not independent external scientific validation. Retain the existing development-only status of all inspected seeds and configurations. No confirmatory, allocation, depth or transfer claim follows from this block.
