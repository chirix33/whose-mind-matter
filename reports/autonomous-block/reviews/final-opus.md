# Final gate: Opus 5.5 scientific-validity review (Round 3 results + FINAL_REVIEW)

- **Reviewer:** sub-agent, model opus (Opus 5.5). Read-only; it made no API calls.
- **Commit reviewed:** `8250247`.

## Part A: Round 3. PASS WITH REQUIRED CHANGES (applied to round3-summary.md)
Every number reproduced from the raw episodes, and the s1/s9 rendered hashes are identical. H3a, H3b and H3c are evaluated exactly to the amended thresholds.
1. **H3c depends on confounded comparators.** s6 is a base-rate state and s4 is the list-order state. Excluding s6 gives −0.021, which fails the threshold. → Disclosed as fragile.
2. **"No net cost vs. none" overstates.** +0.000 nets caution costs at s1/s3/s5 against inherited reference gains at s2/s4/s6. → Reworded.
3. **Keep avoiding a 9-state net figure.** → Kept.
4. **The risk-calibration label needs the reference P(unmoved).** → Computed by enumerating the prior worlds consistent with the visible history including the answer: **0.70 at both s9 and s1**, against thresholds 0.929 and 0.966. Stated, with its dependence on the generator's undisclosed moving base rate.

## Part B: FINAL_REVIEW. PASS WITH REQUIRED CHANGES (applied)
- The recommendation comes first, does not pivot, and is faithful to the gated conclusions; length is fine.
- Required changes:
  - wording at the s9 claims (7/8 pre-registered vs. 10/11 descriptive; "true-content note only repeated the answer"; "consistent with a caution cue");
  - "by realized outcome", with s1;
  - the stated P(unmoved);
  - the next-milestone design grounded in outline factors F1/F2/F4/F5, with pre-registered proportions including STOP and distractor controls, content inferable from the visible history, identical caution text across arms, "costly ask" removed (it would be a reward change), and K(recipient) separately labelled, not excluded;
  - added decisions (out-of-sample context definition; labels accounting for asks; honesty and moving rates in reference semantics);
  - added limitations (a single API policy; the H3c confound);
  - an accurate gate description and review count;
  - a commands and test outcomes section;
  - an ambiguous-context example;
  - corrected source-archive wording.
