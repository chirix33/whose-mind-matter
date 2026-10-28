# Implementation specification — scientific contract (draft v0.1, 2026-10-28)

Status: **draft with open choices**. Items marked **OPEN (D-00x)** are proposed decisions in `docs/decisions/` awaiting research review. Nothing here supersedes the outline (`docs/research/methods-experiments-v2.md`) or `AGENTS.md`. Where this spec narrows or clarifies them, the discrepancy log says so.

Executable reference: `src/officeminds/` (world), `src/vomi/` (units, oracle), `tests/` (hand-checked constructions). Section numbers below are cited from code and tests.

---

## 1. Scope implemented so far
Tier 1 only: a deterministic world with rooms, closed offices, a lobby chute, people with private minds, templated answers, sincere tells, insincere claims, and relayed (nested) beliefs. Depth ≤ 2. Variables: Knowledge and Reliability. There are ten tiny scenarios (§6). Nothing here is LLM-labeled, and no bulk generation has been done.

## 2. Information boundaries (AGENTS §5.1)
| Layer | Type | Who may read it |
|---|---|---|
| Public task structure | `WorldConfig` (layout, roster, query facts, handoff availability, stakes, horizon) and the scenario `brief` | robot, controller, prompts |
| Physical simulator state | `World` positions, holding flag, time | simulator, oracle |
| Each person's private state | `PersonMind`: perceived event IDs, `beliefs`, `nested` beliefs, `intent` | simulator, oracle |
| Robot-visible observations and history | `Observation`, `VisibleHistory` (actions **and** observations) | robot, controller, prompts — via `VisibleHistory.to_agent_dict()` only |
| Robot's inferred perspective graph | `G_t` (§5.3) — **not implemented yet** | robot |
| Privileged annotations | `PrivilegedTrace` (hidden params, full event log, per-step minds), oracle labels | evaluator and training-label generation only |

Guarantees tested in `tests/test_world.py` and `tests/test_units.py`:
- Backstory events and events in other rooms never appear in the agent view.
- `legal_actions` and `generate_candidates` produce identical outputs for worlds that differ only in hidden state.
- Smoke-test prompts contain no hidden-parameter names.

The robot sees people only in its current room. Offices are closed: it learns who is inside only by entering.

## 3. Units, content, ontology
Unit `u = (path, variable)`, path length 1 or 2. Depth-0 physical reasoning is always on and is never a unit.

**Knowledge K(·).** Over the public *query facts* of the task (e.g. `alice_loc`, `meeting_room`). For each fact, j's epistemic state is one of: a supported belief value (which may be **false**), or `unknown`. Objective truth is stored separately in the physical state, never in a mind.
- `K(j)` = j's belief value or `unknown`, per query fact.
- `K(j→k)` = **j's belief about k's belief** per fact. This is neither k's actual belief nor the robot's belief about k. A test (`test_nested_content_is_js_belief_about_k_not_ks_state`) checks a case where `K(rec→alice)` is false while `K(alice)` is true.

**Reliability R(·).** The stable intent type ∈ {cooperative, obstructive}. Statement correctness is *not* a variable: it is derived from belief vs. truth. So a cooperative person with a false belief ("mistaken") answers sincerely and wrongly. That is not an intentional lie. `R(j→k)` (j's belief about k's intent) has no Tier 1 mechanics yet and is never generated. **OPEN (D-004)**: confirm this ontology, including whether "mistaken" stays a generator label for "cooperative + false belief" rather than a third intent.

**Belief dynamics** (`World._apply`).
- `witness`: people present learn the fact.
- `tell` (sincere): the speaker holds the belief; listeners adopt it and set nested(speaker); the speaker sets nested(listener).
- `claim` (possibly insincere, e.g. an answer to `ask`): listeners only update nested(speaker, fact) and do **not** adopt it.
- `say`: visible, with no belief effect (e.g. incentives).
- Obstructive people with a belief lie deterministically: they answer the first other domain value. With no belief they say "I don't know".

