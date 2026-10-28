# D-008 — Generator support and default satisfiability (Stage 1 review Q2)

- Status: **accepted** (Stage 1 research review, 2026-10-28)
- Affects: scenario generation; D-001 bounded actor; pilot scenario selection

## Ruling
- The proposed audit is a **diagnostic, not a universal filter**. A scenario does not have to admit a world in which every default holds.
- **Log:**
  - posterior support size;
  - whether all defaults are jointly satisfiable;
  - which individual violations are possible or entailed;
  - whether a conclusion follows from visible evidence or only from narrow scenario-family support.
- An actor may know a *public* generative model without knowing the actual world. **The public prior must be fixed before the episode's hidden state is sampled.** Instance-specific support built from the actual state's secrets is a leak; enumerating hypotheses in a declared reference model is not.
- Visible contradictions may legitimately show that an assumption is wrong. Do not drop those cases. Keep no-model-needed (STOP) cases too.
- **Pilot generation:** dev groups span ambiguity, resolved evidence, distractors, false beliefs, conflicts, directed perspectives and relevance changes.
  - Balance families and factors before observing outcomes.
  - Never accept or reject scenarios by which method or testimony default wins.
  - Mechanistic subsets may use explicit identifying criteria, with selection rates reported.
- A single fixed broad prior is a later sensitivity test. No per-case prior fixes to restore a gain.

## Implementation
`vomi/theory.py::generator_audit`. For each factor it reports support size, joint satisfiability, possible vs. entailed violations, and whether an entailment already holds in the public prior (family support) or appears only after conditioning on h (visible evidence). The results appear in `reports/tiny-cases.md`.
