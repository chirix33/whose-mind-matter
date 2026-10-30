# Method review after the integration diagnostic (D-017)

Date: 2026-10-29. This responds to `INTEGRATION_BLOCK_RESEARCH_DECISIONS.md` (recorded as D-017). It is a **proposal for research review**, and nothing in it has been launched.

> **Reviewed under D-018** (`METHOD_REVIEW_RESEARCH_DECISIONS.md`).
> - The stop recommendation is accepted.
> - The closure test (§3–§5) is **not authorized** and will not be run.
> - V1–V4 are not launched. The follow-up is a redesign concept: `reports/redesign-concept/CONCEPT.md`.
>
> Corrections applied in place (2026-10-29):
> - (a) The Bayes proposition is now worded about the *computed posterior*. A person's realized mental state is often not determined by h.
> - (b) "Free correct notes have no practical headroom" became "the tested cell-level selection procedure has not demonstrated a practical gain". It is not a ceiling, and some recorded conditions contain two focal notes.
> - (c) The cost per requested unit charges all attempts: 4,027 tokens, which is 77% of a no-note episode, not 63%.
> - (d) The bounded-context cost figures are conditional planning estimates, not bounds.
> - (e) D_memory is no longer defined as an episode-minus-probe residual.
>
> Struck text is kept only where needed for traceability.

Scope of the review work:
- No LLM calls, no paid calls, no training, no prompt or generator change, and no new seeds were used.
- The new evidence comes from two CPU-only scripts over existing material:
  - `scripts/method_review_audit.py`: symbolic, over the already-inspected dev-v3 base draw 20261029. Output `audit.md`/`audit.json`, 12 s.
  - `scripts/method_review_selector.py`: over the existing repair-block episodes. Output `selector-headroom.md`/`.json`.
- All numbers are development data.

## 0. Recommendation

1. **The current implementation leaves no plausible matched-compute value for allocation.** It has three parts: OfficeMinds dev-v3, a full-history LLM decision policy, and one LLM instantiation call per unit. I recommend **stopping its optimization**. This is a finding about this approach, not about theory of mind. Three results support it (§1.6):
   - Reference notes are deterministic functions of h and the public model. They add no information for an ideal actor that already conditions on both. This is a basic information-boundary observation, checked numerically.
   - For the local actor, the tested cell-level selection procedure has not demonstrated a practical gain from free correct notes: +0.044 in-sample (optimistic), −0.001 cross-fitted, with an interval that does not exclude gains above +0.05.
   - Charging all attempts, one requested inferred unit costs about 4,027 tokens, which is 77% of a no-note episode's 5,230 decision tokens.
2. **One hypothesis is still open: the pair K(F→R)+K(R) in 3b.** The symbolic audit shows it is the one note pair whose marginals fully determine the 3b handoff outcome.
   - If the review wants this hypothesis closed rather than left open, I propose **one bounded closure test** (§3–§5). It is local only, USD 0, about 1.5 h of GPU time, and 64 fresh seeds.
   - It has generic-computation controls and a pre-declared stop rule.
   - **The stop branch is the outcome I expect.** No renderer, backbone or generator revision follows a stop.
3. **Making the allocation question testable would need a versioned change** (§6, V1–V4), for example a regime where the decision context cannot hold the history. I am not proposing to start any of these. They are listed so that the stop decision is informed.

## 1. The bounded actor and the value being allocated (review item A)

### 1.1 The actor as implemented (pilot-v2.2, r7)

