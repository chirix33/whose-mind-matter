# Repair-block research decisions

Date: 2026-10-29. Applies after D-015 and the completed repair-and-validation block. Preserve the original research question, prior inspected-data designations, and cumulative USD 5 spending cap. This is one bounded integration diagnostic, not authorization for allocation training or open-ended tuning.

## 1. Accept the negative result for the tested configuration

The repair block tested 288 independent base scenarios and 4,032 episodes, including depth controls. The primary conditions each contain 1,152 episodes:

| Primary condition | Mean task return | Successful episodes |
| --- | ---: | ---: |
| No notes | 0.3807 | 880/1,152 |
| Inferred notes | 0.3378 | 866/1,152 |
| Matched reference notes | 0.3567 | 871/1,152 |

Reference minus no notes is -0.0240, reported 95% CI [-0.0739, +0.0283]. Inferred minus no notes is -0.0429 [-0.0977, +0.0127]. I reproduced both estimates and obtained independent stratified bootstrap intervals approximately [-0.0755, +0.0277] and [-0.0989, +0.0128].

Accept the pre-declared pooled reading: neither condition reaches the practical improvement threshold of +0.05 under this configuration. This does not establish equivalence to zero, significant overall harm, or absence of any useful subgroup. It applies to the equal-weight mixture of the twelve constructions, fixed t0 notes, the declared retention/rendering protocol, and the local policy configuration.

Stop further inference-prompt revisions and allocation training. The favorable small earlier pilot is not a basis for overriding this larger result.

## 2. Decision 1: investigate integration first, without declaring the environment suitable

The evidence warrants an integration diagnostic before another environment redesign.

In 3b, reference notes increased immediate wrong handoffs from 10/96 to 28/96. In 2b, exact belief content was sometimes treated as the recipient's actual location. Those behaviors are direct evidence that correct note content is insufficient for this policy to act correctly. Written reasoning offers useful examples, but is not a reliable record of the model's internal causal process.

Two limits are essential:

- The approximately +0.50 gap to the Bayes actor is **general task-performance headroom**, not an estimate of the benefit available from mental-state notes. It includes search, risk calibration, action-rule application, and ordinary planning. Do not cite it as proof of explicit-note headroom.
- The after-ask stale label cannot explain the increased first-action handoffs: those actions precede the label. It can still contribute to subsequent mistakes. Do not make it the presumed cause of the overall null.

The environment has demonstrated task-level social contrasts under its declared scripted semantics. Whether explicit mental computations improve the actual policy's return/compute tradeoff remains unresolved. That is still the original research question.

## 3. Decision 2: approve a modified, bounded diagnostic

Approve the proposed content/implication by status-label comparison with the controls below. Do not repeat the full 4,032-episode study or change the environment, rewards, inference package, policy instructions, confidence wording, or decoding during this block.

### A. Existing-trace audit first

Use the existing complete traces locally; no new model calls are needed. Separate t0 from later decisions. Tabulate first actions, exposure to stale labels, asks and subsequent handoffs/drops, and whether statements concern a person's own belief or another person's belief.

Use action patterns as the main audit evidence. Any classification of written reasoning must have an explicit rubric, representative examples, and uncertain cases. Do not infer causal effects by comparing episodes that happened to ask with episodes that did not: asking is itself a policy choice affected by the notes.

Verify symbolically which example asks leave the relevant mental content and its public-model posterior unchanged. Distinguish an unchanged person's belief from an updated robot estimate of that belief.

### B. Freeze a small controlled probe

Use fresh seeds selected before any new model output. Include **3b and 2b plus positive controls 3a and 2a**. The controls matter: suppressing all handoffs or always searching could appear beneficial on the two negative cases without demonstrating correct use of perspectives.

Default local scope: eight fresh seeds per construction, two stakes levels, and three policy draws per prompt. Record the exact seed list before outputs. This is a mechanism diagnostic, not a powered pooled-return confirmation. Keep the seed/construction as the independent base unit; variants and draws remain nested.

Use exact public-model reference notes first. Do not generate another inference-package variant. Freeze each note payload once and reuse it across the rendering/status conditions, so changing the display does not change the note draw.

The factors are:

| Factor | Level 0 | Level 1 |
| --- | --- | --- |
| Content presentation | Existing typed content | Same typed content plus its action-consequence mapping |
| After-ask status display | Existing status warning | Omit only the after-ask stale warning |

For status-warning omission, retain the t0 timestamp and identical content. Do not relabel the note fresh, claim it is current, refresh its posterior, or suppress unrelated refutation/invalidation signals. This is a presentation ablation, not a global change to graph semantics.

### C. Test at matched decision contexts

Use both t0 and a standardized post-ask context. At the latter, execute the same predeclared legal ask from the same cloned starting world before presenting the prompts. Preserve the complete observation history, action costs and remaining horizon. Do not select post-ask contexts from successful or failed policy trajectories.

At t0 the stale-display factor has no effect. Verify byte identity and evaluate the three distinct conditions: no notes, typed content, and typed content plus implication. Do not count duplicate t0 prompts as distinct status treatments.

After the standardized ask, evaluate no notes plus the four factorial note conditions. No notes is necessary: comparing only the four note conditions cannot establish that any of them helps.

