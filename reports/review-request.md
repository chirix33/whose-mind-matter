# Review request — 2026-10-29 (redesign concept, D-018)

**Read first:** `reports/redesign-concept/CONCEPT.md`. It is a concept, and no experiment is authorized by it.

Also updated:
- `reports/method-review/METHOD_REVIEW.md`, with the D-018 corrections applied in place and listed at the top;
- `docs/decisions/2026-10-29-D018-stop-and-redesign-concept.md`.

## The concept in brief
- **Relations.** Unit content becomes a distribution over *referents*: which visible event's value a belief points to, with provenance. Value marginals stay derivable. An agent-side relation layer derives same/different/undetermined from the agent's own units and the public constraints. It is declared, costed and ablated, and it is not an evaluator success field.
  - Hand-derived on the existing rows: referents determine the handoff relation in 9 of 9 cases; marginals determine it in 4 of 9.
- **Computation constraint.** A sequential Tier 1 "office day": K tasks drawn from the validated construction families, with a shared cast. Perspective content is reused across decisions, and the log grows for causal reasons, not padding.
  - All baselines keep full-history access: direct, direct with more reasoning, and generic memory. Dense memory has the same representation as the method.
  - Compute is reported on two frontiers, GPU-seconds with caching on and actual-tokenizer tokens.
- **Causal links:** L1 headroom, L2 usability, L3 sparsity/predictability, L4 inferability per cost. Each has its own abandon criterion.
- **Gates:** G0 (CPU only) through G4. Thresholds are frozen per gate, and a failed gate stops the line with no revision.

## Decisions requested
1. **Is the concept convincing enough to keep the project going?** If not, the alternative is freezing and documenting the negative findings (concept §7).
2. **If it is: accept, modify or reject the versioned changes R1–R6** (concept §4.2), especially:
   - R4: the method processes a bounded context while every baseline has full-history access;
   - R5: the bounded-context Bayes actor as the symbolic label reference.
3. **If it is: authorize G0 only** (CPU-only dev-v4 generator and qualification, about a week of engineering), with its abandon criteria (a)–(e). Or authorize nothing yet.
4. **Confirm the scope reading.** The day-level task lengthens the robot's horizon. It does not add modeling of other people's long-horizon goals, which stays excluded.
