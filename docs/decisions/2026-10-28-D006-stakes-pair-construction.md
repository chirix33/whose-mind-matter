# D-006 — Stakes-pair construction for P5 / RQ2(b)

- Status: **proposed**
- Date: 2026-10-28
- Affects: outline §3.5 P5, §5.3 F5, RQ2(b); AGENTS §5.4 P5

## Finding
Multiplying the error penalty ×4 with identical observations does **not** generally leave flip probability unchanged:
- `stakes_m*_q0.95`: P(flip) of R(bob) is 0.05 at ×1 but 1.0 at ×4, because the base action switches from drop to walk.
- `stakes_m*_q0.975`: P(flip) = 0.025 at both, content entropy equal, ΔJ 0.0375 vs 0.075. This is a valid isolating pair.

## Proposal
1. Generate stakes pairs, then **keep a pair for the P5-isolating subset only if** the base action a(S) and the per-world flip pattern are identical across stakes. Verify this numerically for each pair, as `tests/test_oracle.py::test_stakes_pairs` does.
2. Report non-isolating pairs as a separate subset. There the competitors' own stakes sensitivity, via the changed base action, is genuine and must not be suppressed.
3. A pair should show a **ranking** change, not only a magnitude change. In the current pair, K(alice), K(bob) and R(bob) move together. A ranking-change construction needs one unit whose value comes from averting an error and one whose value comes from saving steps, with equal flip probability. That is TODO.

## Review outcome
_(pending)_