**OPEN (D-005)** lists these mechanics for review.

## 4. VoMI and oracle contract (AGENTS §5.2)
This defines the label type currently implemented, **exact symbolic-oracle VoMI** (`vomi/oracle.py`). Every quantity is computed by exhaustive enumeration. There is no sampling, so "exact" is literal *for this model and policy class*.

- **Hidden-world distribution.** Each scenario has a finite prior over hidden parameters. It is conditioned on the visible history by **replay**: a world is kept iff re-executing the robot's actions in it reproduces every observation exactly. The result is renormalized to `b_h`.
- **Unit content.** Deterministic in each world (§3). The content is the true mental content ("oracle content").
- **Decision policy a(S).** In world w the agent knows `c_S(w)`. Its belief is `b_{S,w} = b_h | c_S = c_S(w)`, and `a_S(w) = argmax_a Q(b_{S,w}, a)`. Ties are broken by canonical action order (sorted `Action` tuples), within a tolerance of 1e-9. **The policy reasons over the full raw history h.** See D-001: this is the central open question.
- **Action values.** `Q(b,a) = Σ_w b(w)[r_w(a) + V*(b')]`, where `V*` is the finite-horizon belief-optimal value. Observations update the belief by exact filtering. There is no discount. Reward: +1 success, −0.05 every step (including the terminal one), −0.5 × stakes for an irreversible error (wrong chute drop, or a handoff routed to the wrong room). The episode ends at success, error, or the horizon (default 8), with no extra timeout penalty.
- **Realized return.** `R_w(a, b)` = the return in true world w of taking a, then following the belief-optimal policy. The continuation belief starts at b and is updated by observations.
- **Allocation value.** `J(S) = Σ_w b_h(w) R_w(a_S(w), b_cont)`.
  - Under continuation **`retain`** (default), `b_cont = b_{S,w}`: instantiated units stay in the graph.
  - Under **`drop`**, `b_cont = b_h`: the continuation forgets them.
  - **OPEN (D-002).**
- **VoMI.** `VoMI(u|S) = J(S∪{u}) − J(S) − λ·c(u)`. Cost `c(u)` is in **instantiation calls**: 1 per unit for now. It is a placeholder until real token and latency costs are measured. λ is in return units per call. Labels store the raw `ΔJ`; λ is applied at analysis time. Cache reuse is not modeled yet (§5.3).
- **Naming.** These are values of an *observation-limited* Bayes-optimal agent. They are **not** `Q*` of a fully informed state oracle. The full-information value (each world known) is reported separately as a privileged bound, computed by independent brute-force sequence search.
- **Validity.** A label is valid for a specific (scenario, visible history, S, continuation mode, candidate set, policy class, tie-break). Labels are not transferable across S.

### Three label records (kept distinct)
1. **Exact symbolic-oracle VoMI**: implemented as above.
2. **Oracle-content LLM marginal value**: true content supplied to the *LLM* policy. It requires real LLM calls and is possibly stochastic. Not implemented.
3. **Realized LLM VoMI**: LLM-inferred content and LLM decisions, with recorded sampling. Not implemented.

The symbolic-to-LLM gap must be measured, not assumed. A symbolic label says nothing about how an LLM acts.

### Checks implemented
- Hand-derived values for every tiny case (§6).
- For every hypothesis world, point-mass belief expectimax equals exhaustive brute-force search (an independent code path).
- `J(∅) = V*(b_h)`.
- `V*(b_h) ≤ J(U) ≤ full-information bound`. Information never hurts the symbolic agent, so **negative VoMI arises only from cost in record 1**. Any harm from modeling (C3) must come from records 2 and 3.

