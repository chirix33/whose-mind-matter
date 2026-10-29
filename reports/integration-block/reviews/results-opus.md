# Results gate (Opus, scientific validity): integration block D-016

Reviewer: Opus 5.5 (scientific validity). Date: 2026-10-29. Scope: Entries 1 and 1a, freeze `integration-freeze.json` (7877fa0), outputs at a4fb562. I made no model calls and no new runs. My checks were read-only scratch scripts over the frozen artifacts.

## Verdict: PASS WITH REQUIRED CHANGES

The probe ran as frozen, and the pre-declared readings follow the RC5 code. Two parts of the summary are wrong or incomplete. The label "neither (practically small)" is wrong for post|implication. The omission "harm" leaves out its positive-control counterpart. The changes below concern wording and reporting only. None needs a new run.

## 1. Execution and reading computation

**Checked and passing:**
- **Rows:** 1,536 records with 1,536 unique (state, context, condition, draw) keys and no duplicates. Each of the 8 cells has 192 rows.
- **Hashes:** every record's `prompt_sha256` equals the frozen hash. The t0 duplicates are byte-identical (`checks.t0_duplicate_prompts_identical`). All `source_sha256` entries match the current tree. Every record's `bayes_optimal` set equals the frozen set.
- **Dispatch:** the frozen order has 1,536 jobs. Each condition comes first in a (state, context, draw) block 64/64/64 times at t0 and 38 or 39 times post-ask, so the rotation was counterbalanced as declared.
- **Decoding:** temperature 1.0, max_tokens 1,024, reasoning low and concurrency 8, all as frozen.
- **Failures:** 11 attempts were truncated (`finish_reason=length`, logged as `request_error`). Every one succeeded on retry under the frozen 3-attempt rule, and there were 0 fallbacks. The failed attempts are spread over the conditions (t0|impl 4, t0|none 2, post 0–2 each), and no context is flagged for fallback-rate spread. The exclusion sensitivity is therefore identical to the primary analysis. The retry selects on non-truncated outputs, but this affects only 11 of 1,547 attempts.
- **Qualification:** only the `stale` status appears post-ask, there is no `unknown` mass, and there are 80 implication lines.
- **API spend:** the worst case was USD 0.42, within the 0.50 cap. The run cost USD 0.05509, and the ledger stands at 3.869 → 3.924, below the USD 5 cap. The run made one attempt per decision, and all 16 responses completed.

**Readings.** `reading()` checks the harm branch first, then helps, repairs, neither and uncertain, in the RC5 order.
- **t0|implication = harm** is correct. Negative-pair impl−content wrong is +0.115, CI lower bound +0.031 > 0.
- **post|omission = harm** is correct. omit_main wrong is +0.083 [+0.016, +0.141], so the CI lower bound is > 0.
- **post|implication = "neither"** is mechanically correct, but the label is wrong. impl_main wrong is +0.083 [−0.036, +0.208]:
  - The harm branch does not fire, because the CI lower bound is −0.036.
  - The neither branch does fire, through its "point ≥ 0" clause. The pre-registered text and the code are logically equivalent here.
  - However, "(practically small)" does not describe +0.083 with an upper bound of +0.208. The impl_main gap of +0.117 [−0.119, +0.367] also points the harmful way. The correct meaning is: no help, harm not excluded, size unresolved (RC5 "neither" applied through the non-negative-point clause).

## 2. Mechanism

**t0 implication in 3b.** In 3b every handoff is a wrong handoff, so the wrong rate equals the handoff rate.
- Pooled over stakes, the handoff rate is none 0.062, content 0.167, impl 0.354. Gives under impl rose from 8 to 17 of 48, and all 17 were wrong.
- 2b barely contributes (t0 wrong: none 0.083, content 0.042, impl 0.083). The pair-level t0 harm is essentially a 3b effect.
- The implication line is not false. K(F→R) is correct, and "give(F) sends to X with probability 1.00" is a correct application of the public rule. The error is that R's own belief changed through a quiet conversation that is visible in the history, and K(R) is not allocated.
- The reasoning texts show the policy treating the destination as success, for example: "he forwards to desk_9. Zane is in desk_9 (he believes meeting_room=desk_9)". The certainty wording itself is rarely quoted ("probability 1"/"certain" appears in about 3 of the 17).
- This is consistent with the RC4 certainty confound, but not identified by it. The probe has no case with a certain *and* correct destination. It therefore cannot separate a certainty-keyed heuristic from conflating the destination with the recipient's current belief. In 2a the stale courier also gets a certain-wrong line, yet t0 2a handoffs did not rise (0.062 → 0.042), so the effect is construction-specific.

**Omission harm after the ask.** Omitting the stale line raises handoffs in both pairs:

| Pair | Handoff rate, shown → omitted | Effect of omission |
| --- | --- | --- |
| Negative | 0.578 → 0.609 | wrong +0.083 |
| Positive | 0.417 → 0.500 | correct +0.078 [+0.010, +0.151] |

