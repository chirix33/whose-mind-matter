# Stage 1 prompt / package gate (scientific validity): pilot-v2.2, r7 renderer, K, Stage 2 scripts

Reviewer: Opus (Stage 1 prompt gate, RC10). Date: 2026-10-28. HEAD `9b0c38d`, clean tree apart from the untracked `reports/repair-block/checkpoint.md`. No regression output exists yet. I made no model calls.

Inputs:
- `prompts/pilot-v2.2/unit_system.txt`, diffed against `prompts/pilot-v2.1/unit_system.txt`;
- `src/vomi/pilot.py`: `numbered_public_model`, `task_card`, `matched_notes_text`, `unit_messages`, `run_episode_arm`;
- `src/vomi/unit_schema.py`: `validate_unit_output_v22`;
- `src/vomi/graph.py`: `advance`, `policy_view`;
- `src/officeminds/devgen3.py`: `hidden_vars`, `process_text`, `focal_units`, `roles_for`;
- `tests/test_repair_stage1.py`;
- `scripts/power_repair_stage2.py`, `reports/repair-block/power.{md,json}`;
- `scripts/run_repair.py`, `scripts/report_repair_stage2.py`;
- `reports/repair-block/experiment-plan.md` (Entries 1, 2, 1a), `reviews/plan-opus.md`, `stage2-qualification.json`.

Commands I ran (read-only):
- `pytest tests/test_repair_stage1.py`: 6 passed.
- A scratch script that rendered r7 cards and reference notes for one ×1/perm0 instance of each of 1b, 2a, 2b, 3a, 3b, 3c, 4a, 4b and 4c at fresh seed 20261100. For each one it also rendered an "inferred" payload with the same distribution, in reversed value order, with citations, `unresolved`, a wrong `about` and a different model status. All 9 renders were byte-identical to the reference.

## Verdict: PASS WITH REQUIRED CHANGES (S1–S10)

The plumbing is sound and conforms to Entry 1a:
- PM IDs: stable and sequential, with the hidden-quantity sub-lines included.
- Validator v22: accepts this card's `PM<n>` with kind `public_model`. It rejects `PUBLIC_MODEL`, `PM99` and kind mismatches in both directions, and it keeps `RULE<n>`/`public_rule` unchanged.
- Matched renderer: RC7–RC9 hold:
  - canonical value order;
  - duplicates summed;
  - 2 dp, with values below 0.005 omitted;
  - the confidence rule applied to the unrounded mass;
  - unit label and `about` taken from the unit definition;
  - the constant reminder in the header;
  - confidence wording about the robot's estimate of the person's belief or intent;
  - an abstained output shows its distribution and banner, with no confidence line;
  - graph statuses depend only on the history and the path, so they are source-independent.
- Power script and K choice: they follow RC2/RC3/RC5. **K = 24 is the correct choice under the pre-declared rule.** No K in the grid meets the criterion, and 24 is the largest feasible K in the grid (8 min per seed × 24 = 192 min ≤ 240).
- Prompt arithmetic: correct. The example uses no dev-v3 rate or posterior value, and it includes a no-update case.

Required changes come in two groups:
- **Two are scientific, in the prompt (S1, S2).** They must be fixed before the first v2.2 call, which RC10 allows because no v2.2 output exists. Each is fixed by a dated Entry 1b amendment that supersedes the example text pre-registered in Entry 1a RC10.
- **One is scientific, in the renderer (S3).**
- **The rest are pre-freeze conformity and disclosure items in the power report and the analysis script (S4–S10).**

## What I checked and found correct

- **Prompt diff.** v2.2 is v2.1 plus one section placed before the final line, and the test enforces this. The "no belief / robot unsure / abstain" distinction is unchanged verbatim. The section contains no construction name, hidden label or dev-v3 number.
- **Example 1 arithmetic** (two agreeing clerks, prior 0.35):

  | Combination | Weight |
  |---|---|
  | Box on shelf_1, both clerks truthful | 1/3·0.65² = 0.1408 |
  | Box on shelf_2, both misreport toward shelf_1 | 1/3·(0.35·½)² = 0.01021 |
  | Box on shelf_3, both misreport toward shelf_1 | 0.01021 |
  | Total | 0.16125 |

  P(Ana misreports) = 0.02042/0.16125 = 0.127, which the prompt gives as 0.13 (cooperative 0.87). Mixed truthful/misreporting combinations are correctly excluded.