## 5. Allocation labels, candidates, memory
### 5.1 Gold allocation (AGENTS §5.3)
All three definitions are computed by exhaustive subset enumeration over the candidate set U:
- **minimal sufficient**: J(S) = J(U) with no sufficient proper subset. May be non-unique.
- **minimum-cost sufficient**.
- **leave-one-out necessity**, as a value drop `J(U∖u) < J(U)` and as an action change.

The outline's "minimal set whose removal changes the oracle action" is ambiguous between these. **OPEN (D-003)**. The `substitutes` case shows four minimal sufficient singletons and *no* LOO-necessary unit, even though each unit has value 0.05.

### 5.2 Candidates
`generate_candidates` reads only the brief, the observations and the utterances:
- **depth-1 K**: any roster person observed or named (word match).
- **depth-2 K(j→k)**: j and k both known, plus visible communication (an utterance by one naming the other) or visible co-presence.
- **R(j)**: j uttered a templated incentive phrase, or there are conflicting claims about one fact.

It never reads intent, hidden co-presence or generator tags. Recall against privileged reference candidates (the union of minimal sufficient sets) will be reported separately from router quality. Rules for false-exclusion audits are TODO once balanced generation exists.

### 5.3 Perspective graph and memory — specification, not implemented
Each unit record holds: path, variable, typed content (value | `unknown` | distribution), confidence, visible evidence IDs, timestamp, cost incurred, and status (fresh | retained | stale | contradicted).
- A **retained** unit is not re-inferred. It costs retrieval/prompt tokens (counted), not an instantiation call.
- Invalidation: a unit becomes **stale** when new visible evidence touches its person or fact (they appear, speak, or a relevant event is observed). It becomes **contradicted** when a visible claim conflicts with its content.
- Stale units are never presented as fresh. The graph is never silently cleared.
- For the symbolic oracle, `retain` corresponds to this memory model.

### 5.4 STOP and margin (planned)
STOP label at state (h, S): STOP iff `max_u VoMI(u|S) ≤ 0` over the remaining candidates at the given λ.

The deployment margin must come from the policy's own scores, never from true values. Options are an LLM self-score gap or a log-prob gap. The call that produces it is counted. **OPEN** with D-001, because it depends on the policy class.

## 6. Tiny cases with hand derivations
Layout: lobby — hall — {office_a, office_b}. The robot starts in the lobby holding the package. The chute is in the lobby (drop: 1 step). Walking: hall, office (see who is inside), then deliver = 3 steps → 0.85; if wrong, hall, other office, deliver = 5 steps → 0.75. Worlds are uniform over Alice's office unless stated.

| Case | Hand derivation | Oracle |
|---|---|---|
| `depth0_visible` | Alice is in the lobby: deliver → 0.95. K(rec) has 1 bit of content entropy and P(flip) = 0 | ✔ |
| `depth1_knowledge` | J(∅): ask rec (1 step). Known (½) → drop: 0.90. Unknown → walk: 0.80 − 0.05 = 0.75. Total **0.825**. J(K(rec)): known → drop 0.95; unknown → walk 0.80. Total **0.875** | ✔ |
| `distractor_plausible` | J(∅): ask rec, then ask carol: ½·0.90 + ¼·0.85 + ¼·0.70 = **0.8375**. J(K(rec)) = J(K(carol)) = **0.8875**. Both = ¾·0.95 + ¼·0.80 = **0.9125** | ✔ |
| `distractor_obvious` | Carol visibly "just got here", so K(carol) is constant: ΔJ = 0, P(flip) = 0 (P1) | ✔ |
| `substitutes` | Alice told Bob. Ask Bob, then drop: **0.90**. Any one of K(alice), K(bob), K(bob→alice), K(alice→bob) → drop now: **0.95** | ✔ |
| `depth2_handoff` | No chute. give(rec) succeeds iff rec's belief about Alice's meeting room equals Alice's belief (= her location). J(∅): walk **0.80**. J(K(alice)): walk to the known room **0.85**. J(K(rec→alice)) **0.80**. Both: match (½) → give 0.95, else walk known 0.85 → **0.90** | ✔ |
| `stakes_m{1,4}_q0.975` | Bob claims office_a and states an incentive; P(coop) = q. drop(office_a) beats walk at both stakes (thresholds q > 0.929 / 0.966). R(bob): ΔJ = 0.025·(1 + 0.5m) = **0.0375 / 0.075**; P(flip) = **0.025** at both | ✔ |
| `stakes_m{1,4}_q0.95` | Base action is drop at m=1 but walk at m=4, so P(flip) is **0.05 vs 1.0**. Naive stakes pairs change flip probability too (P5 caveat) | ✔ |

