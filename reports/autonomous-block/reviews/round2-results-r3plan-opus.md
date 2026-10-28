# Round 2 results gate and Round 3 plan gate: Opus 5.5

- **Reviewer:** sub-agent, model opus (Opus 5.5).
- **Method:** read-only; no API calls. Payloads were rendered in memory only.
- **Commit reviewed:** `046907d`.

## Part A: Round 2 conclusions. PASS WITH REQUIRED CHANGES (all applied to round2-summary.md)
1. **Withdraw "integration-limited at s9".** All 15 s9 episodes asked Dave and heard 'lab_north', so the privileged note repeated information the policy already had; false-belief integration was untested. After the ask, dropping is optimal only if P > 0.929, so this is a risk-calibration failure present in every condition.
2. **Headroom is judged by realized outcome.** s1 is the public twin of s9: `none` dropped in 2/3 draws at ×4 stakes (optimal only if P > 0.966) and succeeded because Quinn had not moved.
3. **The doubt mechanism is weaker than stated.** At s1 the reference (0.5/0.5) produced verification in 3/3 draws, and inferred 1/3 vs. inferred_bare 3/3 at s9 is within noise. Soften the presentation claim.
4. **'Privileged reveals target' applies to true-belief content in 8 of 9 states**, not only K(recipient). It was used fully at s2, s4 and s5, partly at s6 and s1, and hurt at s8.
5. **s4 list-order artifact.** Note conditions went to office_a (listed first, and the truth) first; `none` went to office_b first. So stratum C is not a clean null. *(Verified by the main session from the traces.)*
6. **Wording:** the 0.2 unknown is 'not supported by the reference', and is defensible under rules 4 and 6.
7. **Mechanism behind the near-zero 'useful' labels.** The unit's person is present and can be asked, so the note is worth at most one 0.05 step.

## Part B: Round 3 plan. PASS WITH REQUIRED CHANGES (all applied in the plan amendment)
- Replication plus one matched control is the right single action. An integration variant is premature. Not pooling Round 2 draws is correct. The budget is fine: $2.0441 remains, capped at $1.20.
1. Plan and code disagreed on status → the code is kept (copy the reference status) and the threshold departure is disclosed.
2. reference_doubt is byte-identical to inferred_bare at s1 and s9 → Round 3 at s9 is a replication; the two cells are pooled as one 8-draw arm; the '0.4 vs. 0.5' branch is deleted.
3. Fix the outcome mapping: no 'integration-limited' outcome.
4. Thresholds fully defined (≤ 1/4 or ≤ 2/8 for failure; intermediate results inconclusive; H3c requires ≤ −0.025 and negative > positive states), and H3c also reported against `none`.
5. Stratify H3c into {s2, s4, s5} (K(recipient); doubt contradicts rule 2), {s3, s6, s7, s8}, and s1 on its own.
