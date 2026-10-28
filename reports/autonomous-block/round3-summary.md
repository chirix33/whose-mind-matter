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
  - By stratum vs. reference:
    - K(recipient) (where doubt contradicts rule 2): −0.021;
    - other: −0.050;
    - s1, the twin of s9: +0.012 (the doubt prompt did not add a costly check there).
- **Replication of Round 2:** none − reference per state reproduces Round 2 closely (s2 −0.10/−0.10, s4 −0.125/−0.10, s5 +0.075/+0.083, s6 −0.15/−0.133; ties elsewhere). All non-s9 states succeed 4/4 in both conditions.

## Conclusion (amended mapping)
**Generic caution cue; s9 is a risk-calibration failure.**
- The API policy reliably drops the package on possibly stale testimony at s9: 0/14 across rounds.
- Its mental-state notes, including the true content, do not change that. Expressing 0.2 doubt about the informant does (10/11), at a small cost relative to the base-rate-informed reference notes, and at no net cost relative to no notes in the other 8 states.
- This is **not** evidence of value from mental-state content. The doubt mass is not supported by the reference model, and the true content did not help.
- It is a cheap presentation that corrects a policy calibration error in one state. As a method it would need a fair test: the same caution available to the direct baseline, on held-out states.

## Limitations
- One state carries H3a/H3b; 4–8 draws per cell.
- s9 was selected after seeing Round 2, so the s9 tests are replication, not discovery, and Round 2 draws are not pooled.
- H3c rests on 8 states × 4 draws, and its margin over the threshold is small (−0.031 vs. −0.025).
- All results are exploratory, on inspected development data.