| component | definition |
|---|---|
| backbone | local gpt-oss-20b (vLLM 0.32.0, TRITON_ATTN), reasoning effort low, temperature 1.0, max 1,024 output tokens, structured JSON action, bounded retries with recorded fallback |
| decision context c_t | system prompt; task card **with the full declared public model**; the **full visible history ledger** (dev-v3 prologue notices included: who announced, who spoke quietly to whom, who left); the deterministic physical summary; the view of the graph G_t; the legal actions |
| history h_t | every robot-visible observation and the robot's own past actions. In dev-v3 this already determines every unit's typed content exactly (§1.4) |
| retained memory m_t | G_t: units with typed content distributions, as-of step, and status (fresh/stale/…). There is no other memory: each decision call is stateless apart from c_t |
| unit output | one (path, variable): a distribution over content values plus the robot-confidence line (r7). No correctness line, no action advice (D-007) |
| actions | ask, move/search, drop (chute), give (to a courier), deliver, wait; reward +1 / −0.05 per step / −0.5×stakes on an irreversible error; horizon 8 (D-005) |

**Note on drift.** Outline §4.1 step 5 says the policy decides "from the physical state and G_t". D-001 made that the physical state, the *literal report ledger* and G_t. dev-v3 (D-014) then put the prologue's communication events into that ledger, so that unit content would be legitimately inferable from h.
- The consequence is that the decision context already contains everything a unit could say.
- This drift is logged as discrepancy 23. Whether the policy should keep the full history is a versioned choice (V1, §6).

### 1.2 Compute accounting and budget (fixed before any further run)

- **Primary compute unit:** total tokens processed per independent episode on the single backbone, C = Σ over all calls of (prompt + completion, reasoning included).
  - "All calls" means decisions, unit instantiations, retries and failed attempts, any controller, summary or scoring call, and any decision call needed to get a margin feature.
  - Cached prefixes are still counted, with caching reported separately.
  - Reasoning tokens are reported as returned and are never zero-filled.
  - Generated tokens, calls, and monotonic wall clock at stated concurrency are reported beside C.
- **Deployment cost is per independent episode.** Experimental note reuse across draws or conditions is not deployment reuse (D-016 §6).
- **Retained notes are re-charged.** A retained unit costs its render tokens on every decision call that shows it (measured at about +95 prompt tokens per call per note).
- **Budget grid**, anchored on measured repair-block costs:
  - B0 is the measured no-note mean, about **5,230 tokens/episode** (4,615 prompt + 616 completion, 3.1 decision calls).
  - The other grid points are 2·B0 and 3·B0.
  - A method's operating point is its measured mean C.
  - "Matched" means a compared method is run at a fixed, pre-declared setting of its compute knob, and its measured C falls within ±10% of the other method's, or the comparison is shown on the return–compute frontier.
  - Knobs are not tuned on test data.
- **Primary target unchanged:** expected return at matched compute (outline C1/RQ1). Lower compute at matched return is secondary, and the target is not switched after results.

### 1.3 Value definition

For the actual actor π (the backbone at the fixed decoding) and an allocation S held in G:
- J_π(S) = E[episode return], where the expectation is over the public scenario prior (seeds) and π's sampling.
- The marginal value of u is ΔJ_π(u | S) = J_π(S ∪ {u}) − J_π(S).
- Net value is ΔJ_π − λ·c(u), where c(u) is u's measured token cost (instantiation plus re-render) and λ is a stated price per token.
- This is the outline's realized-LLM VoMI with the actor named. It is a property of (π, decoding, context regime, renderer), not of the unit alone.
- **The action effect and the retained-memory effect are kept apart:**
  - D_action is the change in the first decision, measured in a single-decision probe at a fixed context;
  - the episode-level effect is measured separately.
  - *(Corrected under D-018.)* The episode-level effect minus the probe effect is **not** a memory value. Probe Q-values use a declared continuation, while episode returns include later policy changes. A D_action/D_memory split needs matched interventions under one common continuation definition, as in the symbolic decomposition of spec §4.4. Without that, first-action and episode effects are reported side by side, with no causal residual.

### 1.4 Proposition: no value to a Bayes actor that already reasons from h

*(Wording corrected under D-018.)* This concerns the **computed posterior distribution** over a unit's content, which is a deterministic function of h and the declared model. It does not concern the person's **realized** mental state: h often leaves that unresolved (for example, which office a person was quietly told). Revealing a realized value would be a different, privileged operation.