- **No-update case.** With a uniform location prior and a uniform lie, the 0.65 : 0.35 ratio is preserved. The case is correct and gives the right reason.
- **Direction.** The example shows a downward move of obstruction and a no-move. It shows no upward move, and the closing sentence "do the calculation rather than assume a direction" is neutral. The example does not by itself push 4b toward a specific answer. Its problem is structural (S1).
- **r7 cards.** PM IDs appear in every card, `none` included, as disclosed. RULE1–6 text is unchanged. The 4b card shows the two rates on separate PM lines, and the reference renders R notes of 0.94/0.06 and 0.04/0.96 (seed 20261100: rates 0.03 and 0.4).
- **2a stale courier.** The reference K(N) renders as `lab_west: 1.00` with "robot's confidence in this estimate of omar's belief: high (one value has probability at least 0.8)". The header says "a person's belief can itself be false or outdated". The RC8 hazard ("grounded" read as true) is removed.
- **RC13 premise confirmed by rendering.** In 3a and 3c, K(F→R) and K(R) have identical reference distributions (3a: uniform over two offices; 3c: one office with p = 1). In 3b they differ (K(F→R) has one office with p = 1; K(R) is uniform over the other two).
- **Stage 2 states and qualification.** 576 states (24 seeds × 12 constructions × ×1/×4, perm0) all pass. The seeds 2026110x/2026111x appear nowhere outside the repair-block files.
- **Analysis script.**
  - Holm logic: correct (the smaller p is tested at 0.025; the larger at 0.05 only if the first is rejected).
  - RC4 classes and the 9-cell table: correct.
  - Bootstrap: stratified by construction, with an equal-construction-weight estimate (RC6).
  - Per-stratum secondary contrasts with CIs: present, stratum 1 included.
  - Depth: the K(F→R) − K(R) contrast is computed per stratum-3 construction, and the 3b−3a difference-in-differences is computed per seed.
  - Compute: note attempts are charged to the inferred conditions, failed and truncated attempts included.
- **Runner.**
  - The freeze needs a clean tree and hashes every listed source.
  - `notes` refuses to regenerate frozen notes.
  - `policy` verifies the notes hash and every rendered-notes hash before any call.
  - Policy runs in complete seed blocks; blocks are counterbalanced by condition rotation, and errors are recorded rather than retried.

## Required changes

**S1 — The worked example is isomorphic to 4b in hypothesis space and to 4c exactly. Replace it before any v2.2 call.**
- **The two-clerk case.** It uses 4b's hypothesis space exactly:
  - three locations with a uniform prior;
  - two reporters, each misreporting independently with a disclosed rate;
  - a misreporter names one of the two wrong values uniformly.

  It differs from 4b only in the observation (agreeing rather than differing statements). Solving 4b then requires only swapping the observed statements into a solved template.
- **The "only Ana spoke" no-update case.** It is 4c's structure exactly: one reporter, three values with a uniform prior, and a uniform lie over the two others, giving posterior = prior. It hands over 4c's answer pattern directly.

RC10(b) excluded 4b's structure precisely to avoid this. With the current text, the stratum-4 inferred fidelity and inferred − none would measure template transfer, not the generic prior-vs-posterior revision that D-015 Q1 authorizes. That would also undercut later use of the package outside dev-v3.

Replace the example with one whose hypothesis space matches neither 4b nor 4c. It must differ in at least the number of values and the number of sources, or in the error model. Keep:
- (a) one update case;
- (b) one no-update case;
- (c) no dev-v3 value (0.02, 0.03, 0.3, 0.4, 0.05, 0.06, 0.94–0.96; also avoid 1/3 priors over three values);
- (d) a short committed test that recomputes the example's numbers with `fractions` and checks that the forbidden values are absent.

