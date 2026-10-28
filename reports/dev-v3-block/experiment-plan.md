# dev-v3 qualification block: pre-registration

Authority: D-014 (`POST_BLOCK_RESEARCH_DECISIONS.md`). Development data only. Two rounds; return afterwards.
Gates (same as the previous block): Opus checks the validity of each plan and result set; Sonnet independently recomputes numbers. A conclusion is recorded only after both pass. Entries below are append-only; amendments are dated and placed before the outputs they affect.

## Entry 1 — Round A design (written before any dev-v3 code or output)

### A.1 What is new in dev-v3 (vs dev-v2)
1. **Visible prologue.** The task starts after a short prologue the robot watched in the lobby. Every lobby event is shown, in order, with who else was present: announcements, statements, ordinary remarks, quiet conversations (seen but not heard), arrivals and departures. Events in other rooms are not shown. dev-v2 had invisible backstory plus t0 remarks only.
2. **Declared public model per group.** Every rate, prior, response model and template choice the reference uses is printed in the task card ("PUBLIC MODEL OF THIS TASK"). The text is generated from the same specification object that builds the prior, so the two cannot diverge. Priors are disclosed; realized hidden values are not.
3. **Public rules r6** (render revision 6). Six numbered rules, same numbering themes as r5 (rule 2 self-location, rule 5 beliefs about beliefs) so pilot-v2.1's frozen prompt still applies. They describe the dev-v3 event semantics and must hold over every positive-prior world of every dev-v3 group (tested).
4. **Layout.** lobby (chute, except where stated) – hall – three offices. Three offices make search cost visible (2, 4 or 6 extra steps) without changing reward coefficients (+1, −0.05/step, −0.5×stakes error). Horizon 8, which still allows a full three-office search and delivery. Neither layout nor horizon was chosen from any LLM outcome.
5. **Lie model.** An obstructive person names a wrong office chosen uniformly among the others and repeats the same office if asked again (a per-person hidden value). This replaces dev-v2's undisclosed "first other value" rule.

Unchanged: rewards, actions (move, ask, drop, give, deliver, wait), ask semantics (answer = own belief; obstructive = the lie), handoff semantics (a courier forwards to where they believe the package should go), the pilot-v1 policy prompt, the pilot-v2.1 unit package, notes rendering, and the PerspectiveGraph protocol. **No caution reminder is added** to any instruction (D-014 item 6); the task card already states rewards and the disclosed rates.

### A.2 Strata, templates and groups (12 groups = 4 strata × 3 constructions)
Notation: R recipient; offices o_a (first announced), o_b/o_c the others. "Quiet conversation" = the robot sees the two people talk quietly but cannot hear; the public model states what such a conversation conveys.

**Stratum 1: physical/STOP controls (irrelevant people).** Mental units should have zero value.
- 1a *announced*: R announces "R_loc = o_a" in the lobby and leaves. Public model: R went to the announced office and stays there. Expected best action: drop(o_a).
- 1b *unannounced*: R leaves without saying where. Public model: R went to one of the offices (uniform) and told no one. Search is optimal; asking anyone yields "I don't know".
- 1c *announced, then irrelevant chatter*: as 1a, plus statements by others about other matters.

**Stratum 2: evidence-resolved first-order relevance (quiet update, handoff).** Couriers (non-recipient colleagues) forward a handed-over package to where they believe R is. Public model: R announced o_a, later moved to one of the other two offices (uniform), and on the way told the new office quietly to exactly the people shown; everyone is cooperative.
- 2a *one informed colleague*: H and N heard the announcement; R later talks quietly with H. Expected: give(H) (0.95); give(N) is an error; ask(H)+drop 0.90; search 0.80.
- 2b *informed colleague departed*: as 2a, then H leaves the building. Only stale N remains. Expected: search the two other offices (0.80); give(N) and drop(o_a) are errors.
- 2c *two updates (recency)*: R moves twice (each time to an office other than the current one, uniform), telling H after the first move and N after the second. Expected: give(N).

