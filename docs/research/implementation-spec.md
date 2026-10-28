# Implementation specification — scientific contract (v0.3, 2026-10-28)

**Status.**
- v0.3 applies the Stage 1 research review: five corrections plus the Q1–Q6 rulings, recorded as D-007…D-012 in `docs/decisions/`. D-001…D-006 come from the Stage 0 review.
- Nothing here supersedes the outline (`docs/research/methods-experiments-v2.md`) or `AGENTS.md`. Narrowings are logged in `docs/decisions/discrepancy-log.md`.
- Earlier values are preserved with their provenance:
  - Stage 0 values = *legacy privileged perfect-content reference* (§6.1);
  - Stage 1 grounded values are now the **scalar diagnostic** record (§4.3).
- **Numerical claims about the tiny cases (depths, gold sets, values) are not restated in prose here.** They are rendered from canonical records in `reports/tiny-cases.md`. This spec cites tests that assert specific values. (Stage 1 review correction 1: the v0.2 prose wrongly said `nested_reliability` has depth 2.)

**Executable reference.**
- `src/officeminds/`: world, scenarios, episodes.
- `src/vomi/units.py`: units, defaults, candidates.
- `src/vomi/oracle.py`: label records, actor, I-projection, decomposition, depth.
- `src/vomi/allocation.py`: reference values, gold sets, D4/STOP, metrics.
- `src/vomi/graph.py`: perspective graph, refresh, features.
- `src/vomi/unit_schema.py`: typed LLM unit output.
- `src/vomi/theory.py`: P2, audits.
- `tests/`.

---

## 1. Scope implemented so far
- Tier 1 only, depth ≤ 2, Knowledge and Reliability, including nested Reliability **R(j→k)**.
- Cases: 10 legacy tiny cases, 6 grounded cases, and the `reversal_m1`/`reversal_m4` pair from the conflicting-reports family.
- No LLM labels, no bulk generation, no training. The typed unit schema for the Stage 2 pilot exists, but no LLM has been run against it yet.