One compliant option, which I verified:
- Setting: two shelves; box on shelf_1 with prior 0.75 and on shelf_2 with 0.25; one clerk who misreports with prior 0.35 (a misreporting clerk names the other shelf).
- She says "shelf_2". Truthful: 0.25·0.65 = 0.1625. Misreporting: 0.75·0.35 = 0.2625. **P(misreport) = 0.62**, an upward move.
- Had she said "shelf_1": 0.0875/0.575 = **0.15**, a downward move.
- No-update: had both shelves been equally likely, either statement leaves **0.35**.

This shows that the direction depends on the prior plausibility of what was said, without supplying a 4b or 4c template.

Record the replacement as a dated Entry 1b (it supersedes the example clause of Entry 1a RC10). Re-run `test_v22_prompt_is_v21_plus_one_section` and commit the new prompt hash before `regress`. This is the single written revision, made before any output. It is not an iteration under RC11.

**S2 — The "PRIOR" sentence is false for one card line. Make it conditioning-correct.** v2.2 says that public-model probabilities are "PRIOR probabilities: how likely something was before the robot observed anything." The 4c card's own line is conditional on an observed event: "A person who says they would rather keep the package is obstructive with the probability below." (In the generator the remark is always made, so it carries no likelihood ratio.) Under the v2.2 wording, a model is invited to treat 0.05 as pre-observation and then update again on the remark (double counting). That is an internal contradiction between prompt and card in 1 of 12 constructions.

Reword generically, for example:

> Probabilities stated in the public model are the probabilities with which the situation was generated, given exactly what each line says they depend on; they are not yet updated on the rest of the history. Your distribution must be the POSTERIOR: update on the events and statements in the history that those probabilities do not already take into account.

Make this part of the same Entry 1b, before any call.

**S3 — Unit order in the rendered notes leaks role order. Canonicalize it.** `matched_notes_text` renders units in graph-insertion order, which is `focal_units` order. That is role order:
- 1c lists C (the corroborating colleague) before the distractor;
- 2a and 2c list H (the informed courier) before N (seed 20261100, 2a: `K(tomas)`, then `K(omar)`);
- 4b lists X (the low-rate reporter) before Y.

The generator deliberately alphabetizes courier names and speaking order because "role order would mark the informed courier / low-rate reporter". The notes reintroduce that cue, but only in the note conditions. It is matched between inferred and reference, but it confounds every note − none contrast: a policy that defaults to the first-listed courier when a note is uncertain or wrong gains in 2a/2c for a reason other than the note content.

Sort rendered units by a role-independent key, for every source (for example by `str(u)`; names are freshly drawn per seed). Add a test that two insertion orders render byte-identically. Disclose that Round B rendered in role order.

**S4 — `power.md` must report what RC5 requires when the criterion fails, and the consequences.** At present it reports only "chosen K = 24". Add the following:
- (a) **Minimum detectable effect at K = 24**, for P(helps) ≥ 0.8. A normal approximation from the simulated half-widths gives about 0.11 under variance B and about 0.08 under variance A.
- (b) **The K a resolving test would need.** For P(no practical value | Δ = 0) ≥ 0.8, the half-width must be at most about 0.035. That means K ≈ 93 under B and K ≈ 45 under A, about 12 h and 6 h at 8 min per seed, beyond the 4 h limit. P(helps | Δ = 0.10) ≥ 0.8 needs K ≈ 28 under B.

  These are my approximations. Compute and report them by simulation or by stated extrapolation.
- (c) **Plain statements of the limitations:**
  - under a true null, the expected outcome is "unresolved" (P = 0.71 under B, 0.45 under A), and "no practical value" is reached only with P = 0.27 or 0.54;
  - at Δ = δ = 0.05, P(helps) is only 0.21 or 0.46;
  - therefore an §5(4) outcome is the likely result under small or zero effects and must not be read as weak evidence for the null;
  - the simulation tests "helps" at the conservative 0.025 for the reference contrast, so it slightly understates power whenever the inferred p is the smaller.
- (d) **Disclose that the planning input** is 6 Round B `none` returns per (stratum, stakes) cell, from 4 constructions.

Put this text into the freeze, either as `power.md` hashed or as an amendment line.

