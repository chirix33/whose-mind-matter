# Comparing the two redesigns and choosing a research direction

Date: 2026-10-29. Sources: CONCEPT.md, review-request(7).md, CONCEPT 2: Action-Gated Relational Checks, the original methods outline, and the primary literature identified below. This is a research recommendation, not authorization for experiments, new API expenditure or a full environment build.

## 1. Recommendation

For the stated objective of preserving the original novelty and pursuing a potentially standout paper, choose a **lean hybrid led by Concept 1's scientific question, not Concept 2's gate**.

- Keep Concept 1's event provenance, relational perspective representation and selection of computations by decision value.
- Keep Concept 2's action-conditioned focus, explicit decision interface, generic verification/escalation controls and early falsification discipline.
- Do not initially build the full multi-task office day, train a router, or implement the entire Concept 2 condition matrix.
- Do not make a hand-written action-to-query lookup plus veto the central novelty. It is an important baseline and a possible interface, but substantially narrows the original contribution.

The central question should be:

> When several perspective relations could be computed or refreshed, can an agent choose the smallest useful set, preserve their dependencies, and improve decisions at a fixed computation budget compared with uncertainty reduction, structural relevance, fixed checking and generic extra reasoning?

Neither proposal, as written, establishes a spotlight-level contribution. The hybrid is the stronger research bet for that objective, with greater scientific risk than Concept 2's narrower empirical study. Spotlight selection cannot be predicted from a proposal, and numerical novelty ratings or council pass probabilities are not evidence.

If a January submission with limited engineering time is the overriding objective, Concept 2 is the more executable standalone option. It should then be pitched as a scoped action-verification paper with a reduced claim, rather than as fulfillment of the original allocation agenda.

## 2. Direct comparison

These are qualitative research judgments, not measured scores or acceptance probabilities.

| Criterion | Concept 1: relational perspective memory | Concept 2: action-gated checks |
| --- | --- | --- |
| Original allocation question | Stronger preservation: people, variables, paths, refresh, STOP and reuse | Substantial narrowing: action schema largely supplies the people/path; every triggering commitment is checked |
| Main scientific opportunity | Decision-sensitive relational abstraction and resource allocation | Selective verification through a constrained action interface |
| Response to lost correlations | Provenance and referents can preserve shared causes, if represented jointly | Explicit joint success computation avoids multiplying marginals |
| Response to poor policy integration | Still relies heavily on policy use of rendered relations | Directly addresses integration by constraining action execution |
| Cost mechanism | Reuse and incremental refinement may amortize cost | Sparse checks may avoid most extra calls; benefit depends on trigger frequency and checker cost |
| Largest novelty threat | Existing belief trackers, encode-once records and selective world modeling | Existing graph-gated decisions, event-triggered replanning and generic verification |
| Engineering risk | High: representation, inference, memory, generator, reference and controller change together | Lower initial scope, but inference, threshold calibration and gate semantics remain substantial |
| Main confound | Memory/compression could explain gains instead of mental-computation allocation | Generic caution or verification could explain gains instead of perspective selection |
| What is currently unproven | Relation usability, genuinely expensive refinements, useful sparse selection and deployment cost | Trigger coverage, competent-actor headroom, check fidelity and ToM-specific gains |

Concept 1 is better aligned with the intended research identity. Concept 2 is better at specifying a falsifiable near-term intervention. A full merger of both roadmaps would be too large and scientifically difficult to interpret.

## 3. Literature changes the novelty assessment

The following distinctions are supported by primary sources. This is a targeted overlap review, not an exhaustive novelty certification.

