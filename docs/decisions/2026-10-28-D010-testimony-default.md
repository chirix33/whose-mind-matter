# D-010 — Testimony default (Stage 1 review Q4)

- Status: **accepted** (Stage 1 research review, 2026-10-28)

## Ruling
- **Face value** (ε = 10⁻⁶) is the prespecified primary convention of the scalar prototype. **ε = 0.25 (hedged) is a mandatory sensitivity condition.** Neither is claimed to be a psychologically validated model.
- No separate router training under either condition for now. Recalculate and report both on the tiny symbolic examples.
- **LLM pilot:** the same neutral task instructions and evidence interface for every method. Do not force the direct LLM into face-value assumptions to create headroom; it may already handle these cases.
- Report disappearing gains plainly. Under hedged, `false_belief`, `path_asymmetry` and `relevance_shift` lose their gain; `nested_reliability` keeps it but has depth 1. This limits the generality of the constructions and motivates the pilot. It is not a reason to drop the hedged condition.
