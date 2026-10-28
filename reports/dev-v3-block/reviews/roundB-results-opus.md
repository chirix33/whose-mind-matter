# Round B results gate: scientific validity (Opus)

Reviewer: Opus 5.5 sub-agent (scientific validity). Date: 2026-10-28. Scope: commit `a040afe`, run `dev-v3-notes-20261028-165208-67f601`.

Inputs read:
- `POST_BLOCK_RESEARCH_DECISIONS.md`: Round B and "Stop and return".
- `experiment-plan.md`: Entry 2, Entry 1a R8–R12 and Entry 1b.
- `roundB-results-local.md/.json`, `roundB-descriptive-local.md`, `roundB-notes-freeze-local.json` and the draft `roundB-summary.md`.
- `scripts/run_dev_v3_notes.py`, `scripts/describe_dev_v3_roundB.py` and `src/vomi/unit_schema.py` (the validator).
- Raw `episodes.jsonl` and `manifest.json`, `data/dev-v3-block/roundB-notes-local.json` and the rendered prompts.
- The API spend ledger, read only.

No model was called and no repo file was changed except this one. My scratch scripts are outside the repo.

## Verdict: PASS WITH REQUIRED CHANGES

Round B ran as pre-registered. The pre-declared R10 reading reproduces exactly from the raw episodes. The draft's overall direction is honest: reference reads "headroom present", inferred reads "inconclusive", and both are called weak, not demonstrated. The summary still needs fixes before it is recorded:
- It contains factual count errors.
- It overstates the 3c mechanism and the inferred-note diagnosis.
- It understates one consistent pattern in 4b.
- It omits several pre-registered measures and one deviation (B2).

None of the changes needs a new LLM run.

## 1. Execution against the pre-registration

**Verified**
- **Selection:** 1c, 2a, 3c and 4b, all 4 variants, giving 16 states. This matches `round_b_selection` in the freeze and the manifest.
- **Freeze order:**
  - Notes stage 16:50:43–16:51:41; proof committed `d5af211` at 16:52:02; the policy run starts 16:52:08 at `git_commit d5af211`, `git_dirty False`.
  - `notes_file_sha256` (sha of the canonical `states` JSON) recomputes to `19377c2c…` and matches the proof and the manifest.
  - The policy stage asserts every rendered MIND NOTES hash before dispatch.
- **Decoding:**
  - Notes: temperature 0, max_tokens 1024, reasoning low.
  - Policy: temperature 1.0, max_tokens 1024, reasoning low, unseeded (the manifest decoding matches).
- **Dispatch:** counterbalanced, with conditions rotated by (state + replicate) at concurrency 4. The manifest records the dispatch order. 192 episodes, 0 blocked.
- **Retention:** fixed allocation, `allocate=False`, no refresh. The graph is retained and units carry `as_of 0` (in `graph_final`).
- **Failure handling:**
  - Policy: 3 failed attempts in total, all `truncated: finish_reason=length` (2 reference, 1 privileged). All recovered on retry; 0 fallbacks. Episodes were scored as played.
  - Notes: failed notes are null and not shown, per R11.
- **R10:** my independent recomputation gives the same d_s, classes and readings for all three conditions.

**Deviations or disclosures missing from the summary**
- **(a) B2 was skipped, which deviates from the pre-registration.** The Entry 2 trigger (≥ USD 1.00 remaining) held, and R12 provided for running under a hard cap and reporting a partial batch. The skip is defensible (see §4), but it must be recorded as a deviation, decided after local outcomes were seen. The arithmetic must be shown.
- **(b) Content-free inferred cells.** In `4b-stakes4-perm0` and `4b-stakes4-perm1` every inferred note failed. The inferred prompt there reads `MIND NOTES: (none instantiated)`.
  - That prompt has no content. It is not byte-identical to `none`, so the pre-declared "adds no new content" definition (byte identity) correctly did not flag it.
  - These 6 episodes are effectively a second no-note arm. That must be disclosed, and it matters for interpretation (§2).
- **(c) Retries at temperature 0 add little.** In every failing note unit, attempts 2 and 3 are byte-identical. At temperature 0 the 3-attempt protocol gives two distinct attempts, not three. This should be disclosed, not changed.
- **(d) Pre-registered measures not reported** (Entry 2 measures; R8):
  - headroom = V* − none per stratum;
  - coverage;
  - the R8 classification of privileged benefit by mechanism.

