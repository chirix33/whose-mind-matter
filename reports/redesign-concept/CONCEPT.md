# Redesign concept: selective, relation-preserving perspective memory in a sequential office day

Date: 2026-10-29. This responds to `METHOD_REVIEW_RESEARCH_DECISIONS.md` §4 (recorded as D-018).

**Status:**
- **A concept for research review.** It authorizes no experiment and does not claim that a positive outcome is expected.
- No code, generator, prompt or model was changed or run for it.
- The only new evidence is a hand-derived table (§2.3), labeled as such, built on the existing symbolic audit (`reports/method-review/audit.md`).

## 0. Verdict first

I found one concept that meets both of the review's requirements without hiding history from the baselines or padding the task. It changes three things, so it is a versioned redesign (§4.2), not a repair:
- **what a unit's content is:** referents with provenance instead of value marginals;
- **what the agent computes from units:** relations between perspectives;
- **where the computation constraint comes from:** a sequential multi-task day, where perspective content is reused across decisions and the raw log grows for substantive reasons.

**It is still a risky concept.** The first empirical gate, whether the local policy can use exact relation-preserving content at all (§5, G1), sits exactly where the last three blocks failed.

My recommendation:
- If the review accepts the concept, the next authorization should be **only G0**: CPU-only generator and qualification. G0 can kill the concept before any LLM call.
- If the review judges the concept unconvincing, the right action is the review's fallback: **freeze and document the negative development findings.** §7 says what that would contain.

## 1. Why the old design could not answer the question (one paragraph)

In dev-v3, the decision context already held a short, complete history (≈ 600–900 characters of ledger). Notes were computed by separate full-history calls, each costing ≈ 4,027 tokens per requested unit (77% of a no-note episode). They then served only about 3 decisions of a single task.
- For an ideal actor, they added no information.
- For the local actor, they added tokens and a partial view.
- Their content was a set of **marginals**, while the decisions depended on **relations** between perspectives: does the courier's forwarding target equal the recipient's location? (`audit.md` Part 1).

The redesign must therefore change two things:
- **the content type**, so relations can be exposed;
- **the economics**, so that perspective computation is reused and competes with real processing costs rather than with a 200-token ledger.

## 2. Requirement 1: decision-relevant relations

### 2.1 Referential (event-anchored) unit content

Every robot-visible event e in the log has:
- an ID, a time, a kind, an actor, and the people present;
- a **value slot** v(e) for the fact it concerns. The slot is observed (heard) or hidden (a quiet conversation the robot saw but did not hear).

The public model declares constraints between slots. In the current constructions, for example:
- "a change is to a different office": v(change) ≠ v(announce);
- "a quiet conversation started by A conveys the current meeting office": v(A→F) = v(A→R).

A unit u = (path, variable) keeps its definition (D-004; for (j, k), j's belief about k's state). **Its content becomes a distribution over referents**:
- a slot v(e) (the belief came from event e and has not been revised since);
- an observed constant;
- `unknown` (no belief).

Each referent carries its provenance event IDs and an as-of time.

The current value distribution stays **derivable** by projecting each referent onto values through the robot's posterior over slots. Nothing in D-004's ontology changes. The content gains *where the belief came from*, which is exactly what a person's mental state is about: "she believes the meeting is wherever the organizer told her".

### 2.2 Relations the agent computes from its own units

For units u and v about the same fact:
- the agent's **relation layer** computes R(u, v) ∈ {same, different, undetermined} with probabilities;
- it does so from the two referent distributions plus the public constraints, using small symbolic constraint propagation (union-find over slot equalities, with disequalities).

This is a **declared method component**:
- **inputs:** only the agent's own unit contents and the public model;
- **cost:** CPU, measured and reported;
- **ablated** against marginal-only content and referents-without-relations.

**It is not an evaluator quantity.**
- When the agent's inferred units are wrong, its relations are wrong.
- It never computes action values or success probabilities. An "agent-computed action consequence" would be a further, separately ablated component. It is not part of the base concept, given the D-016 harm reading.

### 2.3 Hand-derived check on the existing constructions (not executed)

These are the same rows as `audit.md` Part 1. "Marginals" are the Fréchet bounds on P(give succeeds) computed from the two value marginals. "Referents" is the relation the layer would derive under the declared dev-v3 public model.

