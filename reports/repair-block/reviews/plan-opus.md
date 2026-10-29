# Plan gate (scientific validity): repair-and-validation block, Entries 1–2

Reviewer: Opus (plan gate). Date: 2026-10-28. Reviewed before any code or output for this block.
Inputs: `DEV_V3_RESEARCH_REVIEW.md` (D-015), `docs/decisions/2026-10-28-D015-repair-and-validation-block.md`, `reports/repair-block/experiment-plan.md`, and as background `reports/dev-v3-block/{FINAL_REVIEW,roundB-summary,experiment-plan}.md`, `src/vomi/pilot.py` (`task_card`, `notes_text`, `PEOPLE_RULES_R6`, `Package`), `src/vomi/unit_schema.py` (`validate_unit_output_v21`), `src/vomi/fidelity.py` (`SUPPORT_MIN`, `unsupported_mass`), `prompts/pilot-v2.1/unit_system.txt`, `prompts/pilot-v1/policy_system.txt`, `src/officeminds/devgen3.py`, `scripts/run_dev_v3_notes.py` (`computed_note`, `rendered`). No model calls, no code run.

## Verdict: PASS WITH REQUIRED CHANGES (RC1–RC14)

The plan covers every D-015 §3–§5 item in substance: one package revision (citable PM IDs with invented-ID rejection; one prior-vs-posterior instruction; no-belief/uncertainty/abstention kept); a matched renderer without the reference-only correctness line; full-distribution scoring; fresh preselected seeds; generator unchanged; all four strata (STOP, first-order, depth, probabilistic); equal construction weights; ×1/×4 pairing; frozen payloads; failures charged; base-scenario-level paired analysis with the tail kept; compute reported without a post-hoc penalty; and an outcome map to the four §5 possibilities. Hiding citations for every source is consistent with "retain citations for audit, with a consistent policy-visible display" (a uniform empty display, with citations kept in the records).

What remains is mostly ambiguity that would allow post-hoc choices: which interval decides each outcome and how Holm enters, gaps in the outcome map, an under-specified planning model whose target (+0.10) does not match δ = 0.05, a K grid capped well below the resource limit, a freeze that contains a seed list which depends on a K chosen after the freeze, and renderer canonicalization. Three points are scientific rather than clerical: the wording of the shared status line, the structure of the worked example, and fresh-seed symbolic qualification.

## Required changes

**RC1 — Freeze order (K and the seed list).** Entry 1.2(3) freezes "the Stage 2 protocol and seed list", but Entry 2 computes K "after the Stage 1 freeze". Do one of the following and say which: (a) run the precision simulation before `stage1-freeze.json` and put K, the seed list, the simulation script hash, its RNG seed and its output table in the freeze; or (b) write a dated K amendment (simulation script and output hashes, K, explicit seed list `20261100 … 20261100+K−1`) and commit it before any Stage 2 model call. In either case, list in the freeze the hashes of `scripts/report_repair_stage2.py`, the power-simulation script, the renderer, the r7 card renderer, the v2.2 prompt, the schema and the validator.

**RC2 — Planning model and target effect.** Specify the simulation before running it:
- (a) the generative model: per-episode outcome classes (success at k steps, error, timeout) with probabilities and returns per condition. State how Round B's 4 constructions map to all 12. A natural choice is to apply each stratum's Round B rates to the stratum's other two constructions, with stratum 1 at zero effect.
- (b) Inject alternatives as explicit shifts: an effect 0, an effect δ = 0.05 and an effect 0.10, each produced by a stated mechanism (for example, a fewer-errors mixture).
- (c) Use at least two variance assumptions, Round B's per-state paired-difference SD and that SD × 1.5. Round B's reference had the correctness line, so its effect is not the matched reference's effect.
- (d) Report, for each K, the probability of each mapped outcome (RC4) under each assumed effect, plus the CI half-width. Power at +0.10 alone is not enough, because "no practical reference value" requires CI upper < δ, which needs a half-width below about 0.05 when the effect is 0.
- (e) Use the Holm-adjusted α actually applied (RC3).

