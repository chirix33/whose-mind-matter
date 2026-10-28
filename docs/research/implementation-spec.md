# Implementation specification — scientific contract (v0.2, 2026-10-28)

**Status.** v0.2 incorporates the Stage 0 research review: D-001…D-006 are recorded as accepted, with constraints, in `docs/decisions/`. Items marked **OPEN** are new questions in `reports/review-request.md`. Nothing here supersedes the outline (`docs/research/methods-experiments-v2.md`) or `AGENTS.md`; narrowings are logged in `docs/decisions/discrepancy-log.md`. v0.1 values are preserved as the *legacy privileged perfect-content reference* (§6.1).

**Executable reference.**
- `src/officeminds/`: world, scenarios, episodes.
- `src/vomi/units.py`: units, defaults, candidates.
- `src/vomi/oracle.py`: the three label records, the D-002 decomposition.
- `src/vomi/allocation.py`: gold sets, D4, metrics.
- `src/vomi/graph.py`: perspective graph, features.
- `src/vomi/theory.py`: P2, audits.
- `tests/`.

---

## 1. Scope implemented so far
Tier 1 only, depth ≤ 2, Knowledge and Reliability. That includes nested Reliability **R(j→k)**, which the review kept in core scope. There are 10 legacy tiny cases and 6 grounded cases (§6), plus a parameterized conflicting-reports family for the stakes search, with one found ranking-reversal pair `reversal_m1`/`reversal_m4` (§7). There are no LLM labels, no bulk generation, and no training.

