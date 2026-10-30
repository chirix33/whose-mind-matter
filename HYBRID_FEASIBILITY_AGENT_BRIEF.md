# Start here: hybrid feasibility pilot, with Concept 2 fallback

Date: 2026-10-29. User decision: pursue the lean hybrid first; Concept 2 is the fallback if the hybrid is infeasible after testing. This document authorizes the bounded implementation and local experiments below. It supersedes earlier no-new-experiment instructions only for this block. Preserve all previous frozen data and negative findings.

## 1. Research objective and authority

Build and test whether an agent can choose which **joint perspective computation** to perform, refresh, reuse or skip by its expected decision value and cost.

Retain the original aim: return at matched compute, selecting people, mental variables and directed perspective paths. A hard-coded action-to-query mapping is a baseline, not sufficient evidence for that contribution.

The hybrid uses Concept 1's relational/provenance representation and allocation question, with Concept 2's explicit decision interface and generic-check controls. It does not merge their full roadmaps.

Read these for background, in order:

1. This file: current execution authority.
2. CONCEPT_COMPARISON_AND_HYBRID_RECOMMENDATION.md: rationale and required corrections.
3. CONCEPT.md: referents, relations and reuse; its full office-day build is deferred.
4. CONCEPT 2: Action-Gated Relational Checks: interface and fallback; its original cost forecasts, thresholds and full experiment matrix are not authorized as written.
5. Existing repository specifications, decision records and the frozen experiment summaries as needed.

Do not ask for another approval merely to carry out the work authorized here. Make routine engineering choices, record them before affected outputs, finish the block, and return a consolidated evidence bundle. A genuine missing requirement, unsound information boundary or exhausted resource limit is a reason to stop and report, not silently expand scope.

## 2. Resource and scope limits

- Use the existing local gpt-oss-20b setup. Available already-provisioned cloud resources may be used within existing limits; no new rentals or paid model calls in this block.
- API ledger should remain approximately USD 3.924 of the original USD 5 cap. Do not infer a new USD 10–50 authorization from Concept 2's proposed budget.
- Maximum two working days of implementation effort and two hours of active local model-serving time for this feasibility block. Record actual effort/runtime separately. If the implementation cannot fit, finish the reviewable checkpoint and report the blocker.
- Maximum 2,304 completed episode rollouts across the hybrid and fallback combined, plus at most 96 single-decision integration smoke probes. These are ceilings, not targets to consume.
- Run complete predeclared paired blocks; do not select successful cases or replace difficult seeds. Report partial blocks separately if interrupted.
- No learned router, full office-day generator, broad backbone search, training labels for a future controller, or confirmatory/transfer evaluation.
- One frozen implementation/prompt configuration per branch. Repair demonstrable code/schema defects if necessary, version and log them, and identify affected results. A behavioral disappointment is not a code defect and does not authorize prompt tuning.

All new results are development/feasibility evidence. This pilot is not powered to establish a spotlight-level claim or rule out all useful effects.

## 3. Common foundation: implement and qualify on CPU first

Create a versioned prototype rather than modifying dev-v3 or its frozen reports. Reuse existing tested components where possible.

### Representation and information boundary

Maintain observed event IDs, source provenance, timestamps, access relations and shared latent factors needed for joint perspective reasoning. Preserve the raw history for every baseline. Do not give the deployed method simulator-private minds, hidden realized values, evaluator Q-values or gold source pointers.

The representation must distinguish:

- the robot's uncertainty about a person's categorical belief;
- the person lacking a belief or holding an outdated belief;
- the computation not yet being performed;
- new evidence updating the person's state versus only updating the robot's estimate.

Referent marginals alone are insufficient. Test both deterministic equalities/disequalities and uncertain shared provenance. Use a finite exact joint model for qualification when tractable; do not normalize a truncated list of generated worlds and call it exact. An approximation must expose unresolved mass/coverage and its limitations.

### Four small qualification families

Construct controlled, minimally changed cases using existing validated semantics. Avoid a full environment redesign:

1. **Certain but wrong route:** a courier's destination is known, but it differs from the recipient's relevant location/belief.
2. **Uncertain but aligned route:** individual destination/location marginals are uncertain, but a shared event makes them coincide.
3. **STOP:** a mental relation remains uncertain but cannot improve the current decision enough to justify an additional computation; include physical-observation controls.
4. **Reuse/refresh:** within one short genuine sequence, supported content can be reused, followed by an observed event that changes a relevant dependency. No unobserved reset of minds between decisions.

Use same-physical-state contrasts and matched marginal distributions where relevant. Include correct-handoff controls and at least two meaningful candidate relations, so the selector is not just handed the single query to compute. Do not introduce arbitrary delays, padded text, artificial CPU costs or expensive no-op queries to force an allocation benefit.

Implement the smallest short sequence that supports family 4. If this requires an office-day rebuild, stop that extension and report it as a hybrid feasibility obstacle.

