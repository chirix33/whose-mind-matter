# Review of the hybrid feasibility and Concept 2 fallback

Date: 2026-10-30. Sources: FINAL_REVIEW(4).md, review-request(8).md, cpu-gate.md and the execution brief. This closes the authorized feasibility block. No new model experiments or spending are authorized here.

## 1. Research decisions

1. Accept the hybrid CPU stop for this implementation: shared enumeration makes all tested relations inexpensive, so an expensive allocation mechanism has no demonstrated resource advantage.
2. Preserve the fallback's frozen failure classification. Do not change its criterion after outcomes or declare that it passed.
3. Preserve the substantial positive fallback result as a separate finding: a public-model symbolic checker plus an action gate improves this local policy's return and outperforms its generic LLM checker.
4. Do not start a new natural-language environment, role-play campaign, backbone comparison, router or renderer revision. Export the existing evidence for an implementation/data audit before deciding on another research direction.
5. Keep the approximately USD 1.076 remaining under the original budget unspent.

This is neither a successful allocation result nor an absence of useful findings. The checker intervention and the allocation question have different outcomes.

## 2. What the reported experiment establishes

The fallback contains 96 fresh base scenarios, expanded across two stakes and two policy draws: 384 episodes per condition, 1,536 total. Variants and repeated draws are not independent scenarios.

Reported task returns are direct 0.303, symbolic checker gate 0.564, generic gate 0.433, and ask-first 0.270. Reported paired differences are:

- Checker minus direct: +0.261, 95% CI [+0.186, +0.336].
- Checker minus generic: +0.131, CI [+0.068, +0.194].
- Checker minus ask-first: +0.294, CI [+0.217, +0.375].

The checker's reported success rises from 72.4% to 81.5%, irreversible errors fall from 22.9% to 3.1%, and timeouts rise from 4.7% to 15.4%. The intervention does more than suppress errors, but some avoided errors become timeouts, and execution remains inefficient.

Its processed-token cost is 8,676 per episode, versus 5,168 direct, 11,430 generic and 6,873 ask-first. Ratios computed from the reported means are:

- 1.68 times direct cost;
- 0.76 times generic cost;
- 1.26 times ask-first cost.

Thus the checker has a favorable observed return/cost comparison against generic verification. It offers higher return at higher cost than direct and ask-first. These are distinct operating points, not a matched-compute result.

The social-handoff replay counts are especially useful: 49 would-fail handoffs vetoed, with no would-succeed social handoffs vetoed in that table. Report the exposure and uncertainty; this does not establish universally perfect checking. For stochastic physical/testimony actions, an action that happened to succeed in the sampled world can still be rational to veto ex ante. Do not call every such veto a false positive.

The data support a benefit from structured checking plus execution constraints in this setting. They do not isolate the contribution of a joint relational representation from all other symbolic inference or planning components: there is no deployed marginal-versus-joint gate ablation in this fallback. Keep the CPU representation contrasts separate from the LLM rollout result.

## 3. The frozen cost screen was restrictive

The agent correctly applied the stated rule: versus ask-first, 26% extra tokens exceeds the allowed 10% increase, so the fallback fails that screen.

That rule was a research screening choice in my brief, not a general definition of a useful system. A return increase of +0.294 for 26% more tokens is a potentially worthwhile tradeoff. It would be wrong to interpret the failure as proof that the checker offers no efficiency value.

On the observed means, direct itself has higher return and lower token cost than ask-first; uncertainty on their return difference remains substantial. Asking is therefore not the decisive competitor suggested by the binary screening label.

Retain the old classification and add this interpretation explicitly. Any future protocol should evaluate a predeclared return/resource frontier or a justified fixed resource budget, with uncertainty, rather than using this single tolerance as a general veto on large quality gains. Do not rerun this study merely to obtain a pass under a revised rule.

## 4. The stronger objection is the cheap symbolic solution

The CPU gate reports one relation at roughly 17–28 microseconds and all relations at roughly 19–31 microseconds. Their shared computation removes the supposed per-unit cost. This is evidence against the hybrid's economics in the tested finite-model regime, not a theorem that selective computation is never useful.

The report also gives an exact public-model Bayes expected return of 0.885. If that planner can operate on the same public inputs, it is a strong alternative to retaining an LLM as the decision-maker. Its planning runtime is reported as 4.3 seconds for 192 states, approximately 22 milliseconds per state.

However, this is presently an exact expectation/reference calculation, not a supplied head-to-head rollout baseline. Verify the input contract and deployment implementation before claiming that an experimentally evaluated CPU-only system dominates every LLM system. Zero LLM tokens does not mean zero compute.

In particular, distinguish:

- a public model parsed/compiled from the same task description and observed history available to the LLM;
- task-specific engineering supplied in advance;
- a simulator Scenario object, role mapping, construction ID or prior unavailable to the agent.

All can be useful research objects, but they must not be conflated. Hand-compiling known task templates is legitimate if disclosed; privileged constructor metadata must not silently become runtime input.

## 5. Do not overstate the proposed regime change

The conclusion should not be that useful mental computation requires a public model that is not machine-executable. Any implemented inference procedure is executable; known transition rules can remain part of a meaningful language-grounded task.

The relevant open question is whether reconstructing the appropriate perspective relations from legal observations is genuinely uncertain or computationally costly, and whether selective refinement beats cheap parse-once/dense tracking and generic reasoning at a measured budget.

Natural-language role-play might create that problem, but it does not establish it automatically. It also introduces new difficulties: valid mental-state targets, stochastic character behavior, leakage from private cards, inference calibration and outcome verification. Merely replacing templates with natural language can leave a cheap encode-once solution intact.

Do not begin a Tier 2 redesign simply because the current result is inconvenient. It would be a separately specified project extension with its own novelty and feasibility argument. The original spotlight-oriented allocation contribution is not established by this block.

## 6. Close the block with the actual evidence bundle

Export existing artifacts only. No new model runs, seed sweeps, prompt changes or paid calls are needed for this request.

Provide a compact bundle containing:

- The frozen fallback protocol, configuration, prompts, seed list, manifests and source commit/diff.
- The relational engine, gate state machine, deployment input adapter, CPU qualification script, public-model Bayes planner and relevant tests.
- Per-episode CSV/JSON with scenario grouping, condition, return, outcome, steps and complete usage; analysis script and outputs.
- Veto/intervention records with evaluator-only fields clearly separated from deployed inputs.
- Representative direct/checker/generic traces for successful social discrimination, correct ex-ante rejection of a lucky action, a gate-induced timeout and a missed opportunity.
- The Bayes-reference inputs and values, plus an explanation of whether runtime depends on hand-compiled templates or simulator metadata.
- Exact exported-byte hashes and the unchanged spend ledger.

Correct the statement that the 3c decrease “is policy-draw variance” to “is consistent with sampling variability; no check fired in the cited failing checker episodes.” The absence of a check there does not independently establish the cause of the entire condition difference.

After exporting, leave services stopped. The decision remains: hybrid closed in this regime; fallback failed its original screen; positive symbolic-checker evidence retained; no new experiment authorized.

## 7. Review limits

Only the three reports were attached for this turn. I checked their arithmetic against the prior execution brief and computed ratios from the reported means. I have not independently reproduced the new episode-level estimates, confidence intervals, 1,008 qualification checks, reported tests, information-boundary audit or Bayes calculation. Those require the existing source/data bundle requested above.