- The symbolic check matters here. In all 16 negative base units, the standardized ask leaves both the true content and the public posterior unchanged (`qualification.json`, `symbolic`). There the stale line carries no validity information.
- In 2a-asked-H and 3a, the ask does change the posterior (50/50 → certain), while the displayed note stays frozen at t0.
- The policy's response to the stale line does not track this difference. The line acts as a non-specific caution signal.
- Measured against no notes, omit_avg−none wrong is only +0.057 [−0.031, +0.151]. Omission removes a caution effect; it is not clearly worse than no notes.

**2a post-ask split.**
- Asked-H covers 5 seeds (n = 30 per condition). Correct handoffs are 0.47–0.63 in every note condition and 0.50 for none.
- Asked-N covers 3 seeds (n = 18). The policy re-asks almost every time, and correct handoffs are 0.00–0.06 in every condition.
- The positive-control post-ask evidence therefore rests mainly on 2a-H and 3a. The split is thin.

**API check (§5 bullet 3).**
- 16/16 decisions were Bayes-optimal (gap 0), and the notes changed no action (8/8 identical none/content pairs).
- At the same 8 contexts the local policy made 5 wrong handoffs in 48 decisions: 2b post 2 and 3b t0/post 3.
- So the no-note API policy left no headroom on these 8 contexts. The within-API note contrast is uninformative at the ceiling; it does not show that "notes gain nothing" in general.
- The two policies also differ in configuration: 1 draw and no temperature for the API, and different output caps and effort semantics.

## 3. Audit v2

**Findings.**
- **Existing asks in the reference episodes:** every 2b and 3b ask left both content and posterior unchanged. In 3a the posterior almost always changed. 2a-asked-H was mixed and 2a-asked-N unchanged. The person's belief is never changed by an ask (true content is unchanged in 100% of cases), so every posterior change is a robot-estimate update. This distinction is reported correctly.
- **Stale exposure:** ≈100% of decisions after an ask, and lower for sighting-only decisions.

**Limits.**
- In 2b the rubric codes 82 of 86 decisions as "other", so it says nothing about 2b drop decisions.
- In 3b, 28 of 58 decisions are coded forwarding_rule, all errors, with 8 uncertain.
- The reasoning codes are heuristic and not causal.
- The symbolic table is listed per unit name and has no per-construction aggregate.
- The post-ask action tables compare episodes that chose to ask with those that did not, which is selection by policy. The audit correctly makes no causal comparison.

## 4. Required changes to the summary or handoff (no new runs)

1. **Relabel post|implication.** Replace "(practically small)" with "neither by the rule's non-negative-point clause: no help; harm not excluded". Report wrong +0.083 [−0.036, +0.208] and gap +0.117 [−0.119, +0.367]. Treat it under §5 bullet 5 (unresolved), with an approximate seed count a resolving test would need. Do the same for the interaction (negative wrong +0.062 [−0.125, +0.250]).
2. **Keep the harm readings descriptive.**
   - Report 16 base units per pair, CI lower bounds of +0.031 and +0.016, and sign-flip p = 0.045 and 0.043, with no multiplicity correction across the 3 readings. Holm over 3 would not reach 0.05.
   - State that the t0 harm is carried by 3b.
   - Do not call either effect established.
3. **Comparisons with none, both pairs.**
   - **Negative pair:** no note condition beats no notes at either context (t0 content−none +0.031, impl−none +0.146; post content|shown−none −0.052 [−0.219, +0.104]).
   - **Positive pair at t0:** notes reduce correct handoffs relative to none (content −0.104, impl −0.125 [−0.229, −0.031]) because the policy asks more.
4. **Omission.** Report the positive-control rise in correct handoffs and the handoff-rate shift in both pairs next to the harm reading. Add the symbolic fact that the stale line carries no validity information in the negative pair. Describe the line as a non-specific caution signal. Do not invoke §5 bullet 2 or propose dependency-aware invalidation. The data do not support it, and a dependency-aware label would remove the line precisely in the negative pair.
5. **Implication mechanism.** State that the line is a correct application of the public rule. The harm is consistent with the RC4 confound but not separated from it. The missing information is R's changed belief, an unallocated unit. Never say the mapping was false or "misled" through incorrect content.
6. **API.** Apply bullet 3 with the ceiling caveat, configuration differences and n = 8 contexts with 1 draw each. Describe the result as consistent with a local-policy capability limitation; it is not a backbone benchmark and not evidence about note value. Include the local comparison at the same 8 contexts.
7. **Execution facts.** Report the 11 truncated attempts, all recovered on retry, with 0 fallbacks, and list the hash and dispatch verifications.
8. **Audit limits.** Add the 2b rubric's uninformativeness, the 8 uncertain 3b cases, and an aggregated per-construction symbolic table.
9. **§5 mapping.**
   - **Bullet 4 governs** (neither factor helps): stop further content and display tuning and return to a method/environment review.
   - **Bullet 3:** descriptive.
   - **Bullet 5:** for post|implication and the interaction.
   - **Bullets 1 and 2 do not apply.** Propose no integration component, no invalidation rule, no rollout stage and no new seeds or backbones.
10. **Do not claim:**
    - any return or episode-level effect;
    - any allocation or depth conclusion;
    - that implication lines are harmful in general;
    - that stale labels are valid or useful;
    - that the API policy is superior;
    - that notes have value for the API policy.

    Restate the ruling's final caution: coaching a weak policy through selected false-belief cases would not satisfy the objective.