**Stratum 3: evidence-resolved directed depth-2 / relay, departed organizer, no chute.** Fact `meeting_room`. R goes to, and stays in, the office where R believes the meeting is. Courier F forwards to where F thinks R will go: F's belief about R's belief (path F→R). Public model: organizer A announced o_a; R stated "meeting_room = o_a" in front of F; A later changed the meeting to one of the other offices (uniform) and conveyed it in the quiet conversations shown; then A left the building; everyone is cooperative.
- 3a *relayed*: A talks quietly with F; F then talks quietly with R. F→R current. Expected: give(F) (0.95).
- 3b *depth-2 stale*: A talks quietly with F, then separately with R. F's own belief is current, but F→R is stale (o_a), so give(F) is an error. ask(F) reveals the new office (then walk: 0.80); search 0.80.
- 3c *R uninformed*: A talks quietly with F only. R still believes o_a and is there; F→R = o_a. Expected: give(F) (0.95) or walk to o_a (0.85). ask(F) returns F's own belief (the new office), which is the wrong delivery room.
3a vs 3b is the depth-certification pair: R's location, R's belief and F's own belief are the same; only F→R differs, and the best first action differs.

**Stratum 4: probabilistic (shared disclosed priors; stakes matter).** Disclosed rates are fixed per group from a public draw. Ranges were chosen so that the ×1 and ×4 stakes put the Bayes threshold on different sides (computed from the reward coefficients, not from any LLM run).
- 4a *staleness*: cooperative W states "R_loc = o_a" and says when they saw R. Public: since then R moved to another office (uniform) with probability q ∈ {0.05, 0.06}. Expected: drop at ×1, walk at ×4 (thresholds q* ≈ 0.074 and 0.035).
- 4b *conflicting reporters*: X says o_a, Y says o_b. Public: each saw R; each is obstructive independently with the disclosed probability (X low, Y high, drawn from fixed pairs); R's office is uniform; the lie model is A.1(5).
- 4c *incentive*: X states an office and remarks "I'd rather keep that package myself." Public: a person who says that is obstructive with probability r ∈ {0.05, 0.06}; everyone else is cooperative.

**Distractors (balanced block, fixed in advance).** For stratum s ∈ {1..4} and construction index g ∈ {0,1,2}: level = (g + s) mod 3 → none / plausible / obvious.
- plausible: an extra colleague P is present for every lobby event except quiet conversations, and stays.
- obvious: an extra person D arrives after the prologue and says "I just got here."
- Distractors are never couriers, so the action set does not change by distractor level, except for P's and D's ask actions.

**Variants per group (4 instances).** Stakes ×1/×4 × name permutation (all role names cyclically rotated by one position, recipient included). The permutation is structurally isomorphic and observationally distinct (names change). Holder-swap minimal pairs with fixed names and physical state are built separately (A.3). The four variants share one public parameter draw and one hidden draw. Names come from a 25-name pool and office triples from a label pool, with random listing order. The roster is sorted.

**Hidden sampling.** Each group's prior is built from its public specification. The hidden world is drawn once per group from a separate RNG stream (`dev-v3:hidden:<group>`) after the public draw. Seeds: base 20261029.

**Focal units (fixed allocation for Round B; by construction, declared here).**

| Stratum | Constructions | Focal unit(s) |
|---|---|---|
| 1 | all | K(person) for each non-recipient person present at t0; if none, K(R) (self-location, audited separately) |
| 2 | 2a, 2c | K(H), K(N) |
| 2 | 2b | K(N) |
| 3 | all | K(F→R) |
| 4 | 4a | K(W) |
| 4 | 4b | R(X), R(Y) |
| 4 | 4c | R(X) |

