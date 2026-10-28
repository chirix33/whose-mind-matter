# Round 3 summary: replication and matched doubt control (development data; exploratory)

**Full tables:** `round3-results.md`, from `scripts/report_round3.py`, which implements the amended pre-registration.

**Run:** `notes-value-20261028-090725-c312fa`, at clean commit `578fb6f`.
- The frozen proof `round3-notes-freeze.json` was committed before dispatch, and every injected hash was checked.
- 112 episodes, none blocked, 0 failed attempts.
- **Policy spend:** USD 0.9130 (from tokens). Ledger total USD 3.8690 of 5.00, so USD 1.1311 remains.

## Pre-registered tests (thresholds fixed before outputs)
- **H3a, replication: holds.**
  - At s9, none fails 0/4 and reference fails 0/4. The doubt-carrying prompt (reference_doubt and inferred_bare are byte-identical at s9) succeeds **7/8**.
  - Round 2 is not pooled. Shown alongside: none 0/3, reference 0/3, inferred_bare 3/3.
  - Combined, descriptive only: 0/14 without doubt against 10/11 with it.
  - Every successful episode asks Dave, then checks lab_north, then lab_south, then delivers.
- **H3b, doubt: holds.** Pooled 7/8 ≥ 6/8, with reference ≤ 1/4. At s9 this prompt differs from the reference note only by 0.2 mass on `unknown` (and the 0.5 → 0.4 scaling).
- **H3c, cost: holds narrowly.**
  - In the 8 other states, the mean of reference_doubt − reference is −0.031: 3 states negative (s3 −0.10, s6 −0.10, s4 −0.06), 1 positive (s1 +0.01), 4 at 0.
  - **Against `none` the 8-state mean is +0.000.**
  - Doubt costs extra steps where the reference note let the policy act directly: s3 1.00 → 3.00 steps, s6 2.00 → 4.00.
  - **Fragile.** Two of the three negative states are confounded comparators: at s6 the reference uses undisclosed base rates, and s4 is the list-order artifact state.
    - Excluding s6 alone gives −0.021, which is above the threshold. Excluding s4 and s6 gives −0.015.
    - In Round 3 the reference itself beats `none` at s2 (+0.10), s4 (+0.125) and s6 (+0.15). Doubt keeps the s2 gain, gives back about half at s4 and about two-thirds at s6.
    - So the measured cost is partly doubt undoing reference gains that come from generator knowledge or list order.
  - The "first action differs from the modal reference action" column is tie-sensitive at s6: the reference first actions split 2 drop(room_7) / 2 move(hall). All 4 doubt episodes start with move(hall).
  - By stratum vs. reference:
    - K(recipient) (where doubt contradicts rule 2): −0.021;
    - other: −0.050;
    - s1, the twin of s9: +0.012 (the doubt prompt did not add a costly check there).
- **Replication of Round 2:** none − reference per state reproduces Round 2 closely (s2 −0.10/−0.10, s4 −0.125/−0.10, s5 +0.075/+0.083, s6 −0.15/−0.133; ties elsewhere). All non-s9 states succeed 4/4 in both conditions.

## Conclusion (amended mapping)
**Consistent with a generic caution cue; s9 is a risk-calibration failure.**
- **The risk is real under the reference model.** Given everything the robot saw, including Dave's answer, P(recipient still at the stated room) = **0.70**, at both s9 and its twin s1. Dropping is optimal only above 0.929 (s9, ×1 stakes) or 0.966 (s1, ×4 stakes). This rests on the generator's undisclosed base rate for moving (0.3); the public rules say only that beliefs can be outdated.
- The API policy nevertheless drops on that possibly stale testimony at s9: none 0/7 and reference 0/7 across rounds.
- The true-content note only repeated the answer the policy had already heard, and did not change this.
- A note expressing 0.2 doubt about the informant did: **7/8 in the pre-registered Round 3 replication**, and 10/11 descriptively when the Round 2 draws that motivated the test are included.
- **Elsewhere:** in the other 8 states its mean vs. no notes is +0.000. That nets caution costs at s1, s3 and s5 (−0.04 / −0.10 / −0.075) against gains inherited from the reference at s2, s4 and s6. Against the reference the cost is −0.031, which is fragile (see H3c).
- No 9-state net figure is claimed: +0.081 vs. reference and +0.108 vs. none would both be dominated by s9.
- This is **not** evidence of value from mental-state content. The doubt mass is not supported by the reference model, and the true content did not help.
- It is a cheap presentation that corrects a policy calibration error in one state. As a method it would need a fair test: the same caution available to the direct baseline, on held-out states.

## Limitations
- One state carries H3a/H3b; 4–8 draws per cell.
- s9 was selected after seeing Round 2, so the s9 tests are replication, not discovery, and Round 2 draws are not pooled.
- H3c rests on 8 states × 4 draws, and its margin over the threshold is small (−0.031 vs. −0.025). It fails if s6 (a confounded comparator) is excluded.
- One API policy only (gpt-6.1-sol, low effort). These findings do not transfer to the local policy, where the earlier pilot found that notes reduced return.
- All results are exploratory, on inspected development data.