**RC3 — One decision statistic and how Holm applies.** The map uses "CI lower bound > 0" and "CI upper < δ", while Holm is stated over p-values. Pre-declare exactly one of the following:
- (i) Holm-adjusted sign-flip p (two-sided; the smaller p tested at 0.025, the larger at 0.05) decides "> 0", and the point estimate decides "≥ δ"; or
- (ii) Holm-adjusted bootstrap CIs (97.5% for the first rejection, 95% for the second) decide both bounds.

Also state the CI level for the δ-based statements ("CI upper < δ"; inferred − reference), and say whether the bootstrap is percentile or BCa. Sign-flip: exact enumeration when 2^n ≤ 10^6, otherwise 100,000 Monte Carlo flips with a fixed seed.

**RC4 — Make the outcome map exhaustive and mutually exclusive, with precedence.** At present:
- "inferred helps, reference does not" is unmapped;
- "reference unresolved, inferred helps" is unmapped;
- "inference fails" = "reference helps and inferred does not" mixes a demonstrated failure with imprecision.

Replace the map with a table over (reference class ∈ {helps, no practical value, unresolved}) × (inferred class ∈ {helps and approximates, fails, unresolved}). Define:
- "inferred fails": the inferred − none CI upper < δ, or the inferred − reference CI upper < −δ;
- "inferred unresolved": everything else that is not "helps".

Map each of the 9 cells to one of the four §5 possibilities. A reference-unresolved cell maps to "uncertainty too large", with the inferred result reported descriptively. An inferred-better-than-reference cell is reported as an anomaly that needs a mechanism check, and is not read as "approximates".

**RC5 — K grid and the resource rule.** By my count, one seed is 12 constructions × 2 variants × 3 conditions × 2 draws = 144 episodes, plus 24 stratum-3 depth-control episodes, plus about 40 notes. At Round B throughput, K = 8 is about 1 h of the 4 h limit. The ruling prioritizes more independent base worlds. Either extend the grid up to the largest K the resource estimate allows (for example {3, 4, 5, 6, 8, 12, 16, 20, 24}), or justify the cap at 8.

Pre-declare the rule order:
- (1) drop the K values that exceed the resource estimate;
- (2) take the smallest remaining K that meets the criterion;
- (3) otherwise take the largest feasible K, and report the minimum detectable effect and the K a resolving test would need.

Also pre-declare the overrun rule: run notes for all seeds first; then run policy in **complete seed blocks** (all 12 constructions × conditions × variants × draws per seed, counterbalanced within the block). If the wall-clock limit is hit, analyze only completed seed blocks and report the shortfall. That keeps construction balance.

**RC6 — Stratified bootstrap.** Construction counts are fixed by design (equal weights). Resample base scenarios **within construction** (stratified cluster bootstrap) so that the interval reflects the declared 25%-per-stratum target. Sign-flips remain per base scenario. State the estimand explicitly: the equal-weight mean over the 12 constructions and over ×1/×4 of expected return, generalizing to new public and hidden draws of these 12 constructions, not to new constructions. Report the per-stratum contrasts (stratum 1 included, as a harm check) as secondary, with their CIs.

**RC7 — Renderer canonicalization and tests.** "Byte-identical for equal distributions" needs a canonical form. Today `computed_note` drops zero-mass values and sorts alphabetically, while inferred notes can list zeros, duplicates or any order. Pre-declare:
- value order: the fact-domain order, then "unknown", or the intent order;
- the zero-mass rule: omit p < 0.005 after rounding, for every source;
- rounding: 2 dp, with the status rule applied to the unrounded distribution, stated;
- the `about` field and the unit label: rendered from the unit definition (`describe_unit`), never from model output;
- the section header and the graph statuses (`fact_refuted` / `stale` from `STATUS_TEXT`): identical for every source, or removed for every source. Say which.