## 2. Is the draft's interpretation sound?

**Overall framing.** Reporting the pre-declared reading first and then calling it weak and fragile is the right structure. "Weak and fragile, not a demonstrated effect" is the correct bottom line. My recomputation confirms the core claim.
- Removing just the three tail `none` episodes turns the reference reading from "headroom present" to inconclusive: s1 null, s2 inconclusive, s3 inconclusive, s4 null. The three episodes are 4b-s4-p0 r2 (−2.15), 4b-s1-p1 r0 (−0.70) and 3c-s4-p0 r2 (the −0.40 timeout).
- Stratum 3 alone hinges on the timeout. Without it, reference d_s = [−0.017, −0.025, 0.133, 0.100]: the mean is 0.048 and only 2 of 4 are positive.

**Over-stated in places**
- **The median-of-draws sensitivity is not a neutral robustness check.** A median of 3 discards a single error draw by construction. That error tail is the very outcome the ×4 stakes design is meant to measure. Saying the median "reverses" the reading overstates what it shows. The leave-out result above is the more informative statement: without the tail, the reading is inconclusive, not "no headroom".
- **The noise floor is too narrow.**
  - The 1c/3c identical-prompt noise floor (|0.023|, max 0.05) comes from states with almost no error risk. It does not bound noise in error-prone ×4 states.
  - In 4b-s4-p1 the two content-free arms (inferred-empty vs none) differ by **−0.98**. That is the same size as the reference's +1.00 in 4b-s4-p0. The summary should say that in ×4 states a single draw moves a cell mean by about 1.0.
- **"Almost always asks before acting" is too strong.** The first action is an ask in 37, 35, 36 and 32 of 48 episodes (none, inferred, reference, privileged).

**Under-stated in one place.** The only qualitatively consistent pattern is in 4b, and the summary presents it only as fragility.
- Errors occurred in 5/24 episodes of the arms with no correct reliability posterior:
  - none: 2/12;
  - inferred: 3/12. Two of those were in cells with no note. The third followed the prior-copied R(zane) note.
- Reference and privileged had 0/24 errors.
- In 4b, asking is uninformative: every answer repeats the person's t0 statement. So the only lever is the reliability computation, and the reference posterior uses only disclosed rates.
- This is suggestive of a *computation-aid* effect. It is post-hoc, from one group with one shared hidden draw (X is honest in every variant), and the draws are nested.
- It should be stated both ways: suggestive, and not demonstrated.
- 2a is a counterexample worth including. In 2a-s1-p0 r2 the reference policy asked H, then gave the package to N. Its reasoning: "they would forward to office_c". The note on screen said N's belief is correct now with probability 0.00. So notes did not prevent a perspective error there.

**The 3c mechanism paragraph is not justified as written.** I checked all 48 3c episodes.
- **"Often" is wrong.** Only 3 of 12 `none` episodes walked to F's own (new) office.
  - Their returns were 0.65, 0.65 and −0.40 (timeout, looping hall↔office_a).
  - 7 of 12 asked F first. The 0.80 returns are ask-then-correct-walk, not wrong-office visits. "Costs 0.65–0.80" is therefore wrong.
- **What the notes changed.** Inferred, reference and privileged had 0 of 12 wrong-office visits each.
- **"The depth-2 inference the direct policy skipped" is an overclaim.** The error is a perspective confusion: F's own belief, learned by asking, was taken as R's location. In 3c the actionable content of K(F→R) equals R's own stale belief, and therefore R's location.
  - A depth-1 K(R) note would license the same walk to R's office. That walk is the most common route in the note arms.
  - The depth-2-specific action give(F) rose from 2/12 to 5/12 (reference and inferred alike).
  - There is no K(R) control, and 3c is not the depth-certification pair: R3 certifies with 3a/3b, which are not in Round B.
  - Legitimacy ("evidence-resolved under r6, not a leak") holds, given the stipulated rules (RC3c).

## 3. The 4b inferred-note failures

The validator diagnosis is supported, but the summary gets the counts wrong and the diagnosis is incomplete.

