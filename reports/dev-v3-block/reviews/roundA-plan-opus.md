# Round A/B plan gate: scientific validity (Opus 5.5)

Reviewed: `reports/dev-v3-block/experiment-plan.md` (Entries 1–2) against `POST_BLOCK_RESEARCH_DECISIONS.md` (D-014) and AGENTS.md §5/§7. Background read: `src/officeminds/world.py`, `src/officeminds/devgen.py`, `src/vomi/oracle.py`, `src/vomi/units.py` (`content`, `default_holds`), `PEOPLE_RULES_R5` in `src/vomi/pilot.py`, `reports/autonomous-block/FINAL_REVIEW.md`. No code exists for dev-v3 yet, and I saw no dev-v3 outcomes. This gate checks LLM reasoning and arithmetic. It is not independent scientific validation (D-014 §Disposition).

**Verdict: PASS WITH REQUIRED CHANGES.** The overall design follows the ruling: 4 strata × 3 constructions, name permutation × stakes, a balanced distractor block, shared hidden draws, ask and search kept legal, no caution text, a hash selection, four fixed-allocation conditions, and a local backbone. The 4a stakes threshold is correct. Several checks are vacuous or wrongly specified as written, though. One Round B rendering rule would bias the `reference` condition, and the reading rule cannot be interpreted at this sample size. All items below must go into the plan before any dev-v3 code is frozen. Items R1–R15 need no outcome to fix.