Test byte-identity for (i) equal distributions given in a different order, (ii) a distribution with explicit zero values, (iii) inferred against reference payload objects with differing extra fields (citations, unresolved, model status).

**RC8 — Status-line wording (shared, but not an authority cue).** Without the correctness line, the matched reference in 2a renders K(N) as "office_a: 1.00, grounded" and K(H) as "UNCERTAIN". "Grounded" can be read as "this belief is true", which invites give(N), the error. That would be an artifact of wording that affects both sources, and it would be misreported as a note-induced harm or a null. Word the status line as the robot's confidence about the person's mental state, for example "robot's confidence in this estimate of <person>'s belief: high (one value ≥ 0.8) / low (several values remain)". Keep (and test) a constant reminder that a person's belief can be false or outdated. The same text applies to every source.

**RC9 — Abstain rendering, exactly.** Specify what an `abstain` note shows: the distribution and the rule-derived status line plus the banner, or the banner only. Do not show a contradictory "high confidence" status next to "INFERENCE ABSTAINED". Treat the banner as part of the inferred source's typed content (it is not a source label), report the number of abstain-bannered notes shown per construction, and test the rendering.

**RC10 — The v2.2 prompt is committed and gated before the regression check, and the example is not 4b-isomorphic.** The plan does not contain the instruction text or the worked example, so this gate cannot judge them. Before any v2.2 call:
- (a) commit the complete `prompts/pilot-v2.2/unit_system.txt` and its hash;
- (b) the warehouse example must not share 4b's structure (two reporters with differing statements, independent disclosed obstruction rates, a uniform lie over the other values). It must use none of the dev-v3 rate values (0.02, 0.03, 0.3, 0.4, 0.05, 0.06) or their posteriors (about 0.94–0.95);
- (c) the example should include one case where the evidence does **not** move the posterior off the prior (as in 4c), so that the revision does not teach "always move away from the prior";
- (d) the Stage 1 results gate reviews that text.

Disclose that 4b in Stage 2 reuses the inspected construction and the same two rate pairs. Stage 2 is therefore new draws of the targeted construction, not an out-of-construction test of the revision.

**RC11 — Tighten "format or plumbing bug fixes only".** Allowed: code changes that make the schema, validator, parser or renderer conform to the spec already written in Entry 1. Not allowed after any regression output: any change to the prompt text, the example, decoding, max_tokens, retries, or the validator's acceptance set. In particular, no loosening to accept what the model produced, such as `PUBLIC_MODEL`.

Each fix records the triggering output ID, the diff, and the re-run. All regression runs are reported, not only the last. Truncations at 2048 are failures and do not trigger a token-limit change. If a change outside these limits seems necessary, stop and return under D-015 ("no another prompt revision").

State that the regression check has no content pass/fail threshold for entering Stage 2. Its numbers are temperature-1.0 single draws, and they are not comparable to Round B's temperature-0 notes as evidence that the revision fixed prior-copying.

**RC12 — Fresh-seed symbolic qualification, without replacement.** The "qualification unchanged" test covers only seed 20261029. Before the freeze, run the symbolic Round A checks on every fresh-seed instance actually used (×1 and ×4, perm0):
- the r6 rules over every positive-prior world;
- the exact reference posteriors and Q-values (oracle runtime);
- the stratum-4 stakes flips (for the parameter pair each seed draws);
- the evidence-resolution support check for strata 1–3;
- the R15 shortcut scan at rev 7.

Confirm by search that seeds 20261100+k were never used, including in tests. Pre-declare that no seed is skipped or replaced on the basis of these results. A failure is reported as a generator finding, and the block returns rather than editing the generator.

