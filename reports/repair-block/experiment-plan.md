# Repair-and-validation block: pre-registration

Authority: D-015 (`DEV_V3_RESEARCH_REVIEW.md`). Development data only. At most two stages; return afterwards.
Gates as in earlier blocks: Opus checks the validity of each plan and result set; Sonnet independently recomputes the numbers. Entries are append-only, and amendments are dated and placed before the outputs they affect.

## Entry 1 — Stage 1: repair and qualify (written before any Stage 1 code or output)

### 1.1 Package pilot-v2.2 (the one documented revision)
- **Citable public model (render revision r7).**
  - Every bullet line of the task's PUBLIC MODEL paragraph gets a stable visible ID, `[PM1]`, `[PM2]`, … in order, including the hidden-quantity lines. The ID is assigned by `task_card` when it renders `cfg.public_model`; the dev-v3 generator and its semantics are unchanged.
  - The r6 rules text is unchanged (RULE1–RULE6).
  - Validation: a support item may cite a visible history ID, `RULE1..6` (kind `public_rule`), or a `PM<n>` that **exists in that instance's card** (new kind `public_model`). Anything else is rejected, including `PUBLIC_MODEL`, `PM99` and IDs from another card. Kind and ID must match.
- **Inference instructions (unit prompt v2.2 = v2.1 plus one added section, written once).**
  - (a) How to cite the public model (`PM<n>`, kind `public_model`).
  - (b) *Prior vs posterior:* probabilities in the public model are priors, before the history. The note must give the posterior after the history: list the combinations of hidden possibilities (who is cooperative or obstructive, who moved) that could produce exactly the observed statements and events, weight each by its prior probabilities, and normalize. Conflicting statements rule out combinations.
  - (c) The distinction between no-belief, the robot's uncertainty and abstention is kept verbatim from v2.1.
  - (d) One worked numeric example from a different setting (a warehouse), never from a dev-v3 construction.
  - No hidden label, posterior value or construction name enters the prompt. No arithmetic tool is added (none planned; any would be versioned and reported).
- **Matched note rendering (r7, shared by every note condition).** The policy sees each note through one template:
  - `<unit> about <about> (as of step 0): v1: p1, v2: p2, …`
  - a status line derived by the **same rule** from the distribution for every source: "grounded" if max p ≥ 0.8, otherwise "UNCERTAIN: several possibilities remain";
  - an "INFERENCE ABSTAINED" banner only if the inferred output's status is abstain (the reference never abstains, a disclosed asymmetry).

  Not shown to the policy for any source: citations, excerpts, unresolved items, source labels, the model-chosen status, or a correctness probability. Citations stay in the records for audit. If an inferred and a reference note have the same distribution, they render byte-identically (tested).
- **Scoring.** Scoring v3.1 categories plus the full-distribution metrics: TV against the aligned public-model posterior, unsupported mass (mass on values the posterior gives < 0.2), and valid-note coverage. Each is reported separately; "correct top-1" is never the only fidelity number.

### 1.2 Stage 1 qualification (before the freeze)
1. **Tests:**
   - PM IDs render and are stable;
   - the validator accepts card PM IDs and rejects invented or foreign IDs and kind mismatches;
   - the matched renderer is byte-identical for equal distributions and carries no source label, correctness line or citation;
   - r7 prompts have no design labels or hidden values (R15 test at rev 7);
   - the dev-v3 qualification values are unchanged (the generator is untouched);
   - the full suite passes.
2. **Regression check on inspected material** (development and debugging only; D-015 Q1): run v2.2 locally on the 16 Round B states' focal units plus K(R) for the four 3c states (24 + 4 notes). Report validity, coverage, TV, unsupported mass, and the 4b prior-copy rate (a note within 0.02 of the disclosed prior on every value).
   - This check does **not** select the package. The v2.2 prompt is written once. Only *format or plumbing bugs* found here may be fixed (for example a schema or validator mismatch), and each fix is recorded. The prompt's inference content is not iterated.
3. **Freeze:** `stage1-freeze.json` holds hashes of the package prompt, schema and validator source, the renderer, r7 card rendering, model and decoding settings, and the Stage 2 protocol and seed list, plus the git commit (clean tree). It is committed before any Stage 2 output.