If a note's content is that computed posterior, then for a Bayes actor whose decision context contains h and the model:
- the posterior conditioned on (h, content) equals the posterior conditioned on h alone;
- so ΔJ(u | S) = 0 for every u and S, and every interaction I(u, v) = 0.

**Checked numerically:** 6 constructions × 2 stakes, every subset of {routing units, K(R)}, under an exact I-projection actor with ε = 1. Every J(S) equals V*(h), with max |J(S) − V*| = 0.000 (`audit.md` Part 2).

**Consequence.** Any value of explicit mental computation in this environment must be a **bounded-actor** effect. That means either better return for a non-ideal policy at the same compute, or equal return at lower compute.

For a bounded policy, deterministic processing of h *can* improve decisions. Its value has to be measured for that policy, with its cost; the proposition does not settle it. The repair block's ≈ 0.50 gap to Bayes is general headroom of this policy, and notes have not been shown to recover any of it.

### 1.5 The existing symbolic bounded actor does not supply labels here

The face-value grounded_typed actor (spec §4.2) gives:
- **exactly zero unit value in 5 of 6 constructions** at both stakes;
- non-zero values only in 2c. There, its no-note value is 0.20 at ×1 against V* 0.95. The face-value testimony default up-weights worlds where the recipient returned to the announced office, which the uniform public prior does not support.

That 2c value is a default-interaction artifact (D-009), not a decision-relevant signal. The hedged actor (ε = 0.25) is zero everywhere.

Following the review's caution, **no symbolic record in the current family should be used to manufacture allocation labels for this environment.** Each one either equals Bayes or encodes a prior the LLM baseline is not bound by.

### 1.6 Feasibility arithmetic for each candidate actor and budget

| actor / regime | quality headroom vs Bayes | what notes can add | cost of one unit | verdict |
|---|---|---|---|---|
| **FH-local** (current) | ≈ 0.50/episode (repair) | free correct focal notes (one or two per construction), always given: −0.024 [−0.074, +0.028]. Per-cell choice among the recorded conditions none / focal / K(R), knowing the construction: in-sample +0.044 (optimistic), **cross-fitted −0.001** (`selector-headroom.md`) | **4,027 tokens per requested unit**, all 883 attempts charged to the 720 requests (**77% of B0**); 3,284 per attempt. Plus ≈ 290 render tokens/episode | The tested cell-level selection has not demonstrated a practical gain. This is not a ceiling for state-level selection or untested subsets such as the 3b pair. The cost is a large practical disadvantage but not a proof of impossibility: a note could change call counts or reasoning length |
| **FH-API** (gpt-6.1-sol, low) | none observed on the 8 checked contexts (8/8 Bayes-optimal without notes) | no quality headroom to recover; efficiency would require notes to *replace* reasoning, but in FH they are additive tokens | a separate call over the same history | No allocation purpose demonstrated; keep the USD 1.076 unspent |
| **BC** (bounded context: decision prompt without the prologue ledger; mental information only via G) | exists by construction (`audit.md` Part 3: J_B(∅) < V* in 5/6) | units carry information, and the best set varies by state (§2) | removing the ledger saves only ≈ 150–230 prompt tokens per call (ledger 590–930 characters at t0, ≈ 4 characters/token, *estimate*), ≈ 650 per episode, against ≈ 3,280 per unit plus re-rendering | *Conditional planning estimate (D-018):* if call counts and reasoning stayed unchanged, BC with one unit would cost ≈ +56% over FH, and break-even would need a per-call ledger ≈ 5–6× longer. This is not a performance bound: a redesigned policy's behaviour was not measured, and character counts are not tokenizer counts |

