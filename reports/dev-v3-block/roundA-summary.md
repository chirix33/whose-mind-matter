# Round A summary: the dev-v3 generator and its public-model qualification (symbolic; no LLM)

**Gated.**
- Plan: Opus R1–R15, applied as Entry 1a.
- Results: Opus RC1–RC4, applied as Entry 1b. Sonnet CONSISTENT: its own expectimax matches all 48 instances to within 5e-11.

**Frozen:** `dev-v3-freeze.json`, generated at clean commit `7871e4c` and committed in `984cb50`, before any LLM call on dev-v3.

## What dev-v3 is
- **Size:** 12 groups in 4 strata × 4 variants (stakes ×1/×4 × name rotation) = 48 instances, one hidden draw per group.
- **What the robot sees:** a visible lobby prologue, listing who was present at each announcement, statement, remark, quiet conversation, arrival and departure.
- **Public model:** declared per group in the task card. It is generated from the same specification that builds the reference prior, so every hidden variable, its support and its probabilities are disclosed. Couriers, persistence and the lie model are declared too.
- **Rules:** r6 (six numbered rules) holds over every positive-prior world. Tests trace every belief and nested-belief change, at t0 and after every first question.

## Key results (`qualification.md`)
- **Exact ask-aware values.** ExactOracle computes them with the plain posterior and all actions legal, in at most 1.2 s per instance. Bayes-optimal first actions:
  - 1a and 1c: drop at 0.95; 1b: search at 0.75;
  - 2a and 2c: give to the informed courier at 0.95; 2b: search the other two offices at 0.80;
  - 3a and 3c: give(F) at 0.95; 3b: ask F or search at 0.80;
  - 4a–4c: drop at ×1 and walk at ×4. The stakes flip holds in every stratum-4 group.
- **Evidence resolution is not vacuous.** A card-consistent superset prior (6 patterns in stratum 2; 3 in stratum 3, because the courier is public) conditioned on the rendered prologue reproduces every focal posterior and Q-value. With the prologue removed it fixes no best action, so **the visible history, not the template, resolves each case**. Labels hold given the declared rules (cooperation, quiet-conversation content, the rule-5 bystander clause, the rule-2 lobby-sighting clause).
- **Same-physical-state social pairs.**
  - 2a holder swap: give(H) vs give(N); using the wrong one loses 1.5.
  - 3a vs 3b: {give(F)} vs {ask(F), move(hall)}; loss 1.35. The Π≤1 inputs are equal, so this certifies depth 2 relative to Π≤1, not path direction.
  - Contrasts: 2a vs 2b (physical availability) and 3a vs 3c (different recipient belief).
- **With-chute counterfactual (stratum 3).** In 3c a chute makes drop(o_a) equal to give(F), so the missing chute is what gives K(F→R) task relevance there.
- **Privileged ex-ante ΔJ** for the Bayes actor: 0 for every focal unit in strata 1–3, since the evidence-resolved content is already in the posterior. 4b R units: +0.076 and +0.068; 4c: +0.068.
- **Text and order cues.** Two cues were found and fixed before the freeze: the order in which couriers were listed, and the reporters' speaking order. The tests now check that agent-visible text carries no design labels, IDs or order cues.