### Strong cheap competitor

Implement/measure the cheapest credible exact public-rule tracker or encode-once perspective index available for these observations, with query-specific lookup/rendering. Include its actual parsing, updates and query costs. Do not make dense processing dump all units into every decision prompt.

If this solves every query cheaply and no actual expensive refinement remains, record that as a hybrid-specific failure. It may still provide a legitimate deployed checker for Concept 2; it is not an excuse to add unnecessary LLM calls.

### Common decision interface

Specify and test a complete state machine for proposing, checking, executing, vetoing and re-deciding. Use the same interface across allocation comparisons.

For a terminal one-step commitment:

J_commit = -0.05 + p_success - (1-p_success) * 0.5 * stakes.

Compare with a feasible alternative from the same history and remaining horizon. Do not use V_safe = 0.90 universally. Asking can be uninformative or repeat an obstructive report. Keep ask/search costs and horizon constraints intact.

Use public evidence and the method's own inferred/compiled relations. Evaluator probabilities are allowed only in separately labelled diagnostics. A public-rule computation is not privileged simply because it is action-relevant, but it must be an explicit, costed method component.

Freeze the veto/re-decision limit, treatment of repeated blocked actions, cache keys, invalidation and behavior at budget exhaustion. Never describe a capped approximate gate as a safety guarantee. A scripted fallback must be declared and counted, not chosen from the evaluator's optimal action.

### CPU gate

Before model calls, write a short record showing:

- qualification and replay checks pass with zero information-boundary violations;
- joint relations reproduce the intended contrasts without multiplying marginals;
- observed evidence, queried mental variables and action consequences are separate;
- which computations remain genuinely costly after cheap compilation;
- whether different states justify different queries, reuse/refresh and STOP;
- the actual tokenizer forecast, local runtime forecast and complete branch protocol.

If common semantics, joint inference or information boundaries are unsound and cannot be repaired within the effort limit, stop both branches. If only the hybrid's selection economics fails, move to the fallback in section 6.

## 4. Freeze the hybrid pilot before outcomes

If the CPU gate supports a nontrivial allocation opportunity, freeze the local prototype, prompts, model/decoding, retries, fallback, seeds, costs and analysis before collecting new behavioral outputs.

Suggested maximum design: four families x eight independent base scenarios x two stakes levels x two policy draws x six conditions = **768 episodes**. Each family must vary meaningful public/hidden draws, not only rename one fixed world. Hash or otherwise preselect fresh unused seeds. All paired conditions share the underlying scenario and exogenous draws. Repeats and stakes variants are nested within base scenarios.

Conditions:

- **H0 direct:** full history, existing policy, no separate mental computation.
- **H1 hybrid:** frozen decision-value proxy chooses computation, refresh, reuse or STOP; joint relation engine and common decision interface.
- **H2 structural/fixed check:** checks the fixed action-relevant bundle at eligible decisions with the same engine/interface. Give it the same legitimate cache support.
- **H3 uncertainty selector:** prioritizes uncertainty under the same candidate set, resource limits, engine and interface.
- **H4 generic verification:** a competent generic re-check at the same class of decision opportunities, with comparable resource allowance and the same execution constraints. It may inspect the complete history and preserve access relations.
- **H5 cheap dense/encode-once:** the qualified tracker plus targeted lookup/rendering. Charge its actual costs, not imaginary per-unit LLM calls.

The H1 selector may initially be a transparent frozen rule/score estimating decision value. Specify exactly how it uses inexpensive visible features, stakes, current memory and costs. Do not use evaluator returns/Q-values, hidden worlds or results of all expensive queries at deployment. If it is only structural relevance, label it that way and do not claim value-based allocation has been implemented.

Any exact-content smoke check is a separate diagnostic; only the deployed inferred/compiled engine can support an H1 feasibility pass. Use the shared allowance of at most 96 one-decision smoke probes to catch interface/code failures, not to choose a favorable prompt. Keep and report every output. Freeze subsequent pilot settings without behavioral tuning on those outputs.

An additional advisory-versus-gated ablation is deferred. It must not confound the H1/H2/H3 selection comparison.

## 5. Hybrid decision rule

Primary metric: paired episode task return across independent base scenarios. Secondary: irreversible errors, timeout, correct commitments, task steps, query choice, STOP/reuse/refresh, all processed tokens, calls, retries and measured latency. Report CPU and serving time separately. Measure caching effects rather than equating tokens with GPU time.

Use grouped uncertainty intervals, stratified by family. State that the small pilot is a screen, not confirmatory evidence. Never delete catastrophic failures or select a favorable subgroup as the primary population after outcomes.

Declare budget settings and matching tolerance before calls. Report mean resources and their variation. Claims at matched compute require measured comparable operating points; reference-content costs imputed from an older run are not deployment measurements.

