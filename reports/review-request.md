# Review request — 2026-10-28 (Stage 1: semantics and counterexamples)

For: the research conversation, via Ashraf. The Stage 0 rulings (D-001…D-006) are implemented and recorded as accepted. Implementing them raised the questions below. None of them blocks the small local pilot, but Q1 and Q2 affect what the pilot's symbolic labels mean. Evidence paths are relative to the repo root.

## Q1 — What may a single unit's computation use? (affects D-001's "no unrestricted whole-scene reasoning")
**What is implemented** (`src/vomi/oracle.py`, spec §4.2):
- A unit's grounded output is ONE scalar per factor: P(the face-value default holds | h). That means "rec's belief is not false", "Bob is cooperative", "rec's model of Bob is accurate".
- It is computed as an exact marginal under the full generator, then I-projected into the bounded actor. Other factors keep their defaults.
- The content value is deliberately withheld. When it was exposed, K(alice) (whose belief equals the target) handed the actor the whole-scene posterior over the answer (`stakes_m4_q0.95`, now a regression test).

**Concern:** computing even the scalar uses inference over every person's hidden state.

**Alternatives:**
- **A (current):** exact generator marginal of the scalar.
- **B (local):** the marginal under the actor's own defaulted model with only this factor freed. Doubts that require several deviations at once are then suppressed: in `nested_reliability`, no single unit would suffice, and a 4-unit bundle would be needed.
- **C:** a person-local evidence rule, such as access-and-incentive features mapped to a fixed table. That needs a hand-specified inference rule per variable.

**Recommendation:** A for the symbolic target, with B reported as a sensitivity analysis. The scalar cannot carry the answer itself, and B makes single-unit computations nearly useless whenever deviations co-occur.

## Q2 — The bounded actor's hypothesis space is the generator support (structural leakage)
The actor knows which worlds the generator can produce. If a generator makes the defaults jointly unsatisfiable, the actor "knows" a default is violated without any computation.
- In legacy `depth2_handoff`, the receptionist's model of Alice can never match an informed Alice. The face-value actor therefore already hedges, and every grounded unit is worth 0.

**Proposal:**
- Require generators to make each decision-relevant default violation *possible but not entailed*. The six Stage 1 cases are built this way.
- Add a generator audit: for each scenario, check that some world consistent with h satisfies all defaults.
- Alternatively, give the actor a generic structural prior (e.g. independent per-factor deviations) instead of the generator support. That removes the leakage but makes the actor's model misspecified by design.

**Recommendation:** the audit plus generator rules for the pilot. Revisit the generic prior if the audit proves too restrictive in balanced generation.

## Q3 — Information can hurt bounded actors; no clipping proposed
- privileged_bounded K(alice) in legacy `depth2_handoff`: **−0.60**. Revealing Alice's belief without its accuracy leads the actor to a cheaper but wrong explanation.
- grounded K(alice) under hedged testimony in `path_asymmetry`: **−0.225**.

A Bayes-optimal actor cannot be hurt this way. These are symbolic instances of the C3 mechanism (partial modeling against remaining defaults).

**Recommendation:** keep negative labels (no clipping). Report them as a separate symbolic C3 diagnostic, distinct from LLM hallucination and leakage.

## Q4 — Gains depend on the testimony default (as the review anticipated)
| Case | Face value: J(∅) → J(gold) | Hedged (ε = 0.25) |
|---|---|---|
| false_belief | 0.45 → 0.80 | 0.80 → 0.80 (no gain) |
| path_asymmetry | 0.575 → 0.80 | 0.80 → 0.80 (no gain) |
| relevance_shift | 0.675 → 0.835 | 0.835 → 0.835 (no gain) |
| nested_reliability | 0.575 → 0.80 | 0.575 → 0.80 (gain persists) |

**Question:** which default should define the *main* symbolic labels? The two are equally principled.

**Recommendation:** label under both, train on face value (closest to the review's "act on direct reports at face value"), and report every C1/C2 symbolic result under both. A gain present only under face value is a statement about naive default actors, and should be framed that way.

## Q5 — D-006 ranking reversal: found in the privileged-bounded record; no isolating instance in the grounded record
**Found and independently derived** (`reversal_m1`/`reversal_m4`, record `privileged_bounded`, face value; `tests/test_grounded.py::test_stakes_ranking_reversal_privileged_bounded`):

| Unit | VoMI ×1 | VoMI ×4 | P(flip) (both stakes) | D_memory |
|---|---|---|---|---|
| U = R(bob) | +0.00724 | +0.00724 | 0.036 | 0 |
| V = K(carol) | +0.02909 | −0.04689 | 1.0 | 0 |

- Isolation holds: same observations, priors, costs and eligibility; identical base action and targets; no ties (actor margin ≥ 0.05).
- The flip ranking V > U is fixed, while the VoMI ranking reverses.
- This mirrors the design table: here the high-flip unit *loses* with stakes, instead of the low-flip unit gaining.

**Grounded record: no isolating reversal** in the search (`scripts/search_stakes_reversal.py`; counts in `reports/latest.md` § D-006). The per-criterion diagnostic shows why:
- Grounded outputs are a function of h, so a grounded current-action flip at a given state has probability 0 or 1.
- An isolating reversal would need two units that both flip deterministically, at both stakes, to targets with different error exposure. Under face-value trust, the two doubt-raising units either share a target or one of them stops flipping at ×4.
- The grounded record does yield **general** stakes pairs: in `reversal_m*`, K(bob), K(bob→carol) and R(carol) are worth +0.029 at ×1 and 0 at ×4.

**Alternatives:**
- **A.** Accept the privileged-bounded construction as the D-006 isolating demonstration, and report grounded stakes results as general pairs.
- **B.** Define grounded flip probability over a *distribution of histories* within a scenario family (a frequency), and search for reversals at that level.
- **C.** Defer the grounded isolating test to realized LLM labels, where per-state flip probabilities are fractional.

**Recommendation:** A now, plus B as part of balanced generation.

## Q6 — Negative current-action components are common under retention
In `path_asymmetry` and `nested_reliability`, D_action = **−0.10** and D_memory = **+0.325**. The flip alone is harmful: the default continuation walks back and hands the package over anyway.

**Consequence:** the matched no-carryover subset for D3 will exclude many depth-2 states.

**Question:** is this the intended reading (the value of a computation that changes plans is mostly carryover), or should the D3 comparison also include a "current action plus one-step lookahead" variant? **Recommendation:** keep the ruling as is and report the share of carryover states.

---
Evidence:
- `docs/research/implementation-spec.md` (v0.2)
- `reports/tiny-cases.md` (Part A legacy, Part B grounded)
- `reports/bundle/` (manifest, paired trace)
- `tests/test_grounded.py`, `tests/test_allocation_theory.py`