All values are asserted in `tests/test_oracle.py`. The generated table with every unit's report is `reports/tiny-cases.md`.

## 7. Theory safeguards — status
- **P1:** the implemented check is conditional on the current S, the policy class, and *all* consistent worlds (exhaustive, not sampled). Under `retain`, a unit can have value without a first-step flip (`depth2_handoff` K(alice): residual 0.05; `distractor_plausible` K(rec): residual 0.0125). So "no flip ⇒ VoMI = −λc" **holds under `drop` but not under `retain`**. D-002.
- **P2:** not implemented. It must bound changes in the *pairwise gap* Q(a1) − Q(a2), not per-action changes. Boundary and tie tests are TODO.
- **P3:** (a) complementary: `depth2_handoff`. Neither K(alice) nor K(rec→alice) alone flips the first action; together they do. (b) substitutes: `substitutes`, plus K(alice→rec) substituting K(rec→alice) in `depth2_handoff`. Margin-triggered expansion is not claimed to find complements.
- **P4:** not implemented. No general greedy guarantee is claimed. Pure complementarity gives γ = 0 (K(rec→alice) has singleton value 0 but conditional value 0.05).
- **P5:** paired case verified numerically at q = 0.975: same P(flip), same content entropy, different ΔJ. At q = 0.95 the base action changes with stakes, and so does P(flip). Limitation: in this pair all three units move together, so it shows a change in VoMI **magnitude** relative to λ (allocation flips from STOP to instantiate when λc = 0.05) but **not a ranking change** among units. A ranking-change pair is TODO.
- **Tie-break sensitivity:** in the symmetric `distractor_plausible`, the base action asks carol first purely by canonical order. That makes P(flip) for K(rec) and K(carol) 0.5 vs 1.0 while their ΔJ is equal (0.05). Flip-probability labels (D3) inherit tie-break artifacts. VoMI does not, in this case.

## 8. Depth certification (AGENTS §5.5)
Effective depth ℓ* = the smallest d such that the units with depth ≤ d reach J(U). This is **relative to the oracle policy class of §4 and the candidate set**. `depth2_handoff` certifies ℓ* = 2. `indistinguishable_pairs` also exhibits world pairs that are identical in history and in all depth-≤1 unit contents but whose fully allocated optimal actions differ. That is the controlled-pair form AGENTS asks for, but again only relative to the oracle's policy class. Nothing here constrains an LLM's internal reasoning depth.

## 9. Open choices (must be reviewed before bulk label generation)
| ID | Question | Blocking |
|---|---|---|
| D-001 | Policy class and content semantics for labels: Bayes-optimal over raw h with oracle content (current) vs. graph-limited policy with evidence-grounded content | **all label generation** |
| D-002 | Continuation `retain` vs `drop`; consequence for the §3.4 decomposition and P1 | labels, RQ2 |
| D-003 | Which gold-allocation definition drives which metric | allocation metrics, D4 targets |
| D-004 | Knowledge/Reliability ontology | generator, Tier 2 role cards |
| D-005 | Tier 1 mechanics defaults (chute, handoff routing, sincere tell, deterministic lie, bystanders, timeout) | generator |
| D-006 | Stakes-pair construction for P5/RQ2(b) | RQ2 subsets |
