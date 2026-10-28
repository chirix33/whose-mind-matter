# D-009 — Negative values (Stage 1 review Q3)

- Status: **accepted** (Stage 1 research review, 2026-10-28)

## Ruling
- Preserve negative labels; **no clipping.** Keep pre/post actions, beliefs, inference outputs and return components so the mechanism can be inspected.
- Name: **symbolic partial-model/default-interaction failures.** They are not measured LLM hallucination or perspective leakage. C3 requires the planned LLM intervention and its specified measurements.
- The nonnegative expected value-of-information result presumes a coherent optimal decision maker that can ignore the information. It does not guarantee that a forced bounded update improves realized return.
- Do not claim P4's monotone greedy guarantee for this objective. P1/P2 limitations for carryover and complementarities stand.