| row | courier's forwarding content (referent) | recipient's belief = location (referent) | public constraint used | marginals | referents |
|---|---|---|---|---|---|
| 2a informed H | v(R→H quiet) | v(R→H quiet) | identity | [0, 1] | same → succeeds |
| 2a / 2b stale N | v(announce), observed | v(R→H quiet) | the move is to a *different* office | [0, 0] | different |
| 2c later N | v(R→N quiet) | v(R→N quiet) | identity | [0, 1] | same |
| 2c earlier H | v(R→H quiet) | v(R→N quiet) | each move is to an office other than the current one | [0, 0.5] | different |
| 3a | v(F→R quiet) = v(A→F quiet) | v(F→R quiet) | identity (F relays what A told F) | [0, 1] | same |
| 3b | v(announce) (F did not perceive A→R) | v(A→R quiet) = v(A→F quiet) | a change is to a different office | [0, 0] | different |
| 3c | v(announce) (R's public statement) | v(announce) | identity | [1, 1] | same |

Referents determine the handoff outcome in all 9 rows. Marginals determine it in 4 (the [0,0] and [1,1] rows). The three undetermined rows (2a-H, 2c-N, 3a) are the positive cases, where giving to the courier is correct.

**This is a hand derivation and has not been executed.** G0 (§5) would implement referents in the oracle and verify it over every world, including the bounded-context sufficiency computation of `audit.md` Part 3.

### 2.4 Why this is not a success field

The relation is between two perspectives (where F's model of R points vs where R's belief points). It is not between an action and an outcome.
- It is computed from inferable content, and it stays meaningful when no handoff exists. For example, it predicts what R will do or say when asked, and whether informing R would change anything.
- In the current constructions it is numerically aligned with handoff success (`audit.md` §2 finding 5). The new generator must therefore include **relation queries that are not action-equivalent**:
  - relations whose truth does not decide the current action (no courier present, or the ask is cheaper);
  - actions whose success depends on a relation the agent did *not* compute.

  These are G0 qualification criteria (§5), not optional.

## 3. Requirement 2: a meaningful computation constraint

### 3.1 The task regime: a sequential office day (Tier 1, scripted)

One episode is a **day**. A shared cast of N people (planning range 6–10) carries out routines over a building:
- meetings are announced and moved;
- people relay changes through quiet conversations;
- people leave and return;
- some report incentives (with disclosed obstruction rates, as in 4b/4c).

**K delivery or information tasks** arrive over the day (planning range 1–10). Each is drawn from the existing validated construction families: physical, first-order, depth-2 relay, and probabilistic.

The robot's own asks, moves and handoffs are part of the log. Events from earlier tasks are **substantive, not padding**:
- the stale courier of an early task can be the only courier of a later one;
- a person who witnessed a move hours ago can be the right informant later;
- an announcement can become stale through a relay the robot saw but did not hear.

Log length grows with K and N because the day contains more of the same causal process. Length is never a free knob.

Scaling is reported along K, and the K grid is pre-declared. A method that wins only at the largest K is reported as winning only there.

### 3.2 Where the costs come from (planning model; to be measured, not assumed)

For decision t, let L_t be the log length so far, D the number of decisions in the day, and U the candidate units.

**Direct full-history (A1/A2).**
- Each decision processes L_t plus its reasoning.
- With vLLM prefix caching, much of the re-read prefill is cached, so its *token* cost can overstate its *time* cost. Caching stays on for every method and is reported.
- Its weakness, if any, is expected in **quality**: functional ToM over a long, interleaved, multi-agent log.
- Literature support for that is suggestive but not specific to our setting:
  - models answer literal belief probes far better than they act on beliefs: EnactToM reports 45% on probes vs 0% task completion on its hard split;
  - adversarial or structurally complex stories break strong models (ExploreToM);
  - information asymmetry in multi-party conversation defeats them (FANToM);
  - long-context use is position-sensitive ("Lost in the Middle").

  None of these measures our task. G2 measures it.

**Dense perspective memory.**
- Maintains every candidate unit. U grows roughly with F × N² for F query facts at depth ≤ 2 (N = 8, F = 6 gives ≈ 380 Knowledge units).
- Each unit is refreshed whenever an event touches a person on its path, and is rendered into every decision. The rendering cost and the interference from irrelevant units are the C3 mechanism.
- Even if refresh were free (symbolic tracking), rendering and interference remain. This is why cheap computation does not make dense dominant automatically (review §4).

**Selective perspective memory (the method).**
- Maintains and renders only units with positive estimated net value for upcoming decisions. Each is refreshed incrementally from the events its path perceived since its as-of time (perspective-filtered, as in SimToM and PercepToM). Cost grows with relevant events, not with L_t.
- **Units are reused across decisions within the day.** That is genuine deployment reuse, unlike the experimental reuse across draws that D-016 §6 excluded.

**Generic memory.**
- A rolling narrator summary plus a recent window, or retrieval of past events, at matched cost.
- Hypothesis: narrator summaries record world state and drop who perceived what, which is exactly the decision-relevant relation (MWM's perspective-leakage concern).

### 3.3 The causal explanation, as testable links

Selective relation-preserving perspective memory can beat dense processing and generic extra reasoning at matched compute **only if all four links hold**. Each link has its own test (§5).

| link | claim | how it fails |
|---|---|---|
| L1 headroom | as K grows at fixed per-decision structure, the direct policy's return falls short of the reference by more than δ, *including* with its reasoning knob raised | direct stays near the reference: no computation constraint, so stop C1 here |
| L2 usability | with **exact** referential units and relations, the same backbone takes the correct action in the relation-dependent decisions it currently fails (the 3a/3b types) | it still acts on partial views: the representation is unusable by this actor, so stop |
| L3 sparsity and predictability | at most decisions, a small unit set suffices for the bounded-context reference (§4.2), and visible task structure predicts which set (who the recipient, courier and informants of the current task are) | sufficient sets are large or unpredictable: allocation degenerates to dense or fails, so stop |
| L4 inferability per cost | perspective-filtered incremental instantiation reaches usable fidelity at a cost below re-processing the log or maintaining dense units | inferred units are too unfaithful or too costly: realized value is below direct, so stop |

**Return at matched compute is the outcome.** Selective must beat:
- direct and direct-plus-reasoning (A1, A2);
- generic memory;
- dense memory with the same representation;
- selective with marginal-only content.

If selective beats direct but not generic memory, the effect is not perspective-specific and is not claimed as allocation.

## 4. Definitions: what stays and what changes

### 4.1 Retained from the outline and decisions D-001…D-018
- The research question: whose mind, which variable, which directed path, by decision value, under compute constraints.
- Units (path, variable). K and R. Depth ≤ 2, with depth-0 physical reasoning always on.
- Candidates are derived only from visible evidence, with false-exclusion audits.
- VoMI(u | S) = E[return | S ∪ {u}] − E[return | S] − λ·c(u), as the realized value for the stated actor. Records stay distinct: symbolic reference, oracle-content LLM bound, realized LLM.
- Rewards (+1, −0.05 per step, −0.5 × stakes on an irreversible error). Legitimate ask, search and move actions.
- Informative STOP cases:
  - the recent window already settles the decision;
  - physical observation suffices;
  - asking is cheaper than computing, which is a real trade-off once λ > 0.
- Controls for redundant and complementary units:
  - natural complements: K(F→R) with K(R); R(j) with K(j);
  - natural substitutes: K(H) when R told H; asking R directly.
- The full baseline inventory, with E1 (memory/retrieval) and E2 (generic adaptive reasoning) promoted to **main** controls.
- All-call accounting (D-018 §3).

### 4.2 Changed (versioned, requiring acceptance before any build)

| id | change | why |
|---|---|---|
| R1 | unit content becomes a referent distribution with provenance; value marginals are derived by projection | exposes relations (§2) |
| R2 | an agent-side relation layer computed from the agent's own units, declared, costed and ablated | lets a bounded policy use relations without evaluator quantities |
| R3 | a day-level Tier 1 generator (call it dev-v4) composed of validated construction families with a shared cast, fresh seeds and a pre-declared K/N grid | a substantive sequential task in which perspective content is reused and the log grows for causal reasons |
| R4 | **the method's** decision context is the task card, public model, recent window W, physical summary, rendered units and relations. **Every baseline keeps full-history access**, and generic-memory baselines get their own compressed memories. Information access is equal (the whole log is available to every method's computations); processing differs | the review's separation of information access from processing resources |
| R5 | the **symbolic reference actor for labels** becomes the *bounded-context Bayes actor*: Bayes over the public model, the physical state, the recent window and the units' referential contents, as in `audit.md` Part 3 with referents. Unit values are then genuinely non-zero, and the actor's information matches the method's decision context rather than an arbitrary default prior | replaces the face-value record, which D-018 rejected as a label source here |
| R6 | the compute frontier is reported both as **GPU-seconds at a fixed serving configuration** (prefix caching on for all methods) and as **actual-tokenizer token counts** split into prompt (cached/uncached), completion and reasoning. A claim requires both frontiers to agree in direction. The matching tolerance is pre-declared per comparison | D-018 §3: tokens are not time; caching is visible |

R4 is the point most open to misreading. The method is **not** given less information than the baseline in order to win. It *chooses* to process less, and it competes against the best full-history configuration of the same backbone, including its reasoning knob and caching.

## 5. Gated plan if the concept is accepted (no gate is authorized by this document)

| gate | what | data / cost | abandon if |
|---|---|---|---|
| **G0** CPU only | Build dev-v4 and its public model. Implement referents and the relation layer in the oracle. Qualify on fresh seeds | engineering ≈ 1 week; CPU minutes to hours. **Risk:** the exact reference must stay tractable, so hidden slots must factor by query fact, letting each decision enumerate only its fact's slots. If exactness fails, the concept needs a labeled approximation, which goes back to review | any one of: (a) the referents-determine-relations check fails in > 5% of relation-dependent decisions; (b) median minimal sufficient set ≥ 50% of candidates, so allocation is not sparse; (c) a pre-declared visible-feature rule recovers a sufficient set in < 80% of decisions; (d) < 20% of decisions are relation-dependent, or relation queries are always action-equivalent; (e) the exact or factorized reference is intractable at the K grid's top |
| **G1** local, small | L2 usability. Direct vs exact referential units + relations vs exact marginal units, at **short K** on the current backbone, single decisions plus short episodes | ≈ 500–1,000 decisions; under 30 min local; USD 0 | exact referential content does not raise relation-dependent correct actions by ≥ 0.15 over both direct and marginal-only, or it harms the positive controls. **No renderer iteration**: one pre-declared rendering |
| **G2** local | L1 headroom and the value ceiling. The K grid × {A1, A2, generic memory, dense-exact, selective-exact (reference allocation), selective-exact-marginal}, all fully costed | rough planning: 3 K levels × 6 methods × ~48 days × 2 draws ≈ 1,700 days; up to ~20 decisions/day at long K with 4k–16k-token contexts. Several hours to about a day of local GPU (*estimate*, to be refined with the real tokenizer and measured throughput) | at the top pre-declared K, A2 is within δ of selective-exact at matched compute; **or** generic memory is; **or** dense-exact is. Then even free exact selective content has no allocation-specific advantage, so stop |
| **G3** local | L4 and realized value. Inferred, perspective-filtered, incremental units, with all attempts charged per request | same scale as G2 for the methods that survive | realized selective falls below A2 at matched compute on both frontiers, so stop |
| **G4** | controller: a visible-feature rule first, then learned (outline §4.2–4.3), with RQ2's objective comparisons | as in the original roadmap | as in the original roadmap |

**Rules that prevent endless revision:**
- Each gate's thresholds are frozen before its data exist.
- A failed gate stops the line. It does not trigger a renderer, prompt, backbone or generator revision.
- **Backbone:** the local gpt-oss-20b throughout.
  - A second family (local Qwen3.6-27B or Gemma-4-31B, present but untested and unapproved) would need its own approval, for a pre-declared generality question, never after a failure.
  - The remaining USD 1.076 cannot fund a meaningful long-context API comparison. At an estimated ≈ USD 0.5 per long-K day for a 20-decision day, it would cover about 2 days. It stays unspent.

## 6. Small comparison matrix (G2/G3 core)

| method | history access | processing | units | relations | role |
|---|---|---|---|---|---|
| A1 direct | full log | the whole log per decision | — | — | main baseline |
| A2 direct + reasoning | full log | as A1, one pre-declared higher reasoning setting | — | — | generic compute |
| E1 generic memory | full log via summary or retrieval | rolling narrator summary + window W, or retrieval | — | — | generic memory |
| D dense | full log for refresh | window W + all candidate units | all | yes | dense (Mentis/SymbolicToM-style; labeled as an adaptation) |
| S selective | full log for refresh | window W + selected units | value-selected | yes | **method** |
| S−rel | as S | as S | value-selected | **marginals only** | relation ablation |
| (secondary) random-k, perspective-filtered direct (SimToM-style at decision time), S with agent-computed action consequence | | | | | controls and ablations |

**Outcomes:**
- return (primary), with success, errors and steps;
- both compute frontiers;
- unit fidelity;
- STOP rate and the number of informative STOPs;
- hallucination and leakage counts (RQ3);
- results per K and per construction family.

## 7. If the concept is judged unconvincing: freeze contents

A frozen negative-findings record would contain, with all scripts and hashes already in the repository:
- the D-013…D-016 results, which never showed note value on short-history tasks;
- the D-017 symbolic audit, with its D-018 corrections;
- the cost accounting;
- a short discussion of what the evidence does and does not say about selective theory of mind:
  - marginal notes cannot carry inter-perspective relations;
  - a full-history policy makes separately computed notes redundant in information but not in processing;
  - the integration failure of a mid-size local model.

That record is itself a contribution to the design of decision-oriented ToM evaluation, but it is not the allocation paper.

## 8. My assessment of the concept's main risks, in order
1. **L2 (usability) is where three blocks failed.** Referential content removes one specific failure, missing relations, but not the general one of acting on a partial view. G1 is cheap and decisive.
2. **L1 may not hold for the direct baseline,** especially with caching. A mid-size model on a 10–16k-token templated log may still do well. If it does, there is no constraint to allocate under.
3. **Tier 1 text is templated, so perception parsing is easy.** The LLM's hard step is perception-to-belief (PercepToM's finding), and referents make that step pointer-following. That is the concept's bet. It also means Tier 1 results say little about natural-language logs until Tier 2.
4. **Novelty versus SymbolicToM.** SymbolicToM tracks dense per-character belief graphs for question answering. The distinguishing contributions here would be decision-value selection, relation exposure for acting, and matched-compute evaluation against generic memory and reasoning. If dense tracking suffices (G2's dense-exact arm), the allocation contribution disappears.
5. **Scope.** The day-level task makes the robot's horizon long. The outline's exclusion of "long-horizon goal modeling" concerns modeling *other people's* goals, which stays excluded. The review should confirm this reading.

## 9. Sources consulted (2026-10-29)
- SymbolicToM: Sclar et al., ACL 2023, dense multi-character belief graphs. https://aclanthology.org/2023.acl-long.780
- SimToM: Wilf et al., perspective filtering before answering, ACL 2024. https://arxiv.org/abs/2311.10227
- PercepToM: Jung et al., EMNLP 2024. Models are good at perception inference and weak at perception-to-belief. https://arxiv.org/abs/2407.06004
- FANToM: Kim et al., EMNLP 2023, information asymmetry in multi-party conversation. https://arxiv.org/abs/2310.15421
- Hi-ToM: He et al., 2023, higher-order beliefs. https://arxiv.org/abs/2310.16755
- ExploreToM: Sclar et al., ICLR 2025, adversarial story structures. https://arxiv.org/abs/2412.12175
- EnactToM: 2026, functional vs literal ToM in embodied multi-agent tasks (45% literal probes vs 0% task completion on the hard split, per the abstract page). https://arxiv.org/abs/2605.09826
- Bolander, "Seeing is Believing" (DEL formalization of false-belief tasks), plus complexity results for DEL planning. https://www.imm.dtu.dk/~tobo/bolander2018seeing.pdf
- De Sabbata et al., Rational Metareasoning for LLMs (value of computation as a reward). https://arxiv.org/abs/2410.05563
- Mental World Modeling / MENTIS: Fei & Zhao, 2026. https://arxiv.org/abs/2607.27201
- iAgents / InformativeBench: NeurIPS 2024, information asymmetry among agents. https://proceedings.neurips.cc/paper_files/paper/2024/hash/0534abc9e6db91683d82186ef0d68202-Abstract.html
- Standard references, not re-checked this session:
  - Liu et al., "Lost in the Middle", TACL 2024 (arXiv 2307.03172);
  - Russell & Wefald, value of computation (1991);
  - Gmytrasiewicz & Doshi, I-POMDPs (JAIR 2005).

Secondary-source details (for example, aggregator summaries of FANToM sub-results) were not relied on.