**Selector caveats.** The in-sample selector is upward-biased (winner's curse). Its seed bootstrap interval [+0.036, +0.096] is also optimistic, because a bootstrap of a selection procedure re-uses duplicated seeds. The cross-fitted interval [−0.005, +0.069] has the same leakage, which inflates its upper end. Treat both upper bounds as generous, and the cross-fitted interval as unable to establish equivalence to zero gain.

A selector that knows the construction is not deployable. *(Corrected under D-018.)* It is also **not** an upper bound on a selector that chooses per visible state, or on subsets, pairs and refresh schedules that were not recorded. It is a restricted diagnostic only.

## 2. Relationship audit (review item B)

**What give(c) depends on.** give(c) succeeds iff c's forwarding destination equals the recipient's location. Under the declared model (checked in every world, `audit.md` Part 1):
- (i) the routing unit's typed content (K(c) for an own-belief courier, K(F→R) for F) **is** the robot's marginal over that destination;
- (ii) K(R)'s content equals R's location;
- (iii) every person holds a categorical belief in every world. **All uncertainty in a note is the robot's, never the person's.**

Success is therefore a property of the **joint** of the two unit contents, not of either marginal.

At t0 (dev-v3 base draw, ×1; Q* values for both stakes are in `audit.md`):

| construction | courier's belief | courier's view of R (routing content) | R's belief = location | robot's confidence in destination | P(give succeeds) | bounds from the two marginals alone | independence reading | exposed by notes? |
|---|---|---|---|---|---|---|---|---|
| 2a, informed H | current (m1) | — (own route) | m1, robot: 2 options | 0.50 | **1.00** | [0, 1] | 0.50 | no: equality must come from h ("R told H quietly") |
| 2a, stale N | announced a | — | m1 ≠ a | 1.00 | **0.00** | [0, 0] | 0.00 | yes, if K(R)/location is also shown |
| 2b, stale N | announced a | — | m1 ≠ a | 1.00 | **0.00** | [0, 0] | 0.00 | yes, with the location marginal |
| 2c, later N | m2 | — | m2 | 0.50 | **1.00** | [0, 1] | 0.38 | no |
| 2c, earlier H | m1 | — | m2 ≠ m1 | 0.50 | **0.00** | [0, 0.50] | 0.25 | no |
| 3a | b (told by A) | b (F told R) | b | 0.50 | **1.00** | [0, 1] | 0.50 | no: identical marginals to an "always opposite" case |
| 3b | b (told by A) | a (F unaware A told R) | b ≠ a | 1.00 | **0.00** | [0, 0] | 0.00 | **yes, with the pair K(F→R)+K(R)**; neither unit alone |
| 3c | b | a (nobody told R) | a | 1.00 | **1.00** | [1, 1] | 1.00 | yes, with the pair |

Findings:
1. **The robot's confidence in the destination tells nothing about handoff success, and here it is anti-aligned:**
   - confidence 1.00 goes with success 0 (2a-N, 2b, 3b) and with success 1 (3c);
   - confidence 0.50 goes with success 1 (2a-H, 2c-N, 3a) and with success 0 (2c-H).

   The r7 confidence line is correctly worded as the robot's confidence in its estimate, but the 3b reasoning traces read it as "the package will reach R". **Confidence about a person's state must not stand in for the decision relation.**
2. **The review's illustrative structure occurs in the existing constructions.** In 3a (and 2a-H, 2c), the routing and location marginals are both uniform over the same two offices. The handoff succeeds because they are always *equal*, a fact carried only by a communication edge in h (F told R; R told H). Standalone distributions cannot distinguish it from an always-opposite case.
3. **The pair is the only representation that exposes 3b's relation.** In 3b, K(F→R) is a point mass on the announced office, and K(R) excludes it, so the two marginals jointly determine failure (bounds [0, 0]). Neither alone does. This is why the pair hypothesis is coherent for 3b. It does **not** carry over to 3a, where even the pair leaves [0, 1].
4. **What still has to be computed from h:**
   - the coupling between units: who told whom after which update;
   - for own-belief couriers, the location marginal (unless K(R) is allocated).

   The current notes expose only marginals.
5. **The obvious "fix" is the oracle field the review warns against.** The typed record's second field, P(the unit's face-value default holds), equals P(give succeeds) in **every** row (`audit.md` check). Rendering it, or any "this belief is accurate" line, would hand the policy the handoff's outcome probability. That is action-relevant advice by another name (D-007), so it is not a representation fix.
6. **A bounded-context Bayes actor shows how far content-only marginals carry (`audit.md` Part 3).** The actor sees the stratum's public process and the physical observations but not the prologue; content-only notes are I-projected onto its prior.

   | construction | best set | result |
   |---|---|---|
   | 2b | {K(N)} | reaches V* |
   | 2a | {K(R), K(N)} | reaches V* |
   | 3c | the pair | reaches V* only with the pair (singletons 0.85 / 0.75; pair 0.95; **I = +0.05, a genuine complement**) |
   | 3a | none | **no subset helps**: 0.80 vs V* 0.95, the marginals-only failure of finding 2 |
   | 2c | all three units | best 0.825 vs V* 0.95; every singleton *lowers* value |
   | 3b | ∅ or the pair | correct K(F→R) alone lowers value (0.75 vs 0.80); the pair restores 0.80 = ∅, so **I = +0.05 with zero value over no notes**. The loss is a detour to the noted office, never a handoff (`audit.json` traces). A Bayes actor treats the unresolved relation as risk, while the LLM handed off; this is a descriptive contrast, not a mechanism |

   So positive interactions occur both with and without useful value. The review's warning that a positive I alone is insufficient applies directly.