### A.3 Qualification checks (Round A; must pass before freezing)
Computed by `scripts/qualify_dev_v3.py`; exhaustive over each group's finite support; free/local.
1. **Rules vs transitions:** each r6 clause holds in every positive-prior world of every group, at t0 and after every legal first action (tests).
2. **Belief semantics:** true/false/unknown beliefs, self-location (R knows R_loc), perspective access (only listed listeners update; quiet content reaches only the named listener), and depth-2 contents as designed in A.2 (tests on the constructions).
3. **Reference inputs:** the reference is ExactOracle over the group prior, conditioned on visible history. Test: the set of hidden variables, their support and their probabilities equal the disclosed public-model specification printed in the card. The reference never reads the realized world.
4. **Evidence-resolved labels:** for strata 1–3, each focal unit's *access status* (no belief / current / stale relative to the announced value) must be identical in every world consistent with the t0 history (support check). Any remaining spread is only over physical office choices with a disclosed uniform prior; both facts are reported. Stratum 4 is reported as probabilistic.
5. **Ask-aware action values:** for every instance, the exact Bayes-optimal (expectimax, ask/search/give/drop/wait/deliver all legal) Q-value of every first action under the public model, plus the best value of each action family (ask, search, chute, handoff, wait). This is a symbolic reference for an ideal actor, not an LLM value.
6. **Same-physical-state social-history pairs:** for 2a (holder swapped with names fixed), 2a vs 2b-without-departure (control), 3a vs 3b, and 3a vs 3c, show identical recipient location and positions, a different visible social history, and different optimal first actions with the value gap. Also stakes pairs for 4a–4c: Bayes action at ×1 vs ×4.
7. **Unit value, privileged, Bayes actor:** J(∅) vs J({u}) with u's true content revealed (PRIVILEGED_BAYES), per focal unit. Labeled privileged. Zero values are kept.
8. **Shortcut checks:** the roster is sorted; brief and card text identical across worlds of a group except names; the permuted variant's optimal action is the isomorphic image; no hidden parameter name or value appears in agent-visible text except values the history legitimately shows.
9. **Self-location audit:** K(R) units are classified separately (first-person) wherever they occur.
10. **Replay, pairing, rendering:** record → replay identity for scripted rollouts; variants share the hidden draw; the policy and unit prompts render r6 and the public model; prompt hashes are recorded.
11. **Tractability:** oracle runtime per instance is recorded. If any computation is approximate, it is labeled; none is planned.

**Exclusions:** none planned. A group failing a check is fixed in the generator *before* freezing, with the failure and fix recorded; no group is dropped or replaced for lacking headroom. Zero-value controls stay.

**Freeze:** `reports/dev-v3-block/dev-v3-freeze.json` holds hashes of the generator source, every instance's agent-visible t0 view and card, the public-model specs, r6 rules, prompts, strata, focal units, the Round B selection and model settings, plus the git commit. It is committed before any LLM output on dev-v3.

## Entry 2 — Round B protocol (fixed now; executed only if Round A passes)
- **Selection:** for stratum s, construction index = int(sha256("dev-v3:roundB:stratum<s>"), 16) mod 3. All 4 variants of the selected group are used, giving 16 t0 states. No outcome-based replacement.
- **Backbone:** local gpt-oss-20b (vLLM 0.32.0, mxfp4) for both inference and policy, package pilot-v2.1, render r6.
  - Inferred notes: one frozen draw at temperature 0 (validated decoding), produced and hashed before any policy call.
  - Policy: temperature 1.0, unseeded (independent draws; retries must be able to differ), max_tokens 1024, reasoning effort low.
- **Conditions:** fixed allocation of the focal units at t0, with no further allocation and no refresh:
  - **none**: direct rendering;
  - **inferred**: the frozen local note;
  - **reference**: the exact public-model posterior of the unit content given the t0 history, rendered as a computed note in pilot-v2.1 format (status grounded if max p ≥ 0.8, else uncertain);
  - **privileged**: true content, p = 1. Privileged diagnostic only; not a guaranteed upper bound.

  A condition that is byte-identical to another for a state, or adds no new content, is recorded as such and still run.
- **Replication:** 3 policy draws per state × condition = 192 episodes. Each starts from a full reset. Asking and search stay legal. Dispatch order is counterbalanced (conditions rotated by state and replicate index); concurrency 4. Draws are nested within groups and are not independent scenarios.
- **Resource rule:** if the local server cannot complete the run, finish full replicate passes (all states × conditions per pass) in order, and report the number of completed passes.
- **Measures:**
  - raw return, success, error and steps per episode; per state, per group and per stratum means;
  - headroom = the Bayes-optimal t0 expected return (Round A) minus `none`;
  - note fidelity vs the aligned public-model posterior (scoring v3.1) and vs truth;
  - coverage, note and policy tokens, latency.

  Uncertainty: per-state draws are shown raw. Stratum-level contrasts get a paired bootstrap over states within the group (only 4 states per stratum, so this is descriptive). No pooled significance claim.