- **Counts.**
  - **5 of 24** notes failed, not 6: 4b-s1-p0 R(uma), 4b-s4-p0 R(kim) and R(uma), and 4b-s4-p1 R(uma) and R(zane). The freeze proof `inferred_ok` and the fidelity table both show 5.
  - So 19 notes are valid, not 18.
  - There are **three** valid 4b notes, not two. R(kim) in s1-p0 is correct_supported but is a prior copy (0.98). R(uma) in s1-p1 is correct_supported. R(zane) in s1-p1 is unsupported_committed.
- **Cause.**
  - All 15 failed attempts cite an invented ID `PUBLIC_MODEL`/`public_model` with `kind: public_rule`. That triggers both `cites_non_visible_evidence` and `rule_citation_mismatch` (`unit_schema.py` L178–181).
  - The same prior rates *were* citable. The two valid prior-rate 4b notes cite `RULE6` and pass, and r6 rule 6 points to the public model.
  - Correct statement: the public-model block has no ID of its own, the unit prompt lists only history IDs and RULE1–RULE6, and the model sometimes invents one. It is not true that the numbers cannot be cited.
- **The bigger content problem is missing from the summary.** Fixing the interface would not have produced good 4b notes.
  - In 6 of 8 4b units the final output copies the disclosed prior: X cooperative 0.98, Y cooperative 0.70. It does not condition on the disagreement. The reference posteriors are X 0.945 and Y 0.045.
  - All four Y-unit final outputs say Y is cooperative with probability 0.70.
  - Only two attempts (both R(uma)) tried a likelihood update. Neither was the frozen output for its unit.
  - The single inferred error with a note shown (4b-s1-p1 r2, −0.70) follows the policy's reasoning from the note's "zane cooperative 0.7" to dropping on zane's report.
  - So "their main measured problem is a pipeline gap" is wrong. There are two problems: the interface gap, and failure to condition reliability on conflicting reports.

## 4. B2 skip

The skip is consistent with the ruling:
- The ruling's clause reads "only if its worst-case reservation fits the remaining … cap", and "if the API check cannot fit, finish the free/local diagnostic and report the missing API confirmation".
- Input alone is about 64 × 3.1 × 1,490 ≈ 0.30M tokens, or about USD 0.59 at USD 2/Mtok.
- The worst-case reservations at R12's max_output values far exceed the USD 1.13 that remains: about 198 × 2,000 × USD 10/M ≈ USD 3.96 for policy, plus the notes.
- Running a reduced or alternative API variant after the local results would also break "do not select a new variant after seeing these results".

It is still a departure from R12's partial-run provision, decided after outcomes on cost grounds alone. It must be logged as a deviation, with the token and price assumptions shown, especially for output and reasoning tokens. The ledger reads USD 3.86895, 0 reserved and 0 unresolved, last written 09:11. That is consistent with "no paid calls".

## 5. Recommendation for the block

**Not allocation learning.** Allocation learning would need two things, and neither holds:
- (i) a deployable inferred note that approximates the reference content. Here 5 of 24 notes are invalid and the 4b reliability notes copy the prior.
- (ii) a reference-note value measured with useful precision. Here the reading is tail-driven, and it is inconclusive without three episodes.

The ruling also forbids starting allocation learning automatically.

**Recommend further inference/integration work, plus a reconsideration of how headroom is measured.** Return both to research review.
- **(a) Fix the public-model citation interface.** Either give the block an ID or document RULE6 as its citation. This is a package change and needs review.
- **(b) Check reliability conditioning symbolically first.** Test whether the inference step can produce posterior rather than prior-copied reliability under disclosed rates. Check it against the reference posterior before any policy calls.
- **(c) Separate the two parts of the headroom.**
  - The local policy's gap to V* is 0.06, 0.32, 0.24 and 0.41 by stratum (V* = 0.95, 0.95, 0.95, 0.856). It is mostly over-asking, which no note condition reduced: privileged picks a Bayes-optimal first action in 3 of 48 episodes.
  - Explicit notes can only address the rare-error part.
  - Measuring that part needs many more draws and fresh hidden draws per group. Locally this is cheap: 192 episodes took 139 s.
  - Its power and design are for research review, not this block.

## Required changes (summary and/or report; no new LLM runs)

