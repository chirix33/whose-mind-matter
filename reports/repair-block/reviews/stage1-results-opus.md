# Stage 1 results gate — scientific-validity review (Opus 5.5)

Date: 2026-10-29. Reviewer: Opus 5.5 (scientific validity). Read-only review; no model calls; no repo files changed except this one.
Inputs: `experiment-plan.md` Entries 1, 1a, 1b, 2; commits 4367795, ec2e8d3; `stage1-regress-20261028-234117.json`; `data/repair-block/regress-20261028-234117.json` (privileged rows, attempts included); `scripts/run_repair.py`; `scripts/report_repair_stage2.py`; `src/vomi/pilot.py` (usage aggregation); `src/vomi/unit_schema.py`; `src/officeminds/devgen3.py` (rate keys); `reviews/stage1-results-sonnet.md`.

**Verdict: PASS WITH REQUIRED CHANGES** (R1–R3). All three are reporting or freeze-integrity code changes. None changes the prompt, example, decoding, retries or the validator's acceptance set, and none needs new model output. After they are committed and the tree is clean, `run_repair.py freeze` may run and Stage 2 may begin.

## 1. Entry 1b implementation

- **S1 and S2 (prompt).** Done in 4367795 (23:41:11). The new warehouse example is 0.75/0.25 with one clerk at 0.35, giving 0.62 up, 0.15 down, and the prior again at equal shelf priors. It has no 1/3 and no dev-v3 value. The conditioning-correct wording replaces the "PRIOR before anything" sentence. `test_v22_worked_example_numbers_and_no_dev_v3_values` checks this with `fractions`.
- **S3 (unit order).** Done: `matched_notes_text` sorts by unit label.
- **S4 (power limitations).** Done in `power.md`. The figures match Entry 1b: MDE ≈ 0.109 (B) / 0.07 (A); K ≈ 102 / 46 for the null class; K ≈ 28 for "helps" under B; P(unresolved \| null) 0.71 (B) / 0.45 (A). The table row gives 0.71, while Entry 1b's text says 0.72. This is a rounding difference only.
- **S5.** Done. The anomaly has precedence and maps to "mechanism check; no §5(1)".
- **S6.** Done. Category counts per construction and the privileged per-note rows are written, and 4c reports a prior match as correct, with over-updates counted separately.
- **S7.** Done (`depth_diffs`).
- **S8.** Done. The base scenario value is the mean over available episodes, a scenario is excluded per contrast, and the exclusion lists are written.
- **S9.** Partial; see **R2**.
  - Notes: the report counts attempts with missing usage and attempts with unavailable reasoning tokens.
  - Decisions: `CallRecord.usage()` sums only the non-None tokens, and the episode usage has no count of missing usage, so a missing decision count would silently become 0.
  - Wall clocks, concurrency and the oracle's CPU time are reported.
- **S10.** Satisfied by construction: the ×1 and ×4 variants are separate state IDs, so each gets its own note draw.
- Every RC1–RC14 item is reflected in the code that I traced. No RC item is open apart from R2's S9 residue.

## 2. Regression check

**Executed as pre-registered.**
- It used only the 16 inspected Round B states (1c, 2a, 3c, 4b): 24 focal notes plus 4 K(R) notes. This is development material.
- There is one run (tag 234117). It started after commit 4367795, and its recorded prompt sha `dc169d02…` equals the committed `unit_system.txt`.
- Decoding was T = 1.0, max_tokens 2048 and reasoning low, as registered.
- There was no second run and no RC11 fix, and no content threshold was applied. Sonnet recomputed the numbers independently (CONSISTENT).

**The validator rejections are genuine model errors, not plumbing.** I checked every rejected attempt:
- `rule_citation_mismatch`: the support item uses kind `public_rule` with a history ID (`t0:note0`).
- `cites_non_visible_evidence` and `public_model_citation_mismatch`: the model wrote bracketed IDs (`[t0:note0]`, `[PM7]`).
- `probabilities_not_normalized`: the probabilities summed to 0.299 + 0.045.

Each of these is a correct rejection under the registered acceptance set ("exact ID; kind must match"). Accepting the bracketed form would widen the acceptance set, which RC11 forbids. Every rejection was recovered within 3 attempts (coverage 28/28), and no output was truncated. No RC11 fix is warranted.