## Entry 2 — Stage 2: local replication on fresh seeds (protocol fixed now; executed only after the Stage 1 freeze)
- **Base scenarios.** dev-v3 generator, unchanged. A base scenario is one public and hidden draw of one construction: `generate(seed=s)` for seeds `s = 20261100 + k`, k = 0, 1, … (never used before). Each base scenario uses its unpermuted ×1 and ×4 variants (a paired stakes variant; names are already fresh per seed).
  - All 12 constructions get equal numbers of base scenarios, so each stratum is 25% (the declared target distribution; no oversampling).
  - The number of seeds K is set by the precision calculation below, before any Stage 2 output.
- **Conditions** (fixed allocation at t0; notes retained, no refresh; matched r7 rendering):
  - `none`;
  - `inferred`: v2.2, frozen local note payloads;
  - `reference`: the exact public-model posterior given the t0 history, in the same matched format, without a correctness line.
  - **Depth controls**, stratum 3 only: `reference_KR` and `inferred_KR`, the same as the above but with a first-order K(R) note (R's belief about meeting_room) in place of K(F→R). Contrasts: K(F→R) vs K(R) notes within each condition, by construction (3a, 3b, 3c). The 3a/3b contrast comes from the constructions themselves.
  - Privileged notes are not run.
- **Backbone and decoding:** local gpt-oss-20b (vLLM 0.32.0, mxfp4) for both notes and policy.
  - Notes: temperature 1.0 (the model card's recommended sampling), max_tokens 2048, reasoning low, up to 3 attempts. Sampling, rather than temperature 0, lets the retries in the failure protocol actually differ (Round B: attempts 2–3 were byte-identical). One frozen draw per state × unit, made before any policy call.
  - Policy: temperature 1.0, unseeded, max_tokens 1024, reasoning low, as in Round B.
  - This estimates value conditional on the sampled notes, not inference variability.
- **Replication:** 2 policy draws per state × condition. Counterbalanced dispatch, full resets, asking and search always legal.
- **Failures:** as in dev-v3 Entry 1a R11. Truncated outputs are failed attempts; after 3 attempts the fallback is wait() or no note. Everything is logged and nothing is dropped.
- **Sample size (precision calculation, run after the Stage 1 freeze and before Stage 2 outputs).** A simulation, with the assumptions stated:
  - Each base scenario's paired difference (condition − none, averaged over its 2 variants × 2 draws) is resampled from a planning model fitted to the dev-v3 Round B episode returns (exploratory planning input only; not treated as known rates).
  - Report the 95% CI half-width and the power to detect a +0.10 paired mean difference (two-sided α = 0.05, sign-flip permutation) as a function of K (number of seeds).
  - Choose the smallest K in {3, 4, 5, 6, 8} (that is, 36–96 base scenarios) with power ≥ 0.8. If none reaches it, take the largest K that fits the resource limit, and report the achieved minimum detectable effect.
  - **Resource limit:** ≤ 4 h of local GPU wall clock for Stage 2 (notes plus policy), estimated from Round B throughput (192 episodes in about 8 min).
- **Analysis** (`scripts/report_repair_stage2.py`, written and frozen before outputs):
  - **Unit of analysis:** the base scenario. Its value per condition is the mean return over its ×1 and ×4 variants × 2 draws.
  - **Primary contrasts** (Holm over the two): reference − none and inferred − none. Mean paired difference, 95% cluster bootstrap CI over base scenarios (10,000 resamples), and a sign-flip permutation p-value. Error episodes stay in.
  - **Secondary:** inferred − reference; errors, timeouts and steps per condition; results by construction and by stakes; and the depth contrasts (K(F→R) − K(R) notes per stratum-3 construction, descriptive).
  - **Compute:** note and decision calls, prompt and completion tokens, retries and latency per condition. Reported directly as the return/compute tradeoff; no scalar penalty.
  - **Practical threshold:** δ = 0.05 return.
- **Pre-declared outcome mapping** (D-015 §5):
  - **"reference helps"** = reference − none CI lower bound > 0 and point estimate ≥ δ;
  - **"inferred approximates and helps"** = inferred − none CI lower bound > 0 and inferred − reference ≥ −δ (point);
  - **"inference fails"** = reference helps and inferred does not;
  - **"no practical reference value"** = reference − none CI upper bound < δ;
  - otherwise **"unresolved"**, with the achieved CI and the K a resolving test would need.
- **Note fidelity:** for every inferred note, the categories and TV against the aligned posterior, unsupported mass and coverage, by construction.

## Entry 1a — Amendment after the plan gate (2026-10-28; before any Stage 1 model call and before any Stage 2 output)
Gate report: `reviews/plan-opus.md` (PASS WITH REQUIRED CHANGES RC1–RC14). All are adopted and override Entries 1–2 where they differ.

- **RC1 Order of operations.** K is chosen *before* the freeze. The precision simulation uses only dev-v3 Round B data and no new outputs. `stage1-freeze.json` then contains the chosen K, the seed list `20261100 + k` (k < K) and the simulation report.
- **RC2 Planning model** (`scripts/power_repair_stage2.py`, frozen and reported).
  - **Generative model, per episode:**
    - A `none` return is drawn from the dev-v3 Round B `none` returns of the same stratum and stakes (6 values each: 2 name variants × 3 draws).
    - Round B's 4 constructions represent their strata. Each stratum's pool is applied to all 3 of its constructions.
    - A condition with target effect Δ uses the same pool plus a stated mechanism. Each error or timeout episode becomes a success with probability ρ (drawn from the pool's successes). A constant step-saving shift (a multiple of 0.05 return, interpolated) is then added, so that the condition mean exceeds `none` by Δ×4/3 in each of strata 2–4.
    - Stratum 1's effect is 0.
    - Δ ∈ {0, 0.05, 0.10}, with ρ = 0.5 whenever Δ > 0.
  - **Variance:** (A) the empirical pools; (B) pool deviations from their mean scaled ×1.5.
  - **Unit:** the base scenario. Its value is the mean of 2 variants × 2 draws per condition. Both conditions are drawn independently given the scenario. This is conservative: no positive within-scenario correlation is assumed.
  - **Output per K, Δ and variance assumption:** the probability of each reference class (helps / no practical value / unresolved) under the RC3/RC4 rules, and the mean CI half-width. 400 simulated datasets per cell; 2,000 sign flips; 1,000 bootstrap resamples. Fixed seed. Run with `~/venvs/vllm/bin/python` for numpy; numpy is not part of the project stack.
- **RC3 Decision statistic: rule (i).**
  - A Holm-adjusted two-sided sign-flip test over base scenarios decides "> 0". There are two primary contrasts (reference − none, inferred − none): the smaller p is tested at 0.025 and the larger at 0.05.
  - The point estimate decides "≥ δ".
  - δ-based upper statements ("CI upper < δ", and inferred − reference bounds) use the 95% stratified percentile bootstrap CI.
  - Sign-flip: exact enumeration when 2^n ≤ 10^6, otherwise 100,000 Monte Carlo flips with a fixed seed (analysis); 2,000 in the planning simulation.
- **RC4 Outcome table (exhaustive; precedence top to bottom).**
  - **Reference class:**
    - *helps*: reference − none is Holm-significant > 0 and its point estimate is ≥ δ;
    - *no practical value*: CI upper < δ;
    - else *unresolved*.
  - **Inferred class:**
    - *helps and approximates*: inferred − none is Holm-significant > 0, its point estimate is ≥ δ, and inferred − reference has CI lower ≥ −δ;
    - *fails*: inferred − none CI upper < δ, or inferred − reference CI upper < −δ;
    - else *unresolved*.

  | reference ↓ / inferred → | helps and approximates | fails | unresolved |
  |---|---|---|---|
  | helps | §5(1) propose allocation feasibility | §5(2) inference bottleneck | §5(4) uncertainty too large (inferred) |
  | no practical value | anomaly: mechanism check; §5(3) for the method | §5(3) reconsider method/environment fit | §5(3) |
  | unresolved | anomaly; §5(4) | §5(4) | §5(4) |

  If inferred − reference has CI lower > +δ, that is reported as an anomaly needing a mechanism check, not as "approximates".
- **RC5 K grid and resources.**
  - Grid {3, 4, 5, 6, 8, 12, 16, 20, 24}, after dropping every K whose estimated wall clock exceeds 4 h. Estimate: Round B ran 192 episodes in about 8 min; one seed is 144 + 24 policy episodes plus about 40 note calls, roughly 8 min.
  - Choose the smallest feasible K for which, under variance (B), P(helps | Δ = 0.10) ≥ 0.8 **and** P(no practical value | Δ = 0) ≥ 0.8. Otherwise take the largest feasible K, and report the minimum detectable effect and the K a resolving test would need.
  - Overrun rule: all notes first, then policy in complete seed blocks (all 12 constructions × conditions × variants × draws, counterbalanced within each block). If 4 h is reached, only complete blocks are analyzed.
- **RC6 Estimand and bootstrap.** The estimand is the equal-weight mean over the 12 constructions and over ×1/×4 of expected return. It generalizes to new public and hidden draws of these constructions, not to new constructions.
  - The bootstrap resamples base scenarios within each construction (stratified), and sign flips are per base scenario.
  - Per-stratum contrasts, stratum 1 included as a harm check, are secondary and have CIs.
- **RC7–RC9 Renderer** (implemented in `pilot.matched_notes_text`; tested):
  - canonical value order (fact domain, then unknown; or cooperative, obstructive, unknown); duplicate values summed; 2 dp; values below 0.005 omitted;
  - the confidence rule applied to the unrounded distribution; unit label and `about` taken from the unit definition;
  - a constant header reminding the reader that a person's belief can itself be false or outdated;
  - the confidence line worded as "robot's confidence in this estimate of <whose belief/intent>: high (one value has probability at least 0.8) / low (several values remain possible)";
  - graph statuses shown identically for every source;
  - an abstained inferred output shows its distribution and the abstain banner, with no confidence line. The number of abstain-bannered notes shown is reported per construction.
- **RC10 The v2.2 prompt is committed and gated before the regression check.**
  - The worked example has two *agreeing* clerks with prior 0.35 and posterior 0.13. It also includes a no-update case (one statement leaves the posterior at the prior), and it uses no dev-v3 rate or posterior value.
  - Disclosed: Stage 2's 4b seeds reuse the inspected construction and its two rate pairs. Stage 2 is new draws of the targeted construction, not an out-of-construction test of the revision.
- **RC11 Allowed fixes after any regression output:** only code changes that make the schema, validator, parser or renderer conform to Entry 1/1a.
  - Not allowed: changes to prompt text, the example, decoding, max_tokens, retries, or the validator's acceptance set.
  - Each fix records the triggering output, the diff and the rerun. All regression runs are reported. Truncations are failures.
  - There is no content pass/fail threshold for entering Stage 2.
  - Regression numbers are temperature-1.0 single draws, not comparable to Round B's temperature-0 notes as evidence that prior-copying was fixed.
  - If a change outside these limits seems necessary, stop and return.
- **RC12 Fresh-seed symbolic qualification, without replacement.** Before the freeze, `scripts/qualify_dev_v3.py`'s checks run on every Stage 2 instance (×1 and ×4, perm0, all K seeds): r6 over every world, exact posteriors and Q-values, the stratum-4 stakes flips, evidence-resolution support (strata 1–3), and focal units among the candidates. A failing seed is reported, never replaced.
- **RC13 Depth reading (descriptive only; no depth-2-specific claim from this block).**
  - In the reference arm, K(R) and K(F→R) have the same distribution in 3a and 3c, so those two are label-only controls; their byte-level note differences are reported.
  - 3b is the only construction where the contrast concerns content.
  - Reported: the 3b K(F→R) − K(R) contrast (per condition) and the difference-in-differences (cond − none)[3b] − (cond − none)[3a] across seeds, with CI and n.
- **RC14 Notes and compute.**
  - The notes-freeze proof (payload and rendered-notes hashes per state × condition, coverage) is committed before any policy call, and the policy stage verifies it.
  - Compute per condition charges every note attempt, including failed and truncated ones and the K(R) note calls, plus every decision call and retry: tokens, latency, calls.

## Entry 1b — Amendment after the Stage 1 prompt/renderer gate (2026-10-28; before ANY pilot-v2.2 model call)
Gate report: `reviews/stage1-prompt-opus.md` (PASS WITH REQUIRED CHANGES S1–S10). The first run of this gate was lost in a PC restart; this is the re-run. No v2.2 output exists. The prompt changes below are therefore the single pre-output revision, not an RC11 iteration. This entry supersedes the example clause of Entry 1a RC10.

- **S1 Worked example replaced.** The two-clerk example used 4b's hypothesis space, and its no-update case was exactly 4c. The new example uses two shelves with a non-uniform prior (0.75/0.25), one clerk with prior misreport rate 0.35, and a misreporter who names the other shelf:
  - statement "shelf_2": the posterior misreport is 0.62 (an upward move);
  - statement "shelf_1": 0.15 (a downward move);
  - no-update case: with equal shelf priors either statement leaves the prior, 0.35.

  It contains no dev-v3 value and no 1/3 prior. A test recomputes the numbers with `fractions` and checks that the forbidden values are absent.
- **S2 Conditioning-correct wording.** Public-model probabilities are now described as the probabilities with which the situation was generated, given exactly what each line says they depend on. The note updates only on the history those probabilities do not already take into account. This removes the double-counting invitation in 4c.
- **S3 Canonical unit order** in the rendered notes is alphabetical by unit label, for every source. Role order marked the informed courier (H) and the low-rate reporter (X).
- **S4 `power.md`** now reports, by stated extrapolation from the simulated half-widths:
  - the minimum detectable effect at K = 24: ≈ 0.11 under variance B, ≈ 0.07 under A (floor δ);
  - the K needed for P(no practical value | Δ = 0) ≥ 0.8: ≈ 102 under B, ≈ 46 under A, i.e. 13.6 h and 6.1 h, beyond the limit;
  - the K needed for P(helps | Δ = 0.10) ≥ 0.8 under B: ≈ 28;
  - that under a true null the expected outcome is "unresolved" (P 0.72 under B, 0.45 under A).
- **S5** The anomaly (inferred − reference CI lower > +δ) takes precedence over "approximates", and maps to "mechanism check; no §5(1)".
- **S6** Fidelity output now includes category counts per construction and per-note rows (privileged, in `data/repair-block/stage2-fidelity-rows.json`). In 4c a prior match is reported as correct, alongside a separate over-update count.
- **S7** RC13(a): the byte-level comparison of 3a/3c reference K(F→R) vs K(R) rendered blocks is produced, counting states that differ beyond the unit label and the "estimate of …" wording.
- **S8** A base scenario's value is the mean over its available episodes. A base scenario missing a condition is excluded only from that contrast. Blocked episodes and excluded base scenarios are listed with reasons.
- **S9** Missing usage is counted, not turned into 0. Reasoning tokens are reported or marked "unavailable". Notes-stage and policy-stage wall clocks and concurrency are reported, and the reference oracle's CPU time is reported as non-deployable.
- **S10 Disclosure.** The ×1 and ×4 variants of a base scenario get **independent** inferred-note draws, so the stakes pair differs in both stakes and note draw.
- **Optional items adopted:**
  - exact sign-flip enumeration when 2^n ≤ 10^6;
  - the policy stage requires a clean tree with the notes-freeze proof committed;
  - a seed block starts only if a full block (about 8 min) still fits in the 4 h limit.

## Entry 1c — Stage 1 results gate and resumability (2026-10-29; after the Stage 1 regression output, before the freeze and before any Stage 2 output)
Gate reports:
- `reviews/stage1-results-opus.md`: PASS WITH REQUIRED CHANGES R1–R3, all applied. The first run of this gate was lost in a second PC restart; this is the re-run.
- `reviews/stage1-results-sonnet.md`: CONSISTENT.

**Stage 1 regression result** (development, inspected states; no content threshold). Validity: 28/28. Prior copies: 5/8 by the raw count, but only 2 of the 4 diagnosable notes under the R1 count.
- Under R1 the 4 diagnosable notes are the four 4b notes for the high-rate reporter. Two copy the prior, cooperative 0.70 against a posterior of 0.045. The other two give obstructive 0.18 and 0.89.
- The other 3 raw "copies" are X-unit coincidences: there the prior (0.02) and the posterior (0.055) are within the tolerance.
- The 4 unsupported_committed notes are real inference failures: one 2a leakage (the holder credited with an announcement she could not hear) and three 4b misses for the high-rate reporter.

**Changes applied** (none touches the prompt, decoding, validator acceptance or retries):
- **R1 (defined AFTER the Stage 1 output; reporting only).** A prior copy is counted as diagnosable only where |posterior − prior| > 0.04. The raw count is kept beside it. Addendum: `stage1-regress-R1-addendum.json`.
- **R2.** Decision attempts with missing token usage are counted per condition, never turned into 0.
- **R3.** The freeze hashes `configs/models/local_gpt_oss_20b.json`. `verify()` also checks the power, qualification and model-config hashes and the decoding values.
- **Resumability** (engineering, after two machine restarts):
  - The notes stage appends every finished call to `data/repair-block/stage2-notes-partial.jsonl` and skips finished calls when re-run. Wall clock is summed over segments.
  - `policy --resume <run_dir>` keeps complete seed blocks. A block cut off by a restart goes to `aborted-episodes.jsonl` and is re-run in full, so only complete blocks are analyzed.
  - Every resume is recorded in the manifest. The time spent inside an aborted partial block is not added to the 4 h budget, which is disclosed.