## 2. Information boundaries (AGENTS §5.1)
| Layer | Type | Who may read it |
|---|---|---|
| Public task structure | `WorldConfig` + scenario `brief`; the public scenario prior, fixed before hidden sampling (D-008) | robot, controller, prompts, actor model |
| Physical state and objective truth | `World` positions, holding flag, time, `World.truth(fact)` | simulator, evaluator |
| Private minds | `PersonMind`: beliefs, nested beliefs, assessments (R(j→k) content), intent, perceived events | simulator, evaluator |
| Robot-visible history | `VisibleHistory` (actions and observations, including the literal report ledger). Serialized only via `to_agent_dict()` | robot, controller, prompts |
| Robot perspective graph | `PerspectiveGraph`: unit outputs with timestamp and status; `policy_view()` is what the policy sees | robot |
| Controller features | `visible_features` (depth, recency, spoke-to-robot, conflicting reports, stated incentive, stakes, the actor's own decision margin, evidence count) | controller |
| Privileged annotations | `PrivilegedTrace`, label records, true contents | evaluator, label generation only |

Invariance tests:
- `test_invisible_world_pair_gives_identical_actor_inputs_and_outputs`
- `test_typed_outputs_are_identical_across_invisible_world_pair`

Two hidden worlds with an identical agent view yield identical candidates, features, unit outputs (scalar and typed) and actor actions.

## 3. Units, content, ontology (D-004)
- **K(j):** what j believes per public query fact (a value or `unknown`). It may be false.
- **K(j→k):** j's belief about k's belief.
- **R(j):** intent ∈ {cooperative, obstructive}.
- **R(j→k):** j's assessment of k's intent ∈ {cooperative, obstructive, unknown}.
- **Mistaken** = cooperative plus a false or outdated belief, a derived reporting slice. Scenarios declare the objective truth of every non-location query fact (`World.truth` raises otherwise).
- **Tier 1 scripted policies** (deterministic, identical for every method):

  | Event | Effect |
  |---|---|
  | `witness` | the people present learn the fact |
  | `tell` (sincere) | speaker and listeners hold the belief; nested beliefs are updated |
  | `claim` | listeners update nested(speaker) only; answers to `ask` are claims; obstructive people lie deterministically |
  | `assert` | a possibly insincere statement; a listener without her own belief adopts the value, or its opposite if she distrusts the speaker |
  | `assess` | listeners adopt an assessment |
  | `enter` | a person walks into a room |
  | `say` | visible, no belief effect |

- Intent is never encoded in wording, names or order.

## 4. Label records and evaluator contract

### 4.1 Evaluator
- `b_h` = the public scenario prior restricted to worlds that replay the visible history exactly.
- The evaluator enumerates these worlds to take expectations; actors never see them.
- **Enumerating hypotheses in a declared public model is not an observation leak.** Instance-specific support built from the actual state's secrets would be one (D-008).

### 4.2 The bounded actor
- **Hypothesis space:** the public generator support, conditioned on h by replay.
- **Face-value defaults**, one per factor: K(j) no false belief; R(j) cooperative; K(j→k) j's model of k's belief accurate; R(j→k) j's assessment accurate.
  - `unknown` content satisfies a Knowledge default (no false belief), tested in `test_unknown_counts_as_satisfying_a_knowledge_default`.
- **Actor prior** ∝ prior × ε^(number of violated defaults among UNMODELED factors):
  - ε = 10⁻⁶: **face value**, the primary convention;
  - ε = 0.25: **hedged**, a mandatory sensitivity condition (D-010).
- **Conflict rule:** fewest violations, then prior weight.
- Testimony is a physical observation in the literal ledger, available to every method.
- **What a mental computation is.** Instantiating unit u removes u's default and I-projects (IPF, tolerance 10⁻¹⁴) the actor prior onto u's output marginal:
  - **typed** (`grounded_typed`): a distribution over (content value, default holds) for u's factor, e.g. "rec believes office_a and is not outdated: 0.35". This is the exact typed symbolic reference, closest to the method's typed mental content (D-007).
  - **scalar** (`grounded_scalar`): `p_default_holds` = P(u's factor satisfies its default | h), with the complement `p_default_violated`. A confidence-only **diagnostic**, not the main method (correction 2).
  - Both are exact generator marginals given h. That makes them an **offline symbolic reference**: not a deployable algorithm, and not evidence that the computation is cheap. Whole-history context is allowed, but the output concerns only u's (path, variable); it never carries an action recommendation, other minds' full states, or a hidden-world query (D-007).
  - **Helpfulness is not leakage.** In `stakes_m4_q0.95`, the typed K(alice) output, Alice's belief inferred from Bob's visible claim under the declared model, is useful (gross delta_J +0.045, `test_typed_output_carries_content_and_can_legitimately_help`). That is legitimate inference, not a leak. The Stage 1 report's description of it as a "leak" is withdrawn.
- **Planning:** belief-space expectimax under the actor's own model. Only mental modeling is bounded.

### 4.3 Label records
| Record | Actor | Unit content given to the actor | Role |
|---|---|---|---|
| `privileged_bayes`: legacy privileged perfect-content reference | Bayes-optimal | true contents | Stage 0 values; reference only |
| `privileged_bounded`: privileged perfect-content, bounded actor | bounded | true contents (point mass) | diagnostic; can be negative; not a bound |
| `grounded_typed`: grounded typed bounded-policy reference | bounded | typed (content, default-holds) marginal | exact typed symbolic reference |
| `grounded_scalar`: grounded scalar diagnostic | bounded | `p_default_holds` | **diagnostic only** (Stage 1 "grounded" values) |
| realized LLM value | LLM | typed LLM unit outputs (`unit_schema.py`) | Stage 2 pilot (not yet run) |

**Do not freeze bulk supervision on any symbolic record until the pilot relates it to typed LLM units and realized decision value** (correction 2).

### 4.4 Fixed continuation, decomposition, names (D-002, D-012; correction 3)
- `Q_ref(w, m, a)` is the realized return after action a, followed by the same actor with state m: no new instantiations, retained content, exact observation updates.
- Components:
  - `D_action = E[Q_ref(m, a_y) − Q_ref(m, a_0)]`
  - `D_memory = E[Q_ref(m_y, a_y) − Q_ref(m, a_y)]`
  - **`delta_J` (gross marginal task value)** = J(S∪u) − J(S) = D_action + D_memory, with residual < 10⁻¹² (`test_decomposition_identity_everywhere`).
  - **`net VoMI`** = delta_J − λ·c(u). It is reported only with λ stated (`Decomposition.net_vomi(lam)`, `UnitReport.lam`). No table may call a gross value "VoMI".
- **Carryover effect** = positive delta_J with zero current-action flips.
- **Carryover share** (D_memory / delta_J over positive units) is reported per record. It can exceed 1 when positive units have negative current-action parts.
- The legacy `depth2_handoff` display required by the Stage 0 review is asserted in `test_depth2_handoff_retention_counterexample_decomposes_exactly`: 0.80 / 0.80 / 0.85, giving D_action 0 and D_memory 0.05.

### 4.5 Cost and validity
- c(u) = 1 call (placeholder). A refresh is a counted call.
- Offline exact-reference cost is reported separately from deployment cost (D-007).
- A label is valid for (scenario, h, S, record, testimony default, candidate set, continuation rule, tie-break).
- Nothing is called Q*.

### 4.6 Checks implemented
- Hand-derived values (§6.2).
- Point-mass expectimax equals brute force.
- The decomposition identity.
- Episode = label rollout, plus identical replay.
- Early-failure audit (none found).
- Depth consistency.
- Polarity complement and projection.
- Typed vs. scalar output.
- The unit-vs-STOP stakes pair.
- The evidence-change trace.

## 5. Allocation labels, candidates, memory (D-003; correction 4)
- **Objective:** obj(S) = J(S) − λ·cost(S). Admissible means cost ≤ budget, and always includes ∅.
- **Primary reference = the best admissible objective.** Enumerated exactly for small candidate sets; larger sets must label approximations and bounds.
  - **J(all)-relative sufficiency is a historical diagnostic** (`reference="all"`, `ExactOracle.allocation_labels`), because J(all) can fall below the best subset for non-monotone actors (`test_best_subset_reference_differs_from_j_all_when_non_monotone`).
- **Gold matching:** A is matched to one reference-attaining minimal set G* (by maximum F1, then recall, then smaller |G|, then lexicographic order). P, R and F1 are computed against that G*.
- **Regret:**
  - vs. the reference;
  - vs. the best set with cost ≤ cost(A);
  - vs. J(all) (historical).
- **Wasted unit:** gross J(A) − J(A∖u) ≤ λ·c(u) (net ≤ 0; the price is subtracted once).
- **Missed unit:** gross J(A∪u) − J(A) > λ·c(u).
- **Missed bundle:** a minimal completion of size ≥ 2 with positive net value whose singletons are all non-positive.
- **D4 / STOP:** the conditional reference R(S) = the best admissible objective among supersets of S, which equals the primary reference at S = ∅.
  - STOP(S) ⇔ obj(S) ≥ R(S) − tol.
  - Relevant(u | S) ⇔ u lies in a minimal completion attaining R(S).
  - The target never silently changes; it only conditions on choices already made.
- **Candidates** (visible only): K(j) observed or named; K(j→k) visible contact; R(j) incentive or conflict; R(j→k) contact plus reliability evidence about k.
- **Graph** (D-007):
  - Each record holds unit, path, variable, output (scalar fields or a typed hypothesis list), confidence, evidence IDs, timestamp (valid as of), cost, status, and history.
  - Statuses: fresh, retained, stale, contradicted, refreshed, abstain.
  - `policy_view()` exposes status and timestamp to the policy. A contradicted unit must be refreshed (a counted call) or abstained before use.
  - Trace `reports/bundle/trace-evidence-change.json`, asserted in `test_trace_where_new_evidence_changes_a_useful_inference`: K(rec) = 0.7 at t1, contradicted at t3 when office_a is empty, refreshed to 0.0 at t3, cost 2.
- **Margin:** taken from the actor's own action values only.

## 6. Tiny cases
Layout: lobby — hall — {office_a, office_b}; lobby chute where enabled.

### 6.1 Legacy privileged reference (Stage 0 values)
Asserted in `tests/test_oracle.py`, rendered in Part A of `reports/tiny-cases.md`.

### 6.2 Grounded cases: hand derivations (asserted in `tests/test_grounded.py`, `tests/test_corrections.py`)
| Case | Derivation (face value, `grounded_scalar` unless noted) |
|---|---|
| `false_belief` | default: ask, trust, drop → 0.7·0.90 + 0.3·(−0.60) = 0.45. K(rec) → walking now gives 0.80, so delta_J = +0.35 (D_action 0.35). Hedged: the default already walks, so the gain is 0 |
| `holder_rec` / `holder_carol` | name-symmetric: K(holder) 0.80, K(other) 0.45 |
| `relevance_shift` | J(∅) = 0.675; K(rec) = 0.835 (pure carryover); after Alice appears, 0.95 with or without K(rec) |
| `nested_reliability` | J(∅) = 0.575; R(rec→bob), K(rec), K(rec→bob) → 0.80; R(bob) alone 0.575; complementary {K(bob→rec), R(bob)} → 0.80. **Required depth 1**, since {K(rec)} suffices |
| `path_asymmetry` | J(∅) = 0.575; K(rec→alice) → 0.80, with D_action −0.10 (default continuation 0.475) and D_memory +0.325; K(alice→rec), K(rec), K(alice) = 0. Depth 2 under face value, **0 under hedged** |
| `stakes_m4_q0.95` | face value drops at A: 0.80. R(bob) → walk: 0.845. **Typed** K(alice) also gives +0.045 (legitimate inference, §4.2); scalar K(alice) gives 0 |
| `reversal_m*` (D-011) | p = 35/691. Grounded K(bob): J(walk) = 0.85 − 0.10p, J(drop) = 0.95 − (1 + 0.5m)p, so delta_J = **+0.02909 (×1), −0.04689 (×4)**; flip move(hall) → drop(office_a) at both stakes; D_memory 0; same candidates, output, prior and actions. Net at an illustrative λ = 0.01: +0.01909 vs. −0.05689, so STOP is preferred at ×4 |

## 7. Theory safeguards
- **P1/P2:** current-action component only. P2 uses exact pairwise-gap bounds with strict inequality and tie-boundary tests. Neither is a total-value pruning rule when D_memory can be positive or units complement each other (D-009).
- **P3:** grounded complement {K(bob→rec), R(bob)}; substitutes in `substitutes` (legacy) and `nested_reliability`.
- **P4:** no greedy guarantee is claimed.
- **P5 / stakes (D-011):**
  - The grounded **unit-vs-STOP** pair (§6.2) is the isolating test.
  - The privileged two-unit reversal (R(bob) vs. K(carol)) is a **diagnostic only**.
  - The restricted search's 0 grounded two-unit hits is not an impossibility proof for other task families.
  - Q5-B (averaging over histories) may be added as a frequency over histories.
- **Negative values** (D-009): kept unclipped and named **symbolic partial-model/default-interaction failures**. They are not LLM hallucination or leakage, and not C3 evidence.

## 8. Depth
- **Required depth** = the minimum, over subsets attaining the reference value, of the subset's maximum path length (0 for ∅). It is relative to the record's actor class and candidate set.
- By construction it never exceeds the depth of any reference-attaining set (`test_required_depth_never_exceeds_a_sufficient_sets_depth`, over all cases and records).
- The historical prefix definition (smallest d with J(U≤d) ≥ J(U)) is kept as `effective_depth_prefix`.
- Per-case values: generated table in `reports/tiny-cases.md`.
- Asserted facts (`test_depth_claims_from_review`): `path_asymmetry` 2 under face value and 0 under hedged; `nested_reliability` 1.
- Nothing here certifies an LLM's internal reasoning depth.

## 9. Reward and transition semantics (D-005)
- −0.05 on every step, +1 on success.
- Wrong chute drop: −0.5 × stakes, terminal.
- `give`: terminal and irreversible (no recovery action).
- A last-step success counts; timeout carries no penalty; an invalid action is a costed no-op.
- No early-failure incentive was found.

## 10. Generator audit, limitations, and open items
- **Generator audit** (D-008, a diagnostic and not a filter; table in `reports/tiny-cases.md`):
  - No grounded case has an individually entailed violation, either by family support or by visible evidence.
  - The defaults are **jointly unsatisfiable** at h in `path_asymmetry`, `reversal_m*` and legacy `depth2_handoff`. The v0.2 phrase "possible but not entailed" held per factor only.
- **Testimony sensitivity** (D-010): under hedged, the gains in `false_belief`, `path_asymmetry` and `relevance_shift` disappear; `nested_reliability` keeps its gain at depth 1. This limits the generality of the constructions and motivates the pilot.
- **Limitations:**
  - c(u) is a placeholder.
  - No LLM records yet.
  - Canonical-order tie-breaking is not yet counterbalanced in generated sets.
  - Graph contradiction detection covers only location claims refuted by the robot's own observations.