The default design is therefore 4 constructions x 8 seeds x 2 stakes x (3 t0 + 5 post-ask conditions) x 3 draws = **1,536 one-decision calls**. Counterbalance dispatch and retain all failures under a frozen retry/fallback rule. Record model, effort, temperature, token limits, concurrency and actual usage. Keep the existing local policy configuration to isolate the proposed factors.

This probe does not estimate full-episode return. Do not report it as if it did. Do not automatically add a rollout stage after seeing its results.

### D. Restrict the implication to a legitimate computation

An allowed line is: "Given this estimate and the stated forwarding rule, give(F) sends the package to office_a with probability 1.00."

Generate it only from the allocated typed content and the shared public transition rules. Preserve probability distributions when the destination is uncertain. Qualify the transformation symbolically across the included cases before freezing it.

Do not supply the hidden destination, a true/false belief label unavailable to the agent, an exact optimal action, Q-values, or advice such as "do not give" derived from evaluator access. Do not insert information from an additional unallocated mental unit. Physical action rules stay available to every condition as before.

The mapping is an added reasoning component. Record its specification and cost. If it helps, the result concerns mental content **plus public rule application**; it does not rescue the old content-only method retroactively.

### E. Measures and interpretation

Primary diagnostic measures: erroneous handoffs/drops and the public-model action-value gap V*(h) - Q*(h,a), calculated by the evaluator for the selected action. The latter uses Bayes-optimal continuation and is not an estimate of the LLM's eventual rollout return.

Report paired factor effects, interaction, comparisons with no notes, and separate results for every construction, stakes level, and t0/post-ask context. Show uncertainty across independent base scenarios. Keep error-tail observations. Use common frozen prompts within each contrast; do not tune a variant against these new results.

The positive controls must show that any reduction in wrong handoffs is compatible with retaining correct handoffs. No allocation or depth claim follows from this diagnostic alone.

## 4. Decision 3: a stronger policy is in scope as a separate small check

Approve a bounded policy-only check using the already configured API backbone, if it fits the remaining original budget. Do not change the main backbone or run a model search.

Before any new local or API outcomes, hash-select eight contexts from the probe: one t0 and one standardized post-ask context per construction. Run the exact no-note and existing content-only reference prompts on the API policy: **16 decision calls**, with the same legal actions and public information. Compare with the corresponding local contexts. These are diagnostic samples, not a backbone benchmark or proof of model superiority.

Freeze the API model identifier, effort and output cap before calls; document differences from the local configuration. For this small API check allow one attempt per decision, with no automatic retries. Use the existing validated client and spend ledger. A failed/truncated response remains a recorded failure rather than a reason to increase the configuration mid-run. If truncations prevent interpretation, report the check as inconclusive about policy capability.

Incremental API spending for this check must be **at most USD 0.50**, and cumulative spending must stay below USD 5. Reconcile the approximately USD 3.869 already spent before launch. Verify that the worst-case cost of all 16 calls at the frozen input/output limits fits both caps before launching, and enforce the caps through reservations. If the planned balanced slice cannot fit, skip it and report that limitation; do not substitute a cheaper model or select fewer cases after seeing outcomes.

A stronger no-note policy doing well would indicate a policy-configuration limitation, not establish note value. Only the within-policy note contrast addresses note integration. Even that remains exploratory at this size.

## 5. Stop after this diagnostic and return

Return one consolidated report and evidence bundle. No automatic training, further prompt/rendering revision, new environment version, or larger API run follows.

- If action-consequence mapping helps while preserving positive controls: propose a versioned integration component and a properly budgeted episode-level test. Include a budget-matched generic-computation baseline before claiming perspective-specific efficiency.
- If omitting the status warning helps only after asks: propose dependency-aware invalidation and test its validity. This does not explain the pre-ask failure.
- If the API configuration handles the rules but gains nothing from notes: report general policy capability separately from explicit-computation value.
- If neither factor helps: stop further content/display tuning and return to a method/environment review. Do not keep changing seeds or backbones until a positive result appears.
- If effects are uncertain: state the unresolved effect sizes and resources needed. Do not convert an underpowered diagnostic into a positive or negative general claim.

The original objective remains decision-value allocation over mental variables and perspective paths. A demonstration that a weak policy can be coached through selected false-belief cases would not, by itself, satisfy it.

## 6. Audit notes for the implementation report

I checked the 4,032-row CSV, primary outcome counts, construction summaries, example traces, source diff, freeze metadata, qualification summary, plan and review reports. The supplied prompt, pilot renderer and validator match the corresponding frozen source hashes. I did not rerun the reported 305-test suite or the full oracle qualification.

The 3b example episode's cumulative return is -2.10; -2.05 is its final action's reward. Correct that distinction in summaries without rerunning anything.

Of 23 report/evidence hashes, three match after LF-to-CRLF normalization; the others match directly. This is a packaging detail, not a numerical discrepancy. Preserve exact exported bytes in the next hash manifest.

When reporting deployment cost, distinguish actual unique-note generation during this frozen-note experiment from per-episode cost without such experimental reuse. Repeated policy draws do not automatically justify amortizing a deployable note call across independent episodes.