Recommend **continue the hybrid** only if all three hold:

1. H1 is a valid deployed computation pipeline and shows at least +0.05 mean return versus direct in the predeclared pooled pilot. Report its CI and limitations; a positive point estimate alone is not a paper claim.
2. Against both structural/fixed checking and generic verification, H1 meets a predeclared screening criterion: either at least +0.03 mean return with no more than 10% higher measured processed-token cost, or at least 20% lower processed-token cost with no lower mean return and a paired return CI lower bound above -0.05. Also report latency and CPU costs; do not conceal a material time regression. H1 must not be clearly dominated by the cheap tracker. Label the second route an efficiency feasibility signal, not proof of the original return-at-matched-compute claim. Report uncertainty; these are screening decisions, not established frontier results.
3. The choices are nontrivial: the agent selects different relevant relations and uses STOP or reuse/refresh appropriately. It does not merely compute the same bundle every time. Qualification controls must rule out a win created only by an unfairly verbose dense baseline, withheld baseline information or an uncharged computation.

If uncertainty prevents this recommendation, mark the hybrid **not established within this feasibility block**, not universally impossible. Do not add seeds or revise the method automatically. Proceed to the agreed fallback if its shared foundation is valid.

A hybrid pass ends this block with a proposal for a larger frozen study; it does not authorize router training, a full office-day build or a transfer campaign.

## 6. Concept 2 fallback: authorized if the hybrid does not pass

The user has accepted Concept 2 as the fallback. No extra approval round is needed to run this limited fallback after a hybrid-specific failure or inconclusive pilot.

Reuse the qualified joint engine and decision interface. The fallback's question is narrower: **does action-triggered relational verification improve episode outcomes enough to justify its cost beyond generic verification and simple legal alternatives?** It is not the original broad decision-value allocation claim.

First use existing no-note traces for a CPU-only audit of trigger coverage and lost return. Distinguish social belief-dependent commitments from general physical uncertainty. Replacing recorded errors with ideal continuation is an optimistic diagnostic, not a deployable effect or a universal ceiling for every gate.

If the trigger has no meaningful opportunity on these traces and qualified families, stop. Do not harden the environment or weaken the baseline to create one.

Otherwise freeze one fallback pilot, up to twelve existing constructions x eight fresh base scenarios x two stakes x two draws x four conditions = **1,536 episodes**, subject to the combined block/time cap:

- direct full-history policy;
- targeted relational checker plus gate;
- generic verification plus the same gate;
- a declared simple ask/search-before-commit policy using legal observations and public rules.

Use the deployed checker, not evaluator truth, for the proposed method. A separate exact-content diagnostic may use the remaining smoke allowance but cannot pass the fallback by itself. Avoid another inference-package revision.

Keep positive controls, incorrect/unsupported estimates, missed opportunities and over-caution visible. Judge full return and cost, not only a reduction in wrong commitments. The generic comparator must receive comparable computation opportunities and budgets. The simple policy must handle uninformative answers honestly.

Continue Concept 2 only if the targeted checker shows a practically useful pooled gain (screening threshold +0.05 versus direct), beats generic verification and the simple policy under the same quality-or-efficiency screening criterion in section 5(2), and has no benefit explained solely by suppressing valid commitments. Report CIs; if unresolved at this sample, return unresolved rather than extending the run.

This pilot cannot establish a competitive cross-backbone frontier. A competent larger-policy and escalation comparison remains necessary before a full Concept 2 paper claim, but no new API batch is authorized here. Return its concrete resource forecast with the results.

If the targeted and generic checks perform similarly, identify generic verification as the likely surviving contribution. Do not relabel it perspective allocation. If both hybrid and fallback fail, stop this line and consolidate the negative development findings.

## 7. Stop and return one reviewable bundle

Return after the hybrid pass, the completed fallback, a shared-foundation failure or the resource limit—whichever applies. Do not start another methodological round automatically.

Deliver:

- FINAL_REVIEW.md: what ran, main numbers, hybrid/fallback decision, remaining uncertainty and next recommendation;
- protocol and dated decisions, frozen seeds/prompts/configuration and implementation commit;
- CPU qualification, information-boundary checks, cheap-compiler measurements and exact/deployable distinctions;
- per-episode results and grouped paired analysis with return and complete compute accounting;
- note/query and cache/invalidation traces, representative successes/failures, all truncations and fallbacks;
- source diff or compact reproducible source bundle, hashes, tests and current spend ledger;
- a clear statement of the surviving novelty claim and which original claims remain unsupported.

Use normal engineering and scientific review checks already established in the repository. Preserve failed attempts and contradictory results. Do not report a spotlight probability or upgrade a feasibility screen into a demonstrated contribution.

Start by reading the repository instructions and this brief, inspecting the existing reusable code and evidence, then implementing the common CPU foundation. Do not return only a new proposal unless a concrete blocker prevents the authorized work.