## Arithmetic I recomputed
The layout is lobby–hall–{3 offices}. Every action costs −0.05, success adds +1, and an error costs −0.5×stakes.
- Terminal action at t1 (give/drop): 0.95. Ask then drop: 0.90. Walk to a known office and deliver: 0.85. Search over 2 equiprobable offices: (0.85+0.75)/2 = 0.80. Search over 3: 0.75 (7 steps ≤ horizon 8, so it is feasible). 2c search (final location 1/2 o_a, 1/4, 1/4): 0.775.
- 2a: give(H) 0.95, ask(H)+drop 0.90, search 0.80. Correct.
- 2b: search 0.80; drop(o_a) and give(N) are errors. Correct.
- 3a: give(F) 0.95; ask(F)+walk 0.80; search 0.80. Correct.
- 3b: ask(F)+walk 0.80 and search 0.80 tie exactly in expectation, so the optimal set is {ask(F,·), move(hall)}. Correct.
- 3c: give(F) 0.95, walk(o_a) 0.85. Correct.
- 4a: drop EV = (1−q)·0.95 − q·(0.05 + 0.5·stakes), so ×1: 0.95 − 1.5q and ×4: 0.95 − 3.0q. Walk-then-search EV = 0.85 − 0.15q. That gives q* = 0.10/1.35 = **0.0741** and 0.10/2.85 = **0.0351**. Confirmed. With q ∈ {0.05, 0.06} the Bayes action flips. The gaps are small: 0.019–0.033 at ×1 and 0.043–0.071 at ×4.
- 4c: the same formulas apply with r in place of q, assuming X saw R, R is stationary, and X is not a courier. The flip holds for r ∈ {0.05, 0.06}.
- 4b: the plan gives no numbers. With π = P(R at X's office | statements), the thresholds are approximately π* ≈ 0.926 (×1) and ≈ 0.965 (×4). Some pairs fail: (p_X, p_Y) = (0.05, 0.9) gives π ≈ 0.969, so drop wins at both stakes and there is **no flip**. Other pairs work: (0.06, 0.8) gives π ≈ 0.954, which flips. **4b is the stratum-4 group that the Round B hash selects** (see below).
- Round B selection, computed from the declared formula: stratum1 → index 2 (**1c**), stratum2 → 0 (**2a**), stratum3 → 2 (**3c**), stratum4 → 1 (**4b**). The distractor levels of the selected groups are none / obvious / obvious / obvious. No plausible distractor is run. The depth pair 3a/3b is not in Round B.

## REQUIRED changes

1. **Make the evidence-resolution check non-vacuous (D-014 §4, Round A bullets 3, 4 and 8).** Each group's prior fixes its construction: who talked to whom, who departed, how many moves. Only office and intent values vary. So check A.3(4), "access status identical in every world consistent with the t0 history", holds by construction, and check 3 cannot tell the history from the template. Add two things:
   - (a) A **superset check**. For each of strata 2 and 3, define one stratum-level public model in which the communication pattern varies across worlds (2a/2b/2c patterns and holder swaps; 3a/3b/3c), with a stated prior. Condition ExactOracle on the **rendered visible prologue, as observations**. Show that the posterior over focal-unit contents and the first-action Q-values equal those from the construction-specific prior.
   - (b) A **card-only triviality assessment**. Run the Bayes actor on the card or public-model text without the prologue's communication events. Record any group whose card alone fixes the best action or a focal role, and treat that as public task information, as the ruling requires.
2. **Fix the same-physical-state pair list (A.3(6)).**
   - 3a vs 3c is *not* a same-physical-state pair. R is in the new office in 3a and in o_a in 3c. Relabel it as a "same courier-own-belief, different recipient belief" contrast, or drop it from this check.
   - Define "2b-without-departure". 2a vs 2b differs in whether H is present, which is a physical availability contrast. State it as such.
   - The cross-group pairs (3a/3b, the 2a holder swap) come from different public and hidden draws: different names, labels and new office. State how each pair is built so that it shares names, labels and the exogenous draw. Either use dedicated pair instances or match worlds by office value over the support.
3. **State the depth certification against a formal class, and correct the "only F→R differs" claim.**
   - Name the class Π≤1: policies whose inputs are the card/public model, the physical observation, and the contents of every depth-0/1 unit (K(x) and R(x) for all people), with no raw history.
   - Claim: 3a and 3b give identical Π≤1 inputs, but their optimal first-action sets differ ({give(F)} vs {ask(F), move(hall)}). K(F→R) resolves the difference.
   - Correct A.2. Under world.py semantics, R→F also differs (F tells R in 3a, so R thinks F holds the new value; in 3b R→F = o_a), and so does A→R. The pair therefore certifies **depth 2 relative to Π≤1, not path direction**. To support C4 path asymmetry, report the privileged and grounded values of K(R→F) and K(A→R) next to K(F→R) under the superset model of item 1a.
   - State explicitly that nothing is claimed about the LLM's reasoning depth (AGENTS §5.5), and that 3a and 3b are not in Round B.
4. **Pre-declare the stratum-4 parameters and arithmetic.** For 4b, give the fixed (p_X, p_Y) pairs. For 4c, give the r values. For each, give π, the drop and walk EVs at ×1 and ×4, and the resulting Bayes actions, in the same form as 4a. Some candidate 4b pairs do not flip (see above). Pre-declare the fallback: if a pair fails qualification, the generator's pair set is fixed before the freeze and the change is recorded.
5. **Declare couriers and persistence for each construction, in both the card and the config.**
   - List the handoff_routes for every construction, especially stratum 4. In world.py, `give` routes by the courier's *own belief* whatever their intent. If W, X or Y is a courier, give(X) succeeds with 0.95 even when X is obstructive (both reporters "saw R"). That dominates and removes the stakes flip.
   - Specify what an obstructive courier does, given the "I'd rather keep that package myself" remark in 4c.
   - Also declare publicly that departed people do not return within the horizon. A departure ("leaves the building") must render differently from walking to an office.
   - Declare that R stays put during the episode in every stratum, and that in 4b/4c R has not moved since being seen.
6. **Specify the quiet-conversation and presence semantics in r6.**
   - Give presence lists for every prologue event of 3a, 3b and 3c. In particular, does F see A talk quietly with R in 3b? If F is present, either r6 must say that bystanders of a quiet conversation form no belief about the listener (as r5 rule 5 does now), or F→R would not be stale. Recording this matters because a reader could reasonably infer otherwise.
   - State where the plausible distractor P is during quiet conversations: absent from the lobby, or present without hearing.
   - Add the new event kinds (quiet conversation, departure) to the A.3(1)/(2) tests.
7. **No undisclosed testimony prior; disclose honesty dependence.**
   - Every primary dev-v3 quantity must use the plain posterior b_h: check 5, check 7, the headroom baseline and the Round B `reference` payload. None may use the GROUNDED_* bounded actor, whose `TESTIMONY_DEFAULTS` ε = 1e-6 face-value prior is an undisclosed honesty assumption. Add an assertion test.
   - For each stratum 2–3 label, record that it is evidence-resolved *given* the declared "everyone is cooperative" rule (a disclosed zero-probability alternative) and the declared content of quiet conversations (D-014 §1, §4).
8. **Fix the reference-note rendering and define privileged content.**
   - "Grounded if max p ≥ 0.8, else uncertain" labels a *certainly current* unit as "uncertain" whenever its value is open. Examples: K(H) in 2a (value uniform over two offices, so max p = 0.5) and K(F→R) in 3a. For 3a/3b and the holder swap, this systematically signals unreliability in exactly the cases where the person is informed.
   - Render the access/truth status (the `default_holds` marginal) separately from the value distribution, in fields the pilot-v2.1 inferred format can also express. Freeze the exact rendered payloads. If the format cannot express the distinction, record that as a pre-outcome limitation and apply it to every computed condition alike.
   - For privileged K units, state whether the payload is the belief value only (`units.content`) or the value plus truth status. The truth status reveals the physical target, for example K(W) in 4a.
9. **Declare note retention.** State whether a note is shown at every policy step, with its t0 timestamp and evidence IDs, or only at t0. Apply the same rule to inferred, reference and privileged notes. "No refresh" alone does not settle this.
10. **Make the reading rule unambiguous and aware of noise.** With 4 states × 3 draws per stratum and error returns of −0.55 or −2.05, a ±0.05 cut is far below the plausible SE of a stratum mean difference (roughly 0.2–0.3 at a 10% error rate). Before the freeze, state:
    - (a) the readings for `reference` and `inferred` separately (reference headroom is not deployable value);
    - (b) that "2 of 4 strata" means 2 of strata 2–4, and which condition the stratum-1 tolerance applies to;
    - (c) a third outcome, **inconclusive**, used when the per-state paired differences or the bootstrap range include both 0 and ±0.05. Alternatively, report the rule's operating characteristics, simulated from the previous block's per-episode variance.
11. **Pre-declare failure handling.** For notes: the number of attempts, the bounded retries, and which payload is frozen when generation fails. For policy outputs: invalid, truncated at 1024 tokens, unparseable, or timed out. State how each is scored and logged. Do not resample until an output is valid (AGENTS §8).
12. **Compute the B2 API reservation before dispatch.** Give the worst case as calls × max tokens × price, including notes and retries, and show that it is at most the reconciled remaining balance minus a stated failure reserve. State what happens if the cap halts the batch partway, for example passes over all 64 cells in counterbalanced order, with partial results reported. Give the API note decoding settings.
13. **No LLM touches dev-v3 before the freeze commit.** This includes rendering and format smoke tests. Use dev-v2 or synthetic fixtures for engineering checks.
14. **Correct the provenance and expose the dependence on design choices.**
    - Replace "Neither layout nor horizon was chosen from any LLM outcome". The three-office layout and stratum 3's missing chute were chosen knowing that dev-v2 asking and search were cheap, and in order to create task-level headroom. That is allowed: it is pre-declared and not tuned on dev-v3.
    - "No chute" is defensible as a pre-declared scenario feature, applied to the whole stratum and disclosed in the card. To be clear that it does not remove a solution after outcomes, Round A must also report the **with-chute counterfactual** first-action Q-values for 3a–3c. With a chute, 3c has drop(o_a) = give(F) = 0.95, so K(F→R) has no task-level relevance there.
    - Note that chute availability confounds cross-stratum comparisons.
15. **Extend the shortcut and independence checks.**
    - Check 8: agent-visible text must never contain instance, group or construction IDs, stratum names, construction labels (relayed / stale / uninformed / departed), or focal-unit lists. A note's own unit header in the note conditions is the only exception.
    - Check 10: add the ruling's "prior independence" item. The hidden stream must be independent of the variant and the public draw, and the declared factor independences (X and Y obstruction, the lie target per person) must hold in the constructed prior.

## Recommended (optional)
- Record the resolved Round B selection (1c, 2a, 3c, 4b) in the plan now. Note that the selected set has no plausible distractor and no depth-pair group, and that it stays as declared.
- Add same-physical-state *social* pairs in stratum 4. In 4b, swap which reporter has the high rate. In 4c, compare with and without the incentive remark (r vs 0 at ×4 changes walk to drop). Stratum 4 currently has only stakes pairs.
- Acknowledge in the analysis that allocations are chosen by the designer with privileged relevance knowledge. The note header (which unit is shown) is a cue confounded with content, especially in strata 2–4.
- Classify privileged-note benefit by mechanism: physical-target leakage (K(H) in 2a, K(F→R) in 3a, R(X) in 4b, the truth status of K(W)) versus self-location versus perspective content.
- In 4a, either drop "says when they saw R" or make q a declared function of the stated time. As written, the time is an irrelevant cue.
- Check before outcomes how pilot-v2.1's RULE1–6 citations map to the r6 clauses, and record mismatches without editing the package.
- Pin the scoring-v3.1 source hash, including its post-inspection tie rule, in the freeze. Define operationally what "adds no new content" means.
- A bootstrap over 4 highly dependent states (one hidden draw) is close to uninformative. Lead with per-state raw draws.
- State the fixed design proportions (25% per stratum; one distractor level per construction, which confounds level with construction) and that the stratum-4 Bayes gaps (0.02–0.07) cannot be detected at this sample size.
- Report latency only as descriptive, since vLLM prefix caching and concurrency 4 make it not comparable across conditions.

## Short reasoning
- **Public alignment.** Disclosing rates, the lie model and conversation content in a generated card answers the core D-014 §4 concern. The remaining gaps are the undisclosed persistence and courier facts (R5), the bounded-actor ε prior (R7), and the fact that the "evidence-resolved" status currently comes from the template, not the history (R1).
- **Mental relevance and fairness.** The constructions do create same-physical-state, different-history action differences: the 2a holder swap and 3a/3b. The direct arm keeps the full history, asking, search and the rules, and nothing is removed after outcomes. The faults are in the specification: mis-listed pairs (R2), an overstated depth claim (R3), and a missing 4b specification for the very group Round B will run (R4).
- **Round B.** The structure is sound: frozen notes at temperature 0 hashed before the policy runs, an unseeded temperature-1.0 policy, full resets, and counterbalancing. The rendering rule (R8) would confound the `reference` condition. The reading rule (R10) would turn noise into a verdict. Undeclared retention and failure handling (R9, R11) leave room for choices after outcomes are seen.