**RC13 — The depth reading is pre-declared.** In the reference arm, K(R) and K(F→R) have the **same value distribution** in 3a (uniform over the two new offices) and in 3c (o_a, p = 1). They differ only in 3b (K(F→R) = o_a with certainty; K(R) uniform over the two others). Declare:
- (a) 3a and 3c are label-only controls (the expected K(F→R) − K(R) ≈ 0), and their byte-level note differences are reported;
- (b) 3b is the only construction where the contrast concerns content;
- (c) the 3a/3b contrast is the difference-in-differences (cond − none)[3b] − (cond − none)[3a], computed per base-scenario pair across seeds, descriptive only;
- (d) no depth-2-specific claim is made from this block. At most it is reported that the "3b K(F→R) − K(R)" pattern is or is not consistent with depth-2 value, with its CI and n.

**RC14 — Frozen payload proof and compute completeness.** As in Round B, commit a notes-freeze proof (payload and rendered-notes hashes per state × condition, coverage) before any policy call, and have the policy stage verify it. Compute per condition includes:
- the failed and truncated note attempts;
- the stratum-3 K(R) note calls;
- prompt, completion and reasoning tokens (reasoning tokens as "unavailable", never 0, when not returned);
- the calls;
- the monotonic wall-clock time per stage, with concurrency recorded.

Also record the reference/oracle CPU time, labeled non-deployable.

## Optional

1. Generate one inferred note per base scenario × unit, from the ×1 card, and show it in both stakes variants. The unit's content does not depend on stakes, and this makes the stakes pair differ only in stakes. If this is not adopted, disclose that ×1/×4 also differ in their note draw.
2. Add, to each stratum, a correctness-augmented reference, labeled as a diagnostic, in a small fixed subset (strata 2–3, 1 draw). It bridges to Round B's reference and isolates the effect of the correctness line. D-015 permits this as a separately labeled diagnostic.
3. Fidelity: also report zero-posterior ("impossible") mass, next to the scoring-v3.1 `unsupported_mass` (posterior < 0.2). Report the 4c over-update rate (a note more than 0.02 from the prior, where posterior = prior) as the complement of the 4b prior-copy rate. Report TV over valid notes, with coverage alongside.
4. Report how often the inferred prompt for a fully failed cell ("(none instantiated)") differs from `none` ("(none; this agent does not use …)"). This prompt-text difference is disclosed, not equalized.
5. Disclose the interface changes from Round B that affect every arm, so that Round B and Stage 2 are not compared as like for like: PM IDs in every card (including `none`), no excerpts or citations, and decoding at temperature 1.0 with max_tokens 2048 for notes.

## Short reasoning

- **Matched renderer.** A single status rule applied to the distribution is genuinely matched, and removing citations, excerpts, model status and source labels for every source removes the authority cues D-015 names. The residual risks are canonicalization (RC7), the semantics of the shared word "grounded" now that the correctness line is gone (RC8, a real hazard in 2a), and the abstain banner. The banner is an acceptable, disclosed asymmetry, because abstention is typed inferred content and D-015 requires keeping it, but it must be rendered unambiguously (RC9).
- **Regression check.** It cannot select the package as long as the prompt is fixed and committed before it runs and "plumbing" excludes every content-bearing knob (RC10–RC11).
- **Worked example.** A generic Bayes-enumeration instruction is a fair answer to D-015's prior/posterior directive. Leakage risk comes from an example isomorphic to 4b, or one sharing its numbers. Fresh 4b seeds reuse two rate pairs, so the protection has to come from the example's structure (RC10).
- **Stage 2.** The design is sound, but its precision depends on assumptions that are not yet written (RC2), on a decision statistic that is not yet chosen (RC3–RC4), and on a K cap that conflicts with the "more base worlds" priority (RC5).
- **Base scenarios.** Within a construction, base scenarios in strata 1–3 differ only in names, labels and uniform office draws. They are independent draws of a narrow distribution, so the estimand must say it generalizes over these 12 constructions (RC6).
- **Decoding.** Temperature 1.0 for notes is justified by the model card and by making retries informative. It is part of the package definition, and it is disclosed as conditioning on one sampled note per state.