**S5 — Anomaly precedence in `report_repair_stage2.py`.** RC4: when the inferred − reference CI lower bound is > +δ, the result is an anomaly that needs a mechanism check, "not 'approximates'". The script sets `anomaly` but still lets `inf_class()` return "helps and approximates", which maps the cell to §5(1). Give the anomaly precedence: the inferred class becomes "anomaly (inferred above reference)", and the outcome becomes "mechanism check; no §5(1)".

**S6 — Fidelity output is incomplete.** Entry 2 requires, for every inferred note, the categories, TV, unsupported mass and coverage, by construction.
- `fid_sum` omits the categories, and the per-note `fid` rows are not written anywhere. Add category counts per construction, and write the per-note rows to the privileged `data/repair-block/` path (summaries go in the public report).
- In 4c, posterior = prior, so `prior_copy` there counts correct notes. Report it as "matches prior (correct in 4c)", separately from the 4b prior-copy rate. Add the 4c over-update count (|p − prior| > 0.02).

**S7 — RC13(a) byte-level differences are not produced.** Add to the depth section, for 3a and 3c:
- the diff of the reference K(F→R) and K(R) rendered note blocks (expected: only the unit-label and "estimate of …" line differ);
- the number of states where they differ beyond those lines (expected 0).

**S8 — Blocked episodes and missing cells must be visible, not silently excluded.** `good` excludes blocked episodes, and `contrast()` drops any base scenario that lacks a condition. Pre-declare:
- the base-scenario value is the mean over its available episodes;
- a base scenario that lacks a condition is excluded only from that contrast.

Output the list of blocked episodes and excluded base scenarios per condition and construction, with the reason. This keeps the "nothing is dropped" rule.

**S9 — Compute completeness (AGENTS.md §7; plan-opus RC14).**
- `a.get("prompt_tokens") or 0` turns missing usage into 0. Count attempts with missing usage separately.
- Report reasoning tokens per condition, or "unavailable", using the existing `reasoning_tokens_known` flag. Never report 0 in place of "unavailable".
- Report the notes-stage and policy-stage monotonic wall clock with concurrency (`notes.wall_s` and the manifest `wall_clock_s`).
- Time `reference_note` in the notes stage and report it as non-deployable oracle CPU time.

**S10 — Disclose the separate ×1/×4 note draws.** Plan-opus optional 1 was not adopted: `stage_notes` draws an inferred note per state, so the ×1 and ×4 variants of a base scenario see independent note draws. The stakes pair therefore differs in both stakes and note draw. State this in Entry 1b.

## Optional

1. **Exact sign-flip enumeration.** `sign_flip_p` always uses 100,000 Monte Carlo flips. RC3 specifies exact enumeration when 2^n ≤ 10^6. This matters only if a single seed block completes (n = 12), but it is a one-line conformity fix.
2. **Commit check in `stage_policy`.** Have it assert a clean git tree, with `stage2-notes-freeze.json` tracked and unchanged, so that "committed before any policy call" is enforced and not only procedural.
3. **Overrun rule.** Start a new seed block only if the remaining budget is at least one estimated block time (about 8 min), so the 4 h limit is not exceeded by one block.
4. **Label scan.** Extend the rev-7 design-label scan (`test_r7_prompts_have_no_design_labels`) to the 576 fresh-seed states, and to policy prompts with the reference and inferred matched-note blocks rendered. It currently covers only the default seed and policy prompts without notes. The qualification ran the r6 version.
5. **Regression summary.** Next to the 4b prior-copy rate, also report the inferred status distribution and the PM-citation rate per construction.

## Short reasoning

- **S1 and S2** concern whether the one permitted revision is a generic prior-vs-posterior instruction (D-015 Q1) or a construction-shaped template. The arithmetic and the no-dev-v3-numbers constraint are satisfied. The hypothesis-space isomorphism is not. It is cheap to fix now and impossible to fix after any output (RC11).
- **S3** is a shortcut of the kind AGENTS.md §5.5 names (template or generator ordering), and the generator already guards against it in the history and the public model.
- **S4–S10** make the frozen analysis report what the plan already requires, and keep a likely "unresolved" result from being misread.