- **Pre-declared reading (development, descriptive):**
  - **Explicit-note headroom present** if `reference` or `inferred` beats `none` by ≥ 0.05 mean return in at least 2 of the 4 strata, and in stratum 1 (zero-value control) does not differ by more than 0.05 in either direction. Otherwise "no measurable explicit-note headroom on dev-v3" for this backbone.
  - privileged − none is reported separately and never counted as deployable value.
- **Optional API sanity batch (B2)**, only if Round A passes and the reconciled ledger shows ≥ USD 1.00 remaining:
  - API gpt-6.1-sol (low effort) for both notes and policy; the same 16 states and 4 conditions, 1 draw each;
  - per-stage cap = spent + 0.80;
  - reported separately by backbone. Otherwise the missing API confirmation is reported.

## Entry 1a — Amendment after the Round A plan gate (2026-10-28; before any dev-v3 output, and before any LLM call on dev-v3)
Gate report: `reviews/roundA-plan-opus.md` (PASS WITH REQUIRED CHANGES R1–R15). All required changes are adopted below; they override Entries 1–2 where they differ. Engineering status at amendment time: generator and world extensions written; only symbolic smoke runs (no LLM) on dev-v3.

- **R1 Non-vacuous evidence resolution.**
  - (a) *Superset public model*: for every group in strata 2 and 3, a stratum-level scenario with the group's names, offices and distractor, whose prior mixes the stratum's three communication patterns × holder swap (H↔N in stratum 2, A↔F in stratum 3), uniform over the 6 patterns, times each pattern's own disclosed hidden variables. ExactOracle conditions it on the rendered prologue as observations. Pass criterion: the posterior over every focal unit's content and the first-action Q-values equal those under the construction-specific prior (tolerance 1e-9).
  - (b) *Card-only triviality*: the same superset prior with every prologue notice removed from the observations. Record whether the Bayes best-action set, or the focal person, is already fixed. Such cases are reported as public task information, not removed.
- **R2 Pairs.** Built from the superset machinery so each pair shares names, labels and the hidden draw:
  - same-physical-state social pairs: 2a holder swap (H↔N, names fixed) and 3a vs 3b;
  - a *physical availability* contrast: 2a vs 2b;
  - a *same courier belief, different recipient belief* contrast: 3a vs 3c;
  - stakes pairs: 4a–4c.
  Each gets the full first-action Q table and the gap between the optimal sets.
- **R3 Depth certification.** Class Π≤1 = policies whose inputs are the card/public model, the physical observation (positions, holding, outcome) and the contents of every depth-0/1 unit (K(x), R(x) for every person), with no raw history. Claim to be checked: 3a and 3b give identical Π≤1 inputs, but their optimal first-action sets differ ({give(F)} vs {ask(F), move(hall)}). K(F→R) resolves the difference.
  - This certifies depth 2 relative to Π≤1, **not path direction**: K(R→F) and K(A→R) also differ, and their values are reported next to K(F→R).
  - Nothing is claimed about any LLM's reasoning depth. 3a/3b are not in Round B.