## 3. Complementarity closure test (review item C), specified but not run

> **D-018:** not authorized. It is kept for the record. Its proxy cost charge is per attempt, and per D-018 that kind of figure belongs only in a labeled sensitivity analysis.

**Question.** For the FH-local actor, does the pair {K(F→R), K(R)} with *correct* content raise 3b return beyond:
- each single unit;
- no notes;
- a redundant or irrelevant note;
- an exact history digest of the same length;
- spending comparable extra tokens on the actor's own reasoning?

If it does not, explicit-note allocation is closed for this actor and environment.

**Fixed elements:**
- Constructions 3a, 3b, 3c (3a and 3c are positive controls where give(F) is correct).
- Package pilot-v2.2, renderer r7 content-only, stale label shown as frozen.
- Backbone and decoding as in §1.1.
- Notes are exact reference notes computed at t0, retained for the episode, and never refreshed.
- Episode-level return is primary (it captures D_memory). First-decision outcomes are secondary (D_action).

**Conditions per state:**

| id | allocation / computation | role |
|---|---|---|
| C0 | none | baseline |
| C1 | {K(F→R)} | single u |
| C2 | {K(R)} | single v |
| C3 | {K(F→R), K(R)} | pair |
| C4 | C3 + K(F) | redundant unit (K(F) duplicates K(R)'s location content in 3a/3b; in 3c it is misleading, reported separately) |
| C5 | one correct note on a zero-value unit (the distractor K(P)/K(D) where present; in 3a a length-matched note restating the robot's physical state) | irrelevant / length control |
| C6 | an exact **history digest** of C3's rendered length (±10%): a deterministic, unit-free restatement of the robot-visible prologue events, with no inference and no mental-state vocabulary | matched generic summary |
| C7 | no notes, reasoning effort **medium** (one fixed setting, not tuned) | matched generic reasoning ("think longer") |

**Estimands.** These are means over seeds of state means: 2 stakes × 2 draws per seed, construction-specific.
- Interaction: I(u,v) = J(C3) − J(C1) − J(C2) + J(C0).
- Pair value: J(C3) − J(C0).
- Specificity: J(C3) − J(C6) and J(C3) − J(C7).
- Noninferiority in 3a/3c: J(C3) − max(J(C0), J(C2)).

**Compute in this test:**
- Reference notes cost no LLM tokens, so C1–C5 measure the *value ceiling* of perfect instantiation.
- For matched-compute comparison, each unit is charged a declared **proxy** of 3,284 tokens (the measured repair-block mean per inferred-note attempt), plus measured render tokens. The pair proxy is ≈ 6,600 tokens/episode.
- C7's cost is measured.
- The comparison is reported on the return–compute plane, with the proxy labeled as a proxy.

**Analysis:**
- Seeds are the independent unit. Contrasts are paired within seed. Intervals are percentile bootstrap over seeds.
- Exact sign-flip p-values, with Holm correction across the three primary 3b contrasts: pair value, interaction, and pair − C7.
- Failed or invalid outputs are kept, with the declared fallback, and reported per condition.

## 4. Proceed / stop criteria (review item D), declared before any run

**Proceed** to a *proposal* (not an automatic run) for inferred-pair instantiation and a state-dependent allocation study in strata 2–3, at matched compute, only if all of the following hold in 3b:
1. **Pair value:** J(C3) − J(C0) ≥ **+0.30**, with the Holm-adjusted test rejecting 0.
   - +0.30 is about 30% of 3b's mean Bayes headroom: 0.565 at ×1 and 1.447 at ×4 in repair data.
   - Note the pooled implication: a 3b-only gain of 0.30 adds only ≈ 0.025 to the 12-construction estimand. Reaching the original δ = 0.05 pooled would need comparable gains in other constructions, so a pass justifies only the next proposal, not a C1 claim.
2. **Genuine complementarity:**
   - I(u,v) > 0, Holm-rejecting 0;
   - **and** J(C3) > max(J(C1), J(C2)) by at least 0.10.

   A positive I that comes only from harmful singletons (the symbolic 3b pattern) does not count.
3. **Specificity.** The pair beats both generic controls by ≥ 0.10: J(C3) − J(C6) and J(C3) − J(C7), with the C7 contrast Holm-rejecting 0.
4. **No hidden cost in the positive controls.** In 3a and 3c, J(C3) ≥ max(J(C0), J(C2)) − 0.05. If the pair hurts where give(F) is correct, it is not a deployable unit.

**Stop.** Any of the following closes explicit-note allocation for this implementation:
- criterion 1 fails;
- criterion 3 fails because C6 or C7 reaches within 0.10 of the pair, which would mean generic computation or re-presentation does as well;
- C7 alone closes ≥ 50% of 3b's gap to Bayes at a measured cost no higher than the pair proxy, which would make it a reasoning-budget problem rather than an allocation one.

After a stop, the deliverable is a short write-up of the negative finding:
- no further renderers, backbones, generators or seed sweeps;
- any continuation only through a separately reviewed, versioned redesign (§6).

**Inconclusive** (an interval spans both the threshold and 0) is treated as **stop**. The test is sized so that this outcome is unlikely when a true effect is ≥ 0.40.

**Other partial outcomes:**
- **Criterion 1 passes but criterion 2 fails:** report "joint content is needed" without any complementarity claim, and return to review. No allocation study follows from it.
- **Criterion 2 passes but criterion 1 fails:** stop. A positive interaction without useful value is not a reason to proceed.

## 5. Resource forecast for the closure test (only if approved)

| item | value |
|---|---|
| seeds | **64 fresh, preselected** dev-v3 seeds 20261300–20261363 (none used before; never to be reused as held-out once run) |
| states | 64 × 3 constructions × 2 stakes = 384 |
| episodes | 384 × 8 conditions × 2 draws = **6,144** |
| precision (planning, from repair 3b: seed-level SD of contrasts ≈ 0.71–0.80) | pair-value 95% half-width ≈ 0.18–0.20. With a true +0.40 effect, P(point ≥ 0.30 and CI excludes 0) ≈ 0.85. Assuming the four-term interaction contrast has about √2× that SD, I is detectable only if ≳ 0.28 (a stated limitation) |
| local time | ≈ 60–75 min at the measured ~100 episodes/min (concurrency 8), plus ≈ 15–25 min extra for C7's longer reasoning, plus ≈ 1 min server start: **≈ 1.5 h** |
| CPU | reference notes and history digests: seconds |
| API | **none.** The ledger stays at USD 3.924 of 5 (USD 1.076 preserved) |
| gates | the same two reviewer sub-agents: plan/freeze (Opus) and results (Opus validity + Sonnet recompute) |
| new code | a condition table and C6 digest renderer; a C7 decoding override; the analysis script. No change to the generator, oracle, package prompts or r7 |

## 6. What is retained from the original method, and what would be a versioned change

**Retained unchanged:**
- the research question: choosing whose mind, which variable and which path by decision value;
- units (path, variable) with K/R at depths 0–2, depth-0 physical reasoning always on, and candidates from visible evidence;
- VoMI as marginal return minus λ·cost, with the realized-LLM record as the object of interest;
- the rewards, the legitimate ask/search actions, return at matched compute as the primary target, and the full baseline inventory;
- the information boundaries;
- the closure test itself, which uses only existing components.

**Clarifications needing acceptance (no version change):**
- the actor in §1.1 is the object VoMI is defined for;
- the compute definition and budget grid in §1.2;
- the proposition in §1.4 and its consequence, that symbolic labels from a Bayes-over-h actor carry no allocation signal here;
- §1.5: the face-value grounded record is not a label source in dev-v3.

**Versioned changes (none proposed for execution now):**

| id | change | what it would test | risk |
|---|---|---|---|
| V1 | **bounded decision context**: the decision policy sees the card, the physical summary, its own action and answer log and G, but not the prologue ledger; instantiation calls see h (outline §4.1 step 5 read literally) | allocation as selecting which mental summaries to carry, where units have information value even for an ideal actor | in dev-v3 it is strictly more expensive than FH (§1.6). The direct full-history baseline must stay, so without V3 it cannot win at matched compute |
| V2 | **relational unit content**: e.g. a typed coupling between two perspectives, "does F's model of R match R's belief" | whether exposing relations (§2) lets a bounded policy use mental content | numerically equal to give's success probability here (§2 finding 5), so it risks becoming action advice. It needs a construction where the relation is not action-equivalent |
| V3 | **environment with long histories** (many events and people, multi-episode memory) so that raw history ≫ unit cost | the regime where selective mental computation can plausibly save compute | an environment redesign; changes the paper's emphasis toward memory/compression; needs a fresh qualification block |
| V4 | **non-LLM unit computation** (a symbolic perspective tracker over parsed events) | allocation where units are cheap | with near-zero cost, dense allocation dominates and the allocation question shrinks to avoiding harmful units (C3) |

## 7. What this review does not show
- It does not show that mental-state allocation cannot work in general, nor that C1 or C2 is refuted. The findings are specific to this environment, actor and representation.
- It does not show that the pair helps or does not help the LLM. That is untested.
- It contains no API, Tier 2, Menti-Bench or depth (C4) evidence.
- The bounded-context results (Part 3) are symbolic properties of one declared actor model (the stratum superset, content-only notes, I-projection). They are not predictions of LLM behaviour.
- The selector analysis reuses inspected repair-block data and has optimistic intervals (§1.6).

## 8. Evidence and provenance
- Ruling: `INTEGRATION_BLOCK_RESEARCH_DECISIONS.md` (sha256 `adee8bfe…670b70b`), recorded in `docs/decisions/2026-10-29-D017-method-review.md`.
- Symbolic audit: `python scripts/method_review_audit.py` → `reports/method-review/audit.{md,json}`. All five checks are true:
  - routing content = destination marginal;
  - K(R) = location;
  - people hold categorical beliefs;
  - typed P(default holds) = P(give succeeds);
  - Bayes-over-h J(S) = V*.
- Existing-episode headroom: `python scripts/method_review_selector.py` → `reports/method-review/selector-headroom.{md,json}` (data `reports/repair-block/evidence/episodes-stage2.csv`).
- Measured costs: `reports/repair-block/stage2-results.json` (`compute`). Prompt composition in characters: `audit.md` Part 4. Token conversions at ≈ 4 characters/token are estimates.
- Runs used Windows CPython 3.14 on the workstation. The project code is stdlib-only. No GPU, vLLM or API was used.