**Graph-gated decisions already exist.** Sun et al. explicitly compare prompt serialization, forced graph-generated action shortlists and an overridable graph-informed interface. Consequently, moving a belief representation from the prompt into action selection cannot be our headline novelty. The contribution would have to be the allocation of particular relation computations and its demonstrated resource tradeoff. [Full text](https://arxiv.org/html/2604.23057v1), especially sections 3.2 and 4.2–4.3.

**Adaptive mental-model construction already exists.** AutoToM adjusts mental variables and temporal context using an uncertainty/complexity utility. Its distinction from our proposed controller is the objective and selected operation, not simply adaptivity. Concept 2 incorrectly calls it QA-only: the paper also evaluates embodied online assistance. [Full text](https://arxiv.org/html/2502.15676v3), sections 3.4 and 4.3.

**Encode-once perspective records already exist.** HopToM/HopTrace reports event encoding into perspective records and deterministic nested-query resolution. Thus event pointers and avoiding repeated full-history calls are not enough by themselves. A HopTrace-style dense encoding with cheap targeted lookup is a serious competitor, not an optional weak baseline. The paper also cautions against equating nesting syntax with effective reasoning order. [Primary indexed abstract](https://arxiv.org/abs/2610.17777). The abstract was verified; full text was not retrievable in this review.

**Dense mental-world modeling already connects beliefs to actions.** MWM/Mentis simulates candidate physical and mental branches and evaluates their consequences. Our distinction must concern selective runtime computation under cost, rather than merely representing minds during planning. [Full text](https://arxiv.org/html/2607.27201v1).

**Belief recovery versus use is already a documented gap.** Yin et al. separately evaluate state understanding, belief inference, decisions and execution. Our negative development results are useful motivation and diagnostics, but their general message is not a fresh headline contribution. [Primary abstract](https://arxiv.org/abs/2610.34759).

**Event-triggered integration is also occupied.** BayesBeliefAgent combines Bayesian partner tracking with contradiction-triggered replanning. Its relevance is to the claim that triggering expensive reasoning at the right event is itself new. [Primary indexed abstract](https://arxiv.org/abs/2608.18490); abstract-level verification only.

**Decision-guided selection is broader than ToM.** I additionally found DGS-WM, Model What Matters, which selects observation targets for policy/world-model co-training. It is not the proposed runtime selector over directed mental relations, but we cannot claim that selecting world-model content by decision relevance is new in general. [Primary indexed abstract](https://arxiv.org/abs/2610.19642); full text was unavailable, so no stronger algorithmic equivalence is asserted.

The plausible remaining space is therefore quite specific: **runtime, decision-value selection and reuse of joint perspective computations, with counterfactual evidence that choosing the person/path and the objective matters beyond a fixed action checker.** This is a proposed distinction that still needs implementation and evidence.

## 4. What Concept 1 gets right, and what must change

### Preserve the causal representation, not just a new note format

The strongest part is the distinction between a belief's value and where that belief came from. Two people can each be 50/50 over rooms A and B while always agreeing or always disagreeing. Preserving the shared event or source can distinguish those cases without revealing a hidden room.

However, a distribution over referents for each unit can still lose correlation. Two marginal distributions over event IDs do not generally determine their joint. The representation must retain shared latent variables or explicit coupling constraints. Union-find is sufficient for deterministic equalities/disequalities; it is not a general probabilistic inference engine for uncertain observation, source reliability or correlated hypotheses.

The proposed relation layer must therefore specify deterministic and probabilistic cases separately. It must expose unsupported/inconsistent constraints rather than silently turn them into a confident equality.

### Do not construct an unnecessarily weak dense baseline

Maintaining every possible unit and dumping all of them into every prompt makes dense processing easy to beat for the wrong reason. Include dense encoding with query-specific retrieval/rendering. The candidate count should reflect the task's real facts, access relations and possible paths, not a combinatorial count of nonsensical units.

For scripted public transitions, exact event parsing and symbolic tracking may be cheap. Compare against that. If exact compilation plus targeted lookup solves the task more cheaply, there may be no reason for an expensive mental-inference selector in that regime.

### The label reference is not yet actor-aligned

A bounded-context Bayes actor can define information value for a restricted decision context. That does not establish the behavioral effect of a note on the actual LLM. Keep symbolic sufficiency/cost references separate from realized-policy labels. Also account for information disclosed by which unit is selected, selection order and omitted units: a supposedly Bayes-optimal reference cannot ignore its own observation/message mechanism.

The existing I-projection approximation should not be renamed a fully coherent Bayes receiver without specifying the likelihood of the transmitted summaries.

### Defer the full office day

The day-level regime could create genuine reuse, but building it first simultaneously changes task distribution, horizon, memory, representation and inference. It risks spending a week qualifying a setting before checking whether the proposed representation is usable.

Use a minimal relation test and a short substantive reuse sequence first. A longer sequence should be justified by actual dependencies and measured cost, not by increasing context until a favored method wins. Generic memory must be allowed to preserve who perceived what; a narrator summary deliberately deprived of that information would be a weak control.

## 5. What Concept 2 gets right, and what must change

### Keep its intervention discipline

It correctly addresses the observed failure of correct advisory notes. Matching a targeted check against a generic check under the same gate is essential. Escalation, a competent direct policy, simple ask/search rules, fixed-query checks and positive-control handoffs are strong comparisons.

But an action-to-query lookup is primarily structural relevance, not demonstrated decision-value allocation. Checking every qualifying action with a two-check cap does not establish that the controller knows when a relevant computation is worth buying. It also misses cases where the actor never proposes the good action: a verifier of bad commitments cannot recover every missed opportunity.

### Fix the decision rule and checker semantics

For a one-step terminal commitment, the immediate expected return is

J_commit = -0.05 + p - (1-p) * 0.5 * stakes.

Compare this with a feasible alternative's value from the same history and remaining horizon. A single V_safe = 0.90 is not valid across states with different access, search distance, information or remaining time. The proposal's thresholds are illustrative, omit the step-cost difference, and must not become an unqualified gate rule.

An ask can be uninformative, reveal only the speaker's own belief rather than its nested belief, or repeat an obstructive report. An ask-first baseline is necessary, but should not be described as uniformly safe or informative.

A sixteen-world cap is not an exact posterior guarantee. Generated hypotheses can omit consequential worlds, misweight them or conflate the robot's information with someone else's. Track coverage/residual uncertainty and qualify inference separately from the gate's effect.

Specify the complete state machine after a veto: number of re-decisions, treatment of a second blocked proposal, what happens at the cap, and whether a cached verdict still applies. As written, one re-decision, repeated checks and execution after the cap are not a complete consistent protocol. A capped risk gate is not a safety guarantee.

An exact-content gate with fixed thresholds is not a universal upper bound on every deployable policy: exact probabilities can be integrated poorly or over-cautiously. Call it an oracle-content interface diagnostic, not proof that no implementation can work if it fails.

### Repair the proposed controls

Random-relation and direction-swap controls must preserve the meaning of the information they compute. Do not insert an unrelated probability as the proposed action's success probability. Use a labelled wrong-target computation with the same downstream interface, or a clearly declared synthetic corruption diagnostic. These answer different questions.

Use actual episode outcomes, not just wrong-commit reductions. A gate can improve that rate by blocking everything and then timing out. Include correct commitments and completion cost.

### Rebuild cost forecasts from measurements

Active parameters times tokens is a rough proxy, not measured cross-model compute. MoE routing, memory traffic, quantization, attention, serving hardware, prefill/decode mix and caching all matter. A cheapest-provider price ratio cannot establish a 1.4–1.7x physical compute margin. The 120b model's task competence must be measured rather than assumed from size.

The measured old baseline used about 3.1 decisions per episode; Concept 2's four-to-six-decision assumption is a new forecast. Generic-check cost, veto frequency and retry rates remain unknown. Do not use them as established break-even facts. No current provider price or total-spend forecast is endorsed by this review.

The example action-audit block is not fully internally consistent: an OPPOSITE coupling with exhaustive A/B marginals implies zero agreement, not 0.05, unless residual hypotheses are explicitly included. Its stated block length also needs actual tokenization.

## 6. The lean hybrid I recommend

Working framing: **Whose Mind Matters? Decision-Value Refinement of Relational Perspectives.** The title is provisional, and the proposed mechanism is not an established new result.

### Core architecture

1. **Maintain a cheap provenance index.** Record observed events, source IDs, timestamps and known access relations. Retain the raw log for every method. The index must not contain simulator-private beliefs or evaluator-supplied source pointers.
2. **Produce a small action set.** Include the current proposal and meaningful alternatives, such as asking, searching and handing off. Charge proposal and scoring calls. Do not depend only on the actor volunteering an irreversible mistake.
3. **Identify unresolved joint perspective queries.** For example, whether F's forwarding view is aligned with R's relevant state, or whether testimony from S changes that relation. Include cheap reuse and refresh options.
4. **Select a computation or STOP.** The controller chooses among available queries/refinements, cached results and stopping, considering expected decision improvement and cost. A structural action-trigger rule remains a baseline. A learned router is optional later, after actual selection value exists.
5. **Refine only the evidence needed.** Use the index and the agent's legal source spans; preserve shared causes in the hypothesis representation. If every query is already settled by cheap compilation, return that result without an LLM call.
6. **Use a common decision interface.** A gate, constrained shortlist or explicit decision executor can use the relation result. Keep this interface identical across the competing allocation objectives. Ablate advisory versus constrained integration separately.
7. **Cache with dependencies.** Reuse supported relations until relevant evidence changes. Distinguish fresh evidence that changes the person's state from evidence that changes the robot's estimate. All indexing, retrieval, inference, invalidation and rendering costs count.

The cache is a supporting component, not a second headline memory contribution. The gate is a supporting component, not a claim of novel graph integration. The scientific object is the choice of relational computation.

### The value being selected

For a stated bounded actor and continuation, use the expected downstream return change from a computation q, minus its total cost. If results persist, include their future value in that return; do not subtract an unrelated probe effect to label a memory contribution.

A useful conceptual expression is:

V(q | h,m) = E_y[J_pi(h, update(m,q,y))] - J_pi(h,m) - lambda * C(q | h,m).

This expression is a metareasoning objective, not itself a novel theorem. Estimating it cheaply is part of the research problem. Do not obtain it at deployment by querying evaluator action values or by running all expensive checks first. Evaluation-only paired rollouts may supply development targets, with their actual labeling cost reported.

### What would distinguish it experimentally

The same action can require no new computation, a cheap cached lookup, one source-reliability update or a joint path refinement depending on the visible state. The same uncertain relation can deserve computation at high stakes and STOP at low stakes. An irrelevant uncertain person's state should remain uncomputed. These are the cases that distinguish a decision-value policy from a fixed action checker, entropy reduction and structural relevance.

If all cases select the same two people whenever give(F) is proposed, there is no compelling allocation contribution. Use Concept 2's fixed relevant bundle as a strong baseline and accept that possible outcome.

## 7. Evidence needed for a potentially standout paper

### One coherent scientific claim

Proposed claim, not a current finding:

> Preserving dependencies between perspectives enables an agent to select which mental computations to perform or refresh by their decision value, improving task return at fixed resources beyond dense encode-once tracking, generic verification and structural action-trigger rules.

Four evidence requirements follow.

**Representation necessity.** Construct certified cases with identical physical state and identical mental marginals but different joint relations and best decisions. Include direction controls and cases where the relation is irrelevant. The elementary correlation counterexample is a useful diagnostic, not enough by itself to constitute the paper's theoretical novelty.

**Objective necessity.** Compare value-based selection with entropy, structural relevance, action-triggered checking, fixed relevant bundles and matched-random allocation using the same engine and decision interface. Vary stakes and computation costs independently. Stakes can also change a baseline policy's actions and flip probabilities, so do not revive the original invalid invariance claims.

**Resource advantage.** Include direct/more-reasoning, generic verification, escalation, dense exact/encode-once lookup and generic memory. Record CPU cost, tokens, latency and available GPU measurements separately. Do not require every metric to improve simultaneously or collapse provider dollars into physical compute. Declare the resource objective and operating points before outcomes.

**Generality.** A January paper with only inspected OfficeMinds templates would have a limited empirical claim. A stronger contribution needs at least one independent task or interaction mechanism and more than one competent policy configuration, evaluated under a frozen protocol. A natural-language coordination/role-play task with private information boundaries would help restore the original transfer ambition. Adding twenty irrelevant events alone is not an independent task family.

The old negative results support the motivation; they are not the headline discovery. A new acronym, a larger baseline table or a guarantee copied from classical metareasoning would not substitute for these distinctions.

## 8. A smaller next step than either complete roadmap

Do not begin Concept 1's week-long G0 build or Concept 2's full episode matrix immediately. First produce a small qualification package with four designed decision situations:

1. A certain but wrong forwarding destination.
2. An uncertain destination perfectly aligned with the recipient.
3. An unresolved relation that cannot affect the best current decision, supporting STOP.
4. A relation worth refreshing after a substantive new event, with earlier evidence reused legitimately.

For each, specify legal observations, joint hypotheses, action consequences, cheap compiled outputs, candidate refinements, costs and why the chosen refinement might beat its alternatives. Qualify both deterministic and uncertain-provenance cases. If an exact public-rule compiler already answers everything cheaply, identify that honestly before inventing an expensive checker.

This package should also identify the nearest implementation-level baselines from the literature and the minimum new component separating us from them. That is a feasibility review, not a new batch of LLM experiments or an authorization to revise the environment until it yields a win.

Only if the mechanism survives that review should a small, predeclared actor-usability and cost test reopen. It should test the new joint representation and selection opportunity, not rerun a failed advisory-note variant. A short genuine reuse sequence can follow; a long office day is justified only if measured reuse is necessary to the claim.

A failed substantive gate can stop this implementation under the schedule. It does not logically refute every future ToM-allocation architecture. Likewise, a positive perfect-content diagnostic does not authorize controller training automatically.

## 9. Timeline, venue and confidence

The official calls currently list January 4, 2027 for ACL's latest ARR cycle and January 4/11 for IJCAI abstract/full submission. That leaves roughly nine to ten weeks from this review. Both proposals contain substantial unvalidated engineering and empirical assumptions; promising a spotlight outcome on that schedule would be unrealistic.

My priority order for the stated goal is:

1. Lean hybrid: highest fidelity to the intended scientific contribution, conditional on a real and cheap selection opportunity.
2. Concept 1 after substantial scope reduction and a stronger dense/encode-once comparison.
3. Concept 2 as a narrower executable verification paper, with honest reduction of the allocation claim.

These are research judgments, not acceptance probabilities. A very strong Concept 2 result could still be valuable, but successful execution would not automatically restore the claims it explicitly drops. If the hybrid has no clean novelty distinction or resource mechanism, stopping is preferable to relabelling generic verification as selective theory of mind.

## 10. Verification scope

Read both proposals, review-request(7), and the original methods outline. Cross-checked the most consequential literature overlaps using primary abstracts or full text as identified above. Did not independently verify every entry in the council bibliography or its numerical cost/acceptance forecasts. Failed full-text retrieval is not evidence that a paper does not exist.

The key correction to Concept 2's literature table is that AutoToM is not QA-only. The additional DGS-WM overlap deserves inclusion in either redesign's related-work discussion. Its training-time focus differs from the proposed runtime perspective selector; further full-text inspection is required before claiming a sharp algorithmic separation.

No experiments, model calls, paid API calls or repository mutations were performed for this comparative review.