1. **Fix counts.** 5/24 inferred notes failed (not 6), 19 are valid (not 18), and there are three valid 4b notes. Name their categories, and say that R(kim) in s1-p0 is a prior copy. Fix this in "Pipeline finding" and in "Conclusion".
2. **Correct the 4b cause.** Failed attempts cite an invented `PUBLIC_MODEL` ID; `RULE6` citations of the same rates passed. The gap is "no ID for the public-model block, and the model invents one", not "uncitable". Also disclose that temperature-0 attempts 2 and 3 were byte-identical in every failing unit.
3. **Add the 4b content finding.**
   - 6 of 8 final 4b outputs copy the prior, and all 4 Y units say cooperative 0.70 against a posterior of 0.045.
   - Link the 4b-s1-p1 r2 error to the R(zane) 0.70 note, using its reasoning.
   - Replace "main measured problem is a pipeline gap" with the two-problem statement.
4. **Disclose the content-free inferred cells.**
   - In 4b-s4-p0 and 4b-s4-p1 the prompt reads "(none instantiated)", which is effectively a second no-note arm.
   - Report its difference from `none`: 0.00 and −0.98.
   - Qualify the noise-floor bullet: the 1c/3c floor does not cover error-prone ×4 states, where one draw moves a cell mean by about 1.0.
5. **Rewrite the 3c paragraph** with the counts in §2:
   - 3/12 wrong-office visits under `none` (returns 0.65, 0.65, −0.40), against 0/12 in each note arm;
   - give(F) 2/12 → 5/12.
   - Call it consistent with the note correcting a perspective confusion. The usable content equals R's own belief, which a depth-1 note would also supply. There is no K(R) control and 3c is not the certification pair, so it is not evidence specific to depth 2.
   - Remove "often" and "0.65–0.80".
6. **Reframe the fragility evidence.**
   - Label the median-of-3 analysis as tail-discarding by construction.
   - Add the leave-out result: dropping the 3 tail `none` episodes makes the reference reading inconclusive, and stratum 3 alone depends on the timeout.
   - Add the 4b pattern as a post-hoc, single-group, single-hidden-draw observation: 5/24 errors without a correct reliability posterior, against 0/24 with one.
   - Add the 2a reference counterexample.
7. **Report the missing pre-registered measures.**
   - Headroom V* − none per stratum: 0.06, 0.32, 0.24, 0.41.
   - Coverage: 19/24 focal units have a valid inferred note; computed notes have 24/24.
   - R8 privileged mechanism classification:
     - 2a: target leakage, since the true K(H) content is R's office;
     - 4b: true intent identifies the true report, which is effectively target leakage;
     - 1c and 3c: identical to reference, so no privileged-specific benefit.
   - Policy attempt failures: 3 truncated attempts, all recovered, 0 fallbacks.
8. **Record B2 as a deviation from Entry 2/R12.** It was decided after local outcomes, on cost grounds, under the ruling's worst-case clause. Show the estimate's arithmetic and the worst-case reservation, and state that no substitute API variant was run.
9. **Fix "almost always asks before acting"** to "first action is an ask in 32–37 of 48 episodes per condition".
10. **Add the block recommendation in §5 to the summary:** not allocation learning; inference/integration work first; a re-measurement design for the error-tail headroom goes to research review.

## Optional

- Report unsupported mass next to the fidelity category.
  - The inferred K(yara) note in 2a-s1-p0 puts 0.33 on office_b, which has posterior 0. It also splits office_c and office_a 0.50/0.17 with no evidence, yet it is scored correct_supported.
  - All four 2a inferred top values equal the truth (office_c) under a 50/50 posterior. Note this as chance: temperature 0 and correlated variants.
- Say that retained notes appear as "stale" after step 0. The graph status becomes stale. This is symmetric across conditions under R9, but it affects how notes are read in multi-step episodes.
- Rendering rounding: reference R(uma) shows cooperative 0.04 and obstructive 0.95, which sums to 0.99.
- Where the inferred content was correct (3c), the inferred arm behaved like reference: 0 wrong-office visits and give(F) in 5/12. That is worth one sentence, so that "inferred shows no reliable value" is not read as "inferred notes never help".
- In 4b all variants share one hidden draw in which X is honest. Realized returns therefore reward "trust X", while the ×4 Bayes action is to walk. State this when comparing to V*.
