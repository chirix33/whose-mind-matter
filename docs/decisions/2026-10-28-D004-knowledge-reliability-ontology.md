# D-004 — Knowledge / Reliability ontology

- Status: **accepted — mistaken = cooperative + false/outdated belief; R(j→k) KEPT in core** (review 2026-10-28)
- Date: 2026-10-28
- Affects: outline §3.2, §5.1 (intent types: cooperative, mistaken, obstructive), §5.2 role cards; AGENTS §5.1

## Proposal (implemented provisionally in `vomi/units.py` and `officeminds/world.py`)
- **Knowledge**, per public query fact. The value is a believed value (it may be false) or `unknown`. Truth lives only in the physical state.
  - `K(j→k)` = j's belief about k's belief value.
  - Graded confidence is not modeled in Tier 1: beliefs are categorical. Confidence belongs to the robot's inferred unit (in G_t), not to the person.
- **Reliability** = stable intent ∈ {cooperative, obstructive}.
  - "Mistaken" is **not** an intent. It is a generator label for "cooperative with a false belief", i.e. statement-level incorrectness derived from Knowledge vs. truth.
  - This keeps the outline's three generator types while satisfying AGENTS ("a mistaken cooperative speaker is not automatically an intentional liar").
- **Obstructive behavior:** with a belief, a deterministic lie (the other value in a binary domain); without one, "I don't know".
  - Open: should obstructive people sometimes tell the truth, e.g. strategically? That would make R non-identifiable from one exchange, which is more realistic but harder.
- `R(j→k)` is not generated until Tier 1 has mechanics that create beliefs about others' intent (e.g. a warning "don't trust Bob").

## Questions for review
1. Accept "mistaken = cooperative + false belief" rather than a third intent?
2. Should obstructive people be stochastic or strategic liars in Tier 1?
3. Add mechanics for `R(j→k)` in core scope, or defer?

## Review outcome
**Accepted.** Supplied by the research review 2026-10-28 (`research-reviews/stage-0-research-review.md`, supplied by Ashraf; that folder is gitignored, so the binding points are restated here).

- Mistaken = cooperative intent plus a false or outdated belief. Keep cooperative/mistaken/obstructive as derived reporting slices, and define how overlaps are reported.
- Tier 1 uses fixed, inspectable scripted response policies: deterministic first, optional seeded stochastic variants, no equilibrium or strategic optimizer. The same policy applies to every method.
- Never encode intent through wording, names, template order or hidden flags. Include visible evidence that makes some reliability decisions inferable, plus ambiguity controls.
- **R(j→k) stays in the core ontology:** j's belief/assessment of k's intent. It needs a finite representation and a tiny example, and candidate eligibility still requires visible evidence. Answer to my question 3: do not defer it.