## 2. Information boundaries (AGENTS §5.1)
| Layer | Type | Who may read it |
|---|---|---|
| Public task structure | `WorldConfig` + scenario `brief` | robot, controller, prompts |
| Physical state and objective truth | `World` positions, holding flag, time, `World.truth(fact)` | simulator, evaluator |
| Private minds | `PersonMind`: beliefs, nested beliefs, **assessments** (R(j→k) content), intent, perceived events | simulator, evaluator |
| Robot-visible history | `VisibleHistory` (actions **and** observations, including the literal report ledger of heard utterances). Serialized only via `to_agent_dict()` | robot, controller, prompts |
| Robot perspective graph | `vomi.graph.PerspectiveGraph`: unit records built from visible evidence plus unit outputs | robot |
| Controller features | `vomi.graph.visible_features` (depth, recency, spoke-to-robot, conflicting reports, stated incentive, stakes, the actor's own decision margin, evidence count) | controller |
| Privileged annotations | `PrivilegedTrace`, label records, true contents | evaluator, label generation only |

**Invariance test** (`test_invisible_world_pair_gives_identical_actor_inputs_and_outputs`): two hidden worlds of `false_belief` with an identical agent view yield identical candidates, features, grounded outputs and grounded actions. Only the privileged record lets the private difference (Alice's switch) reach an actor.

## 3. Units, content, ontology (D-004 accepted)
- **K(j):** j's belief value per public query fact, or `unknown`. It may be false.
- **K(j→k):** j's belief about k's belief.
- **R(j):** intent ∈ {cooperative, obstructive}.
- **R(j→k):** j's **assessment** of k's intent ∈ {cooperative, obstructive, unknown}. Not k's actual intent, and not j's reliability.
- **Mistaken** = cooperative plus a false or outdated belief. It is a derived reporting slice (cooperative-accurate / mistaken / obstructive), computed per person from (intent, belief vs. truth). An obstructive person with a false belief is reported as obstructive.
- Scenarios must declare objective truth for every non-location query fact. `World.truth` raises otherwise: an undeclared truth previously made every belief count as a default violation.

**Tier 1 scripted policies** (deterministic, inspectable; identical for every method):

| Event | Effect |
|---|---|
| `witness` | the people present learn the fact |
| `tell` (sincere) | the speaker holds the belief; listeners adopt it plus nested(speaker); the speaker sets nested(listener) |
| `claim` | listeners update only nested(speaker). Answers to `ask` are claims. Obstructive people lie deterministically (the other domain value) or say "I don't know" |
| `assert` (possibly insincere) | listener rule: a listener without her own belief adopts the value, unless she assesses the speaker as obstructive, in which case she adopts the other value of the binary domain; the speaker assumes listeners adopted it |
| `assess` | listeners adopt "person X has intent v"; the speaker too, unless vouching for himself |
| `enter` | a person walks into a room |
| `say` | visible, with no belief effect |

Intent is never encoded in wording, names or order. The only reliability cues are templated incentive statements and conflicting claims.

## 4. Label records and evaluator contract (D-001, D-002 accepted)

### 4.1 Evaluator
- Hidden-world posterior `b_h`: the finite scenario prior restricted to worlds that **replay** the visible history exactly, renormalized.
- The evaluator enumerates these worlds to take expectations of realized returns. **Actors never see them.**

### 4.2 The bounded actor (main policy class)
- **Hypothesis space:** the generator's support, conditioned on h by replay. This is a modeling choice with a known risk (§10, OPEN Q2).
- **Face-value defaults**, one per mental factor (all persons, all paths of depth ≤ 2):
  - K(j): no false belief on query facts (belief ∈ {truth, unknown});
  - R(j): cooperative;
  - K(j→k): j's model of k's belief ∈ {k's belief, unknown};
  - R(j→k): j's assessment ∈ {k's intent, unknown}.
- **Actor prior** ∝ generator prior × ε^(number of violated defaults among UNMODELED factors):
  - ε = 10⁻⁶: **face value** (main);
  - ε = 0.25: **hedged** (the alternative testimony default the review required).
- **Consequences:**
  - A direct, unambiguous report is acted on at face value (`test_direct_testimony_default_acts_on_face_value`).
  - **Conflict rule:** conflicting testimony is explained with the fewest default violations, with remaining ties weighted by the prior. This is lexicographic as ε → 0.
- **Testimony:** heard utterances are physical observations in the literal ledger, and every method sees them. The actor conditions on them exactly through replay.
- **What a mental computation is.** Instantiating unit u (i) removes u's default and (ii) I-projects the actor prior onto u's **grounded output**: the posterior P(default holds | h) of u's factor under the generator (iterative proportional fitting to 10⁻¹⁴).
  - The output is *only* this accuracy/cooperation/mismodel probability, **never the content value**.
  - Reason: exposing the content marginal let K(alice), whose belief equals the target, deliver the whole-scene posterior over the answer. It was found in `stakes_m4_q0.95` and a regression test now covers it.
  - A unit with no visible support gets its prior accuracy, which carries no information: e.g. K(alice) in `depth1_knowledge` = 0.
  - **OPEN Q1:** computing that scalar uses whole-generator inference; whether that is acceptable.
- **Planning:** physical planning is belief-space expectimax under the actor's own model (depth-0 reasoning, mandatory). Only mental modeling is bounded.

### 4.3 Three label records (descriptive names)
| Record | Actor | Unit content given to the actor | Role |
|---|---|---|---|
| `privileged_bayes`: **legacy privileged perfect-content reference** | Bayes-optimal over h | true contents of S | Stage 0 values; reference only, never a target |
| `privileged_bounded`: **privileged perfect-content, bounded actor** | face-value bounded actor | true contents of S (point-mass constraint) | reference; **not an upper bound** (it can be negative, §7) |
| `grounded`: **grounded bounded-policy value** | face-value (or hedged) bounded actor | grounded outputs (§4.2) | **main symbolic target** |
| realized LLM value | LLM | LLM-inferred | not implemented (Stage 2+) |

### 4.4 Fixed continuation and the D-002 decomposition
- `Q_ref(w, m, a)` is the realized return in true world w of action a. After a, the **same actor with cognitive state m** continues: no new instantiations, retained content, beliefs updated by exact conditioning on new observations.
- No allocation is re-solved per branch.
- For a = a(m) and a_y = a(m ∪ {u}):
  - `D_action = E[Q_ref(m, a_y) − Q_ref(m, a_0)]`
  - `D_memory = E[Q_ref(m_y, a_y) − Q_ref(m, a_y)]`
  - `VoMI_retained = D_action + D_memory − λc = J(S∪u) − J(S) − λc`
- The residual is |…| < 10⁻¹² for every unit, case and record (`test_decomposition_identity_everywhere`). The identity is algebraic, not causal.
- **Carryover effect** = positive value with zero current-action flips.
- Measured patterns:
  - pure current-action (`false_belief` K(rec): D_action 0.35, D_memory 0);
  - pure carryover (`relevance_shift` K(rec): 0 / 0.16);
  - **negative current-action component** (`path_asymmetry` K(rec→alice): −0.10 / +0.325). Without retention the flip alone is harmful, because the default continuation walks back and hands over the package anyway.
- **Legacy display required by the review** (`depth2_handoff`, K(alice), legacy record):
  - E[Q(m,a0)] = 0.80, E[Q(m,ay)] = 0.80, E[Q(my,ay)] = 0.85;
  - D_action = 0, D_memory = 0.05, residual 0, carryover.

### 4.5 Cost, λ, validity, naming
- c(u) = 1 instantiation call (placeholder). λ is in return units per call.
- Retained units cost no new instantiation in the symbolic actor; observation updates are free.
- Labels store raw ΔJ and components; λ is applied at analysis time.
- A label is valid for (scenario, h, S, record, testimony default, candidate set, continuation rule, tie-break).
- No value is called Q*. The full-information value is a privileged bound computed by independent brute force.

### 4.6 Checks implemented
- Hand-derived values for 4 non-degenerate-posterior grounded cases (§6.2).
- Point-mass expectimax equals brute force.
- The decomposition identity holds everywhere.
- Each episode's return equals its label rollout, and replay is identical.
- An early-failure-incentive audit, by full-information search over every hypothesis world of every case, finds **none**.

## 5. Allocation labels, candidates, memory (D-003 accepted)
- **Sufficiency:** preserves the reference expected task value, J(S) ≥ J(U) − 10⁻⁹, under the stated record and testimony default.
- We compute minimal sufficient sets, minimum-cost sufficient sets, and LOO necessity (both value-based and action-based).
- **Matching:** a predicted allocation A is matched to ONE minimal sufficient set G*, chosen by maximum F1, then recall, then smaller |G|, then lexicographic order. P, R and F1 are computed against G*.
- **Also reported:**
  - regret vs. J(U) and vs. the best budget-feasible set;
  - the optimal-action set (`optimal_action_set`);
  - wasted units (conditional net value ≤ λc);
  - missed units;
  - **missed bundles**: minimal completions of size ≥ 2 with positive net value whose singletons are all non-positive.
- **D4 target:** conditional relevance(u | S) = u ∈ some minimal completion of S. **STOP(S)** = S sufficient. There is a minimum-cost variant. In `substitutes`, all four units are relevant at ∅; after one is chosen, STOP and nothing else is relevant.
- **Candidates** (visible only):
  - K(j): j observed or named;
  - K(j→k): visible contact between j and k;
  - R(j): templated incentive or conflicting claims;
  - **R(j→k):** the K(j→k) contact condition plus visible reliability evidence about k.
- **Graph** (`PerspectiveGraph`): each record holds unit, path, variable, output, confidence, evidence IDs, timestamp, cost and status.
  - Status is retained, stale (new visible evidence about the person), or contradicted (the robot later observed the claimed room without the recipient).
  - Re-instantiating a retained unit is an error. Advancing costs nothing.
- **Margin:** taken from the actor's own action values (`decision_margin`), never from true values. In an LLM pipeline, the call that produces it will be counted.

## 6. Tiny cases
Layout: lobby — hall — {office_a, office_b}. Chute in the lobby where enabled. Walking from the lobby: right office 0.85, wrong-then-right 0.75.

### 6.1 Legacy privileged reference (Stage 0 values, unchanged)
Reproduced in Part A of `reports/tiny-cases.md` and asserted in `tests/test_oracle.py`:
- depth1: J(∅) 0.825, K(rec) 0.875, K(alice) 0.95;
- distractor: 0.8375 / 0.8875 / 0.9125;
- depth2: 0.80 / 0.85 / 0.80 / 0.90;
- substitutes: 0.90 → 0.95;
- stakes q = 0.975: ΔJ(R(bob)) 0.0375 / 0.075.

Under the grounded record, all legacy cases except `stakes_m4_q0.95` have **zero** unit value: their generators contain no false beliefs that face value would mishandle, or they entail default violations (§10).

### 6.2 Grounded cases: hand derivations (face value unless noted)
| Case | Derivation | Asserted |
|---|---|---|
| `false_belief` (Alice switched offices unseen with p = 0.3) | default: ask rec and trust the answer → 0.7·0.90 + 0.3·(−0.60) = **0.45**. K(rec) (P(outdated) = 0.3): walking now gives 0.80, beating ask-then-walk (0.77) → **0.80**; D_action 0.35, D_memory 0. **Hedged:** P_actor(moved) = 0.075/0.775, so the default already walks: **0.80, gain 0** | ✔ |
| `holder_rec` / `holder_carol` | name swap: K(holder) 0.80, K(other) 0.45, J(∅) 0.45 in both | ✔ |
| `relevance_shift` (Alice may walk in at t = 1) | J(∅) = ½·0.90 + ½·0.45 = **0.675**. K(rec) = ½·0.90 + ½·(0.7·0.80 + 0.3·0.70) = **0.835**, pure carryover. After Alice appears: J = 0.95 with or without K(rec) | ✔ |
| `nested_reliability` | give fails iff Bob obstructive and rec naive (0.25): 0.75·0.95 − 0.25·0.55 = **0.575**. R(rec→bob), K(rec), K(rec→bob) each → walk **0.80**. R(bob) alone **0.575** (the default assumes rec sees through Bob). **Complementary pair** {K(bob→rec), R(bob)} → 0.80, while each alone gives 0.575 | ✔ |
| `path_asymmetry` (F6) | forwarding fails iff Alice heard of the move and did not tell rec (0.25) → **0.575**. K(rec→alice) → **0.80**. K(alice→rec), K(rec), K(alice) → 0.575 (directed asymmetry). D_action: the default continuation returns and gives: 0.75·0.85 + 0.25·(−0.65) = 0.475 → **−0.10**; D_memory **+0.325** | ✔ |
| `stakes_m4_q0.95` | face value drops at A: 0.95·0.95 − 0.05·2.05 = **0.80**. R(bob) → walk: 0.95·0.85 + 0.05·0.75 = **0.845** | ✔ |

## 7. Theory safeguards: status
- **P1:** stated for the current-action component only. A no-flip certificate implies D_action = 0, not VoMI = −λc, whenever D_memory can be positive.
- **P2:** `p2_certifies_no_flip` uses exact **pairwise-gap** decrease bounds with strict inequality.
  - Tests cover the tie boundary.
  - A counterexample shows a per-action bound |Δq| ≤ δ certifying wrongly (the gap moves by 2δ).
  - An end-to-end check verifies that certification ⇒ no current-action flip.
- **P3:**
  - complements (grounded) `nested_reliability` {K(bob→rec), R(bob)}; complements (legacy) `depth2_handoff`;
  - substitutes: legacy `substitutes`, and grounded K(rec)/K(rec→bob)/R(rec→bob) in `nested_reliability`.
- **P4:** not implemented. No greedy claim.
- **P5 / D-006:** the entropy objective is invariant across stakes in every stakes pair (same posterior).
  - **Isolating ranking reversal found in `privileged_bounded`** (`reversal_m*`; Bob says A, Carol says B):
    - U = R(bob): VoMI +0.00724 at both stakes, P(flip) 0.036;
    - V = K(carol): +0.02909 at ×1, −0.04689 at ×4, P(flip) 1.0;
    - identical base action and targets, zero carryover, actor margin ≥ 0.05;
    - hand-derived in `test_stakes_ranking_reversal_privileged_bounded`.
  - **No isolating reversal in `grounded`.** Grounded flips are a function of h (0/1 per state). The diagnostic shows every grounded reversal fails isolation (a unit never flips, the base action changes, or the flip pattern changes). Grounded stakes results are therefore general pairs (OPEN Q5).
- **Bounded actors can be hurt by information.**
  - privileged_bounded K(alice) in legacy `depth2_handoff` = −0.60;
  - grounded K(alice) under hedged testimony in `path_asymmetry` = −0.225.

  Partial modeling against remaining defaults can mislead. A Bayes-optimal actor cannot suffer this. The finding is relevant to C3. **OPEN Q3:** no clipping is proposed.

## 8. Depth certification
ℓ* = the smallest d such that the units of depth ≤ d reach J(U), **relative to the record's actor class and candidate set**.
- Grounded: ℓ* = 2 in `path_asymmetry` and `nested_reliability`.
- The legacy pair construction (`indistinguishable_pairs`) applies to the privileged record only, because grounded actions are a function of h.

## 9. Reward and transition semantics (D-005 accepted)
- Every executed step costs −0.05, including the terminal one. Success is +1.
- A wrong chute drop costs −0.5 × stakes, is terminal, and is irreversible.
- `give` is terminal and irreversible, because the package leaves the robot's custody and Tier 1 has no recovery action.
- At the cap, the transition applies first: a last-step success counts. Otherwise the episode times out with no penalty.
- An invalid action is a costed no-op.
- Audit: no early-failure incentive in any case. Tests are in `tests/test_allocation_theory.py`.

## 10. Known limitations and open questions
1. **OPEN Q1.** Unit outputs are exact generator marginals of a single scalar per factor. Whether a unit may use whole-generator inference to compute that scalar.
2. **OPEN Q2.** The bounded actor's hypothesis space is the generator support. If a generator makes defaults jointly unsatisfiable, the actor "knows" a violation exists without any computation. That is structural leakage, seen in legacy `depth2_handoff`, where the default actor already walks. The grounded cases are built so that default violations are possible but not entailed. A generator audit is proposed.
3. **OPEN Q3.** Negative grounded and privileged values (above).
4. Robustness depends on the testimony default. Under hedged, the gains in `false_belief` and `path_asymmetry` vanish (the hedged default already walks), while the `nested_reliability` gain persists (`reports/tiny-cases.md`, Part B).
5. c(u) is a placeholder. There are no LLM records yet. Tie-breaking is canonical order and has not yet been counterbalanced in generated sets.