**The 4 `unsupported_committed` notes are genuine inference failures:**
- 2a ×4 perm0, K(yara): the note says office_b with p = 1.0, but the posterior is office_a/office_c at 0.5 each and puts 0 on office_b. The holder is credited with the announced value she could not have received, which is perspective leakage. The other three 2a holder notes are correct 0.5/0.5 splits.
- 4b Y units (prior obstructive 0.3, posterior 0.955):
  - perm0 ×1 R(uma) = 0.7/0.3 and perm1 ×1 R(zane) = 0.7/0.3 are exact prior copies;
  - perm0 ×4 R(uma) = 0.824/0.176 moves away from the posterior;
  - the fourth Y note (perm1 ×4 R(zane) = 0.894 obstructive) is correct.

  So the S1/S2 revision did not reliably produce the conflicting-statement update in 4b. This is a substantive weakness of inference, not a defect of the gate. It is exactly what the inferred arm of Stage 2 is meant to measure, and RC11 forbids iterating on it.

**The prior-copy metric needs a disclosed refinement (R1).**
- For the 4b X units, the prior is 0.02, the posterior is 0.055, and the tolerance is ±0.02. The "prior copy" window [0, 0.04] lies within 0.055 TV of the correct answer, so the metric cannot separate copying from correct inference.
- It also counts a 1.0/0.0 note (perm1 ×4 R(uma)) as a "prior copy", which is Sonnet's remark.
- Three of the five reported copies are such X-unit coincidences.
- On the discriminating units (the Y units, |posterior − prior| = 0.655), the rate is **2/4 exact prior copies, 1/4 wrong-direction, 1/4 correct**.
- The raw "5/8" should be kept but annotated.

**Stage 2 disclosure.** These single T = 1.0 draws are not evidence that prior-copying was fixed or not fixed (RC11). They do suggest, without confirming, that Stage 2 may land in the "inference fails" or "unresolved" cell for the inferred arm. That is a pre-declared, informative outcome and no reason to block.

## 3. Required changes (before `freeze`)

- **R1 — prior-copy refinement (reporting only).**
  - In `report_repair_stage2.py` (fidelity summary) and in the Stage 1 summary text (checkpoint or `latest.md`), mark a reliability note's prior-copy test as *discriminating* only when the reference posterior's p(obstructive) differs from the disclosed prior by more than 2 × tolerance (> 0.04). Report three things: (a) the raw count, unchanged; (b) prior copies among the discriminating units; (c) the number of non-discriminating units.
  - Keep `prior_copy` itself unchanged.
  - Record the Stage 1 refined figure: 2/4 discriminating (Y units); 3 of the raw 5 are non-discriminating X units, one of them a 1.0/0.0 note.
  - State that the refinement was defined after viewing Stage 1 output and before any Stage 2 output.
- **R2 — S9 for decision calls.**
  - Count the decision attempts whose `prompt_tokens` or `completion_tokens` are None. For example, add `usage_missing_attempts` to the per-kind usage aggregation in `pilot.run_episode_arm`, or derive it in the report if the episode records carry attempts.
  - Report it per condition next to `decision_prompt_tokens`, so that a missing decision count is not silently 0.
- **R3 — freeze integrity.**
  - Add `configs/models/local_gpt_oss_20b.json` to `FROZEN_SOURCES`. `decoding()` and `hf_snapshot` are read from it at run time, and `verify()` currently does not detect a change to it.
  - Make `verify()` also check that `power.json` and `stage2-qualification.json` still match `power_sha256` and `qualification_sha256`, and that `decoding("notes")` and `decoding("policy")` equal the frozen values.

## 4. Optional

- **O1.** Guard `stage_notes` the same way as `stage_policy`: require a clean tree with `stage1-freeze.json` tracked. This makes "freeze committed before any Stage 2 output" machine-checked.
- **O2.** `sign_flip_p` tests the pooled unweighted mean, while `estimate` is the construction-weighted mean. These are identical when the design is balanced with no exclusions. Either state this, or flip on the construction-weighted statistic.
- **O3.** Add `src/vomi/runlog.py` to `FROZEN_SOURCES`.
- **O4.** In Stage 2 compute, also tabulate rejections by validation-error type. Bracketed IDs and kind mismatches are a recurring source of retry cost.
- **O5.** A truncation is recorded as `request_error`, and the `error` text still says "truncated". Report truncations as a separate count.

## 5. Reasoning

- The pre-output revision (S1–S10) was applied before the only v2.2 call.
- The regression check ran once, on development material, without iteration or threshold, and its rejections reflect the registered validator.
- The observed failures (one leakage note, three Y-unit misses) are honest content results that Stage 2 is designed to measure. They are not grounds for further prompt work inside this block.
- The required changes protect the interpretation of a fidelity metric, the pre-registered compute accounting, and the guarantee that the frozen configuration is what actually runs. All are cheap and need no model output.