- **R4 Stratum-4 parameters (fixed now).**
  - 4a: q ∈ {0.05, 0.06}.
  - 4c: r ∈ {0.05, 0.06}.
  - 4b: (r_X, r_Y) ∈ {(0.02, 0.3), (0.03, 0.4)}, with π = P(R at X's office | the two differing statements) = (1−r_X)r_Y / [(1−r_X)r_Y + r_X(1−r_Y) + r_X·r_Y/2]: 0.945 and 0.942. These are between the approximate thresholds 0.926 (×1) and 0.965 (×4).
  - Qualification asserts that the exact Bayes first action differs between ×1 and ×4 in every stratum-4 group. If a group fails, its parameter set is changed in the generator before the freeze and the change is recorded.
- **R5 Couriers and persistence (in the card and the config).**
  - Couriers: H and N in stratum 2; F in stratum 3; nobody in strata 1 and 4. The card says "Nobody else accepts handed-over packages."
  - Every card states that after the prologue nobody but the robot moves, and that beliefs change only through answers to the robot's questions.
  - People who leave the building do not come back. That is rendered as "leaves the lobby and the building", distinct from "leaves the lobby".
- **R6 Quiet conversations.** The plausible distractor P, and anyone else in the lobby, is present for quiet conversations (shown in "others present"). They see the conversation but do not hear it.
  - r6 rule 1 says a quiet conversation is heard only by the person addressed.
  - r6 rule 5 adds that watching a quiet conversation tells a bystander nothing about what the listener now believes. In 3b, F watches A talk quietly with R, and F→R stays stale under this rule. Tests cover quiet conversations and departures.
- **R7** Every primary quantity uses the plain posterior b_h (ExactOracle `belief`, PRIVILEGED_BAYES for privileged unit values). No GROUNDED_* bounded actor or ε face-value prior is used, and a test asserts this. Strata 2–3 labels are evidence-resolved *given* the declared "everyone is cooperative" rule and the declared content of quiet conversations; reports say so.
- **R8 Computed notes.**
  - The status follows the package's own definition, applied to the value distribution (grounded if max p ≥ 0.8, else uncertain).
  - Each computed note also carries one `unresolved` line, so that the certainty of the access status is not hidden behind "uncertain": "Under the public model, the probability that this belief is correct now is X" for K units, or "...that this view of <k>'s belief is correct now is X" for depth-2 units. For R units, the value distribution already is the reliability posterior, so no line is added.
  - reference: X = the posterior P(default holds | h).
  - privileged: the true belief value (p = 1) and the true correctness (1.00 or 0.00), in the same format. It is a privileged diagnostic and can reveal the physical target; the report classifies privileged benefit by mechanism (target leakage / self-location / perspective content).
  - Inferred notes are the model's own output, and their format differs from computed notes. This is a recorded presentation limitation.
- **R9 Retention.** Notes are instantiated at t0 and shown at every policy step with their t0 timestamp (graph retained; `fact_only` refutation; no refresh). This is identical for every note condition.
- **R10 Reading rule** (per condition, reference and inferred read separately):
  - **Stratum classification.** For each stratum, take the per-state paired difference d_s (mean over draws of condition minus none; 4 states).
    - *positive*: mean ≥ +0.05 and at least 3 of 4 d_s > 0;
    - *negative*: mean ≤ −0.05 and at least 3 of 4 d_s < 0;
    - *null*: |mean| < 0.05 and every |d_s| ≤ 0.10;
    - otherwise *inconclusive*.
  - **Overall reading.** *Headroom present* if at least 2 of strata 2–4 are positive and stratum 1 (the zero-value control, for the same condition) is not negative. *No measurable headroom* if no stratum among 2–4 is positive and at least 2 are null or negative. Otherwise *inconclusive*.
  - Per-state raw draws come first in the report. The bootstrap is descriptive only. Stratum-4 Bayes gaps (0.02–0.07) are below what this sample can detect.
- **R11 Failures.**
  - Notes: up to 3 attempts (existing protocol). If all fail, the frozen payload is null and the inferred condition shows no note (recorded).
  - Policy: up to 3 attempts per step. Invalid, unparseable, illegal, truncated (finish_reason length) and timed-out outputs are failed attempts. After 3, the fallback is wait() (flagged). Episodes are scored as played. No resampling beyond the protocol; every attempt is logged.
- **R12 B2 API batch.**
  - Policy max_output_tokens 2000, reasoning effort low; notes max_output_tokens 6000. Up to 3 attempts per call, as in R11.
  - The ledger reserves each call's worst case before dispatch, and the stage hard cap = reconciled spent + 0.80 USD. This keeps a reserve of at least 0.33 USD below the original USD 5 total.
  - Dispatch: notes first (frozen), then policy cells in counterbalanced passes. If the cap halts the batch, completed passes and cells are reported as partial.
- **R13** No LLM call touches dev-v3 before the freeze commit. Engineering checks use symbolic code or dev-v2.
- **R14 Provenance and the chute.**
  - Provenance corrected: the three-office layout and stratum 3's missing chute were chosen knowing that dev-v2 asking and search were cheap, in order to create task-level headroom. They are pre-declared and not tuned on dev-v3.
  - Round A also reports with-chute counterfactual Q-values for 3a–3c. In 3c a chute makes drop(o_a) = give(F), so K(F→R) has no task-level relevance there.
  - Chute availability confounds cross-stratum comparisons.
- **R15 Shortcut and independence checks.** Agent-visible text (rendered unit and policy prompts, at rev 6) must not contain instance, group or construction IDs, stratum names, construction labels, PURPOSE text or focal-unit lists. The note conditions' own unit header is the only exception. The hidden RNG stream depends only on the construction, not on the variant. The declared independences hold in the prior (product test).
- **Recorded, from the optional list:**
  - The Round B selection resolves to **1c, 2a, 3c, 4b** (distractors none / obvious / obvious / obvious). There is no plausible distractor and no depth-pair group. It stays as declared.
  - In 4a the remark is changed to "earlier" (the time was an irrelevant cue).
  - The scoring-v3.1 source hash goes into the freeze.
  - "Adds no new content" = the rendered MIND NOTES section is byte-identical to that of another condition for the same state.
  - Fixed design proportions: 25% per stratum, one distractor level per construction (so level is confounded with construction).
  - Latency is descriptive only.
  - The allocation is designer-chosen with privileged relevance knowledge. The note header itself is a cue.

## Entry 1b — Round A results gate (2026-10-28; before the freeze and before any LLM call on dev-v3)
Gate reports:
- `reviews/roundA-results-opus.md`: PASS WITH REQUIRED CHANGES RC1–RC4.
- `reviews/roundA-results-sonnet.md`: CONSISTENT. An independent expectimax over all 48 instances matches to within 5e-11. The hand derivations, stakes flips, pairs and Round B selection (1c, 2a, 3c, 4b) all match.

Applied before the freeze:
- **RC1 Agent-visible text now matches the simulator.**
  - (a) Quiet notices read "X talks quietly to Y; only Y can hear it…". "Others present" excludes both parties, and r6 rule 1 names the addressee.
  - (b) The public-model header says it is given to the robot identically in every condition, and that people in the scene form beliefs only as rules 1–5 describe. Characters do not reason from the public model, consistent with rule 5's bystander clause and the 3b label.
  - (c) r6 rule 2 adds that seeing someone in, arriving at or leaving the lobby changes nobody's belief about which office that person is in. This was already the simulator semantics: K(N) in 2a stays at the announced office. Reference values are unchanged.
- **RC2 Tests.**
  - The rule-1/5 quiet test now checks addressee adoption, both nested beliefs, and unchanged bystander beliefs and nested beliefs.
  - The rule-3 test now covers t0 statements and every first-question answer in every prior world, each on a fresh world.
  - The rule-5 test now traces every nested-belief change to its cause, using recorded presence.
  - New tests cover lobby sightings and quiet-notice rendering.
  - An earlier rewrite of these tests had never reached the file because of a shell-quoting failure; the gate caught this.
- **RC3 Documentation.**
  - (a) *Deviation from R1a:* the stratum-3 superset mixes 3 patterns (3a, 3b, 3c) without an A↔F swap. The card names the courier publicly, so swapping A and F would change the public action set (who accepts give), not a hidden variable. The stratum-2 superset keeps the 6 patterns (H↔N swap), because both are couriers.
  - (b) *Card-only column:* "fixes" means that the Bayes optimal first-action set computed with the prologue notices removed equals the full optimal set. Under a construction-specific prior this happens for 1b, 2a, 2c, 3a and 3c, because that prior encodes the role pattern; the card text does not disclose it. Under the card-consistent superset prior no group is fixed, so the visible prologue resolves each case. Caveat: set equality does not catch containment (for 2b and 3b the card-only set can contain the full set without being equal).
  - (c) *R7 statement:* the strata 1–3 labels and the 3a/3b Π≤1 certification are evidence-resolved **given the declared rules**: everyone is cooperative, the content of quiet conversations, rule 5's bystander clause and rule 2's lobby-sighting clause. They are stipulations of the public model, not entailments of the history without them.
- **RC4 Provenance.** Everything is committed, the qualification is regenerated at a clean commit, `dev-v3-freeze.json` is written, `run_dev_v3_notes.py verify` passes, and the freeze is committed before any LLM call.
- **Sonnet presentation notes** are applied to the qualification report:
  - the move family is labeled "move" (it includes walking back to the lobby);
  - the 2a-vs-2b loss reads "n/a: action illegal" instead of nan;
  - the privileged ΔJ column is labeled ex-ante.
