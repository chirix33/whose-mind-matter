# D-002 — Continuation semantics: does instantiated content persist after the labeled step?

- Status: **proposed**
- Date: 2026-10-28
- Affects: outline §3.4 (flip × value decomposition), §3.5 P1, §5.4 divergence tags; AGENTS §5.2, §5.4 P1; `ExactOracle.evaluate(continuation=…)`

## Problem
VoMI compares `a(S∪{u})` with `a(S)` at step t, but the action values also depend on what the agent does afterward. Two consistent readings:
- **retain**: content instantiated at t stays in the graph and informs later steps. This matches the outline's perspective graph with retention.
- **drop**: the continuation policy forgets S. Only the step-t decision uses it.

They give different labels. Under `retain`, the §3.4 identity `VoMI = P(flip) · E[ΔQ | flip] − λc` **fails**: a unit can be valuable without changing the current action. P1 ("no flip ⇒ VoMI = −λc") then fails too.

Evidence (`reports/tiny-cases.md`):
- `depth2_handoff`, K(alice): P(flip) = 0, ΔJ_retain = 0.05, ΔJ_drop = 0. The first move is `move(hall)` either way. Knowing Alice's room only pays off two steps later.
- `distractor_plausible`, K(rec): P(flip) = 0.5, E[ΔQ|flip] = 0.075, no-flip residual 0.0125. ΔJ_drop = 0.0375.

## Alternatives
**A. retain everywhere.**
- For: matches deployment with memory; values multi-step planning.
- Against: the §3.4 decomposition and P1 must be restated over the *whole continuation*: "flip anywhere in the remaining trajectory".

**B. drop everywhere.**
- For: the decomposition and P1 hold exactly.
- Against: undervalues units whose payoff comes later, so the router would re-infer each step. That inflates compute, and it conflicts with graph retention.

**C. retain for labels, and restate the theory in terms of trajectory flips (recommended).**
- Define the flip event as "the realized trajectory under S∪{u} differs from that under S". Then `ΔJ = P(traj-flip) · E[ΔR | traj-flip]` holds identically, and P1 holds in trajectory form.
- Keep the step-level P(flip) as the D3 baseline's target, as the outline intends. The residual becomes a reported quantity: "value not visible to a one-step flip detector". That is arguably extra evidence for C2.

## Recommendation
**C.** Implementing trajectory flips is a small change: compare realized action sequences per world.

## Consequences
- P1 pruning in deployment must check that no feasible content changes the current action **or any planned future action**. A one-step flip check is not a sound pruning test under retain.
- The divergence-tag subsets (outline §5.4) must specify which flip notion the D3 baseline uses.

## Minimal example
`depth2_handoff`. Reproduce with `pytest tests/test_oracle.py::test_depth2_complementary_pair_and_certification`.

## Review outcome
_(pending)_
