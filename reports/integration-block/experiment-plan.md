# Integration diagnostic: pre-registration (D-016)

Authority: D-016 (`REPAIR_BLOCK_RESEARCH_DECISIONS.md`). Development data only. One diagnostic block, then return. Gates as before: Opus checks validity, Sonnet recomputes the numbers. Entries are append-only.

## Entry 1 — design (written before any code or output of this block)

### A. Existing-trace audit (no model calls)
- **Source:** repair Stage 2 run `repair-stage2-20261029-132459-743ace`, the none / inferred / reference conditions in all 12 constructions, with separate tables for 2a, 2b, 3a and 3b.
- **Action patterns, the main evidence.** Per construction × condition × stakes:
  - the t0 first-action distribution (give, drop, ask, move, wait, deliver);
  - for later decisions (t ≥ 1): stale-label exposure (whether any shown note had the graph status `stale` at that decision); the action at the step right after an ask (give, drop, other); and whether that give or drop was an immediate wrong delivery.
  - No causal comparison between episodes that did and did not ask.
- **Reasoning classification** (explicit rubric, heuristic, reported with examples):
  - for the 3b and 2b reference episodes' give/drop decisions, the decision's reasoning text is coded as (i) treats a stated or estimated belief as the recipient's location, (ii) applies the forwarding rule to the courier's belief about the recipient, (iii) other, or (iv) uncertain;
  - keyword rules are written before any coding, with 3 representative examples per class and every uncertain case listed;
  - the reasoning text is not treated as a causal record.
- **Symbolic check:** for every 2a/2b/3a/3b instance and its standardized ask (§C), whether the ask leaves the allocated unit's true content unchanged (the person's belief) and whether it leaves the unit's public-model posterior unchanged (the robot's estimate). Both are reported, and kept distinct.

### B. Probe states and notes
- **Fresh seeds** `20261200 + k`, k = 0..7, never used before. Constructions 2a, 2b, 3a and 3b; unperturbed ×1 and ×4 variants. That is 64 states in 32 independent base units (seed × construction). No other seed is ever substituted.
- **Notes:** exact public-model reference notes for the construction's focal units (2a: K(H), K(N); 2b: K(N); 3a/3b: K(F→R)). They are computed once per state at t0 and frozen (sha256), then reused unchanged in every rendering, status and context condition. There are no inferred notes and no new inference package.

### C. Decision contexts and conditions
- **t0 context:** the episode's first decision.
- **Post-ask context:** from a clone of the same t0 world, run one standardized legal action, `ask(<subject>, <query fact>)`. The subject is the person in the first focal unit in canonical (alphabetical unit-label) order. The prompt is then built from the full history (both steps, with costs and the remaining horizon). The ask is fixed in advance and never chosen from any trajectory. If the subject is absent or the ask is illegal in some state, that state's post-ask context is reported as unavailable; none is expected.
- **Rendering:** r7 matched content as in the repair block, with two flags:
  - `implication` (off/on). On adds one line per courier unit after the note's content: "Given this estimate and the stated forwarding rule, give(X) sends the package to <office> with probability <p>[, to <office> with probability <p> …]". It is computed from the note's own value distribution and the declared handoff route (K(j) for an own-belief courier; K(F→R) for F). Mass on "unknown" maps to "is not forwarded to any office (a wrong delivery)".
    - It has no hidden destination, true/false label, optimal action, Q-value or advice.
    - Known property, disclosed: in 2a and 3a the line can show destination uncertainty even though the handoff succeeds. Only the history, not the note plus the rule, establishes that the courier is current. This is what the positive controls test.
  - `stale_warning` (shown/omitted). Omitted hides only the graph status `stale` line ("new evidence about this person has appeared…"). The t0 timestamp, the content, and any other status (for example `fact_refuted`) stay; nothing is relabeled fresh.
- **Conditions:**
  - t0: `none`, `content`, `content+impl`. The stale factor cannot apply at t0, so the 2×2 prompts reduce to these three, verified byte-identical.
  - Post-ask: `none`, plus the 2×2 `content|shown`, `content|omitted`, `impl|shown`, `impl|omitted`.
  - Total: 64 states × (3 + 5) × 3 draws = **1,536 single-decision calls**.
- **Policy:** the local gpt-oss-20b, unchanged: pilot-v1 policy prompt, r7 card, temperature 1.0, max_tokens 1024, reasoning low, concurrency 8. Up to 3 attempts per decision (the existing protocol; a truncation is a failed attempt); after 3, fallback wait(), recorded. Dispatch is counterbalanced (conditions rotated by state and draw).

### D. Measures
For each decision with action a at history h:
- **wrong**: a is give or drop, and stepping a clone of the true world with a ends in an error;
- **correct handoff**: a is give or drop, and the step ends in success;
- **gap**: V*(h) − Q*(h, a), from ExactOracle on the plain public-model posterior, with Bayes-optimal continuation and asks legal. This is an evaluator quantity, not an estimate of LLM rollout return.

### E. Analysis (`scripts/report_integration.py`, frozen before outputs)
- **Unit:** the base unit (seed × construction). Its value per condition is the mean over ×1/×4 × 3 draws, computed separately for t0 and post-ask. Stakes are also reported separately.
- **Contrasts**, each paired within base units, as a mean difference with a 95% bootstrap CI resampling seeds within construction (10,000 resamples):
  - t0: content − none, impl − none, impl − content;
  - post-ask: each note condition − none; the implication main effect (impl − content, averaged over status); the omission main effect (omitted − shown, averaged over implication); and the interaction.
- Every contrast is reported for wrong rate, gap and correct-handoff rate. It is broken out per construction, and the negative pair (2b, 3b) is pooled separately from the positive pair (2a, 3a). There are only 8 seeds per construction, so all of it is descriptive.
- **Pre-declared reading** (§5 of the ruling; "negative" = 2b+3b, "positive" = 2a+3a):
  - **Mapping helps while preserving the positive controls:** in the negative pair, the impl − content wrong-rate CI upper bound is < 0, *and* in the positive pair the impl − content correct-handoff point estimate is ≥ −0.10, at t0 or post-ask (reported separately).
  - **Status omission helps only after asks:** post-ask omitted − shown wrong-rate CI upper bound < 0 in the negative pair, with the same positive-control condition.
  - **Neither helps:** both effects' CIs include 0, or both point estimates are ≥ 0.
  - **Uncertain:** anything else. Report the effect sizes and the number of seeds a resolving test would need.
  - Comparisons with `none` are always reported, and no note condition is called helpful without them.
- The API check (§F) is reported separately and never pooled.

### F. API policy check
- **Selection** (fixed now): for each construction c, seed index = int(sha256(f"integration:api:{c}")) mod 8, and stakes = ×4 if int(sha256(f"integration:api:stakes:{c}")) is odd, else ×1. Both that state's t0 and post-ask contexts are used: 8 contexts.
- **Conditions:** `none` and `content` (status shown, the existing presentation). That is **16 decision calls**.
- **Model:** gpt-6.1-sol at reasoning effort low, max_output_tokens 2000, one attempt, no retries.
- **Budget:**
  - reconcile the ledger first;
  - worst case = Σ(estimated input tokens × $2/M) + 16 × 2000 × $10/M, which must be ≤ USD 0.50 and keep the cumulative total < USD 5;
  - the stage cap is spent + 0.50, enforced by the ledger's reservations;
  - if the worst case does not fit, skip the check and report that.
- A failed or truncated response is recorded as a failure. If failures prevent interpretation, the check is "inconclusive about policy capability".

## Entry 1a — Amendment after the plan gate (2026-10-29; before any probe output and before any re-coding of reasoning)
Gate report: `reviews/plan-opus.md` (PASS WITH REQUIRED CHANGES RC1–RC9). All are adopted. Both optional items are adopted too: the positive-pair wrong rate, and an exact paired sign-flip test next to the bootstrap.

- **RC1 Ask subject.**
  - The subject is `path[0]` of the first focal unit in alphabetical order: F for K(F→R), N for 2b, and whichever of H/N sorts first in 2a.
  - The per-state (ask, fact, subject role) list is frozen in `integration-freeze.json`.
  - 2a post-ask results are split by the role that was asked.
  - The symbolic check of content and posterior is reported per state (`qualification.json`, `symbolic`).
- **RC2 Stale factor, described accurately.**
  - At the post-ask context, every focal unit is `stale` because its people were seen or mentioned at t1; a `wait` would do the same. The factor is therefore "omit every `stale` status line". It concerns the evidence-touch label, not ask-specific invalidation.
  - Statuses are computed by the unchanged `advance` on the real post-ask history. The qualification asserts that only `stale` appears (true in all 64 states) and logs each unit's triggering evidence IDs.
  - The audit splits stale exposure into after-ask and sighting-only.
- **RC3 Implication qualification** (`qualification.json`, `implication_table`; hashed in the freeze).
  - There are 80 courier lines in 64 states, with no `unknown` mass, so the wrong-delivery clause was dropped.
  - The line is a function of (frozen note, `handoff_routes`) only (`pilot.implication_line`). It inherits "as of step 0" and is never recomputed after the ask.
  - For each line the table also lists the evaluator's P(success | give) and P(wrong | give); these are never shown.
- **RC4 Certainty confound, pre-registered.**
  - The line shows a *certain* destination exactly where the handoff is wrong (2b, 3b, and the stale courier in 2a), and a 50/50 destination exactly where it succeeds (the informed courier in 2a, F in 3a). The destination marginal is not the success probability.
  - The implication may therefore **lower correct handoffs** in the positive controls, and such a drop is attributed to the marginal-only mapping as specified.
  - No joint or success-probability line will be added in this block.
  - The probe has no case with a certain *and* correct destination, so it cannot separate correct use of the mapping from a certainty-keyed heuristic.
- **RC5 Reading map**, as implemented in `scripts/report_integration.py`:
  - **helps (preserving positive controls)**, all of the following:
    - negative-pair factor wrong-rate CI upper < 0;
    - negative-pair condition − none wrong-rate point < 0;
    - positive-pair correct-handoff points ≥ −0.10, both vs none and for the factor;
    - negative-pair factor gap point ≤ 0;
    - positive-pair factor gap point ≤ +0.10.
  - **repairs note-induced harm only**: the factor beats content, but not none.
  - **harm**: wrong-rate CI lower > 0, or positive correct-handoff CI upper < 0.
  - **neither (practically small)**: wrong-rate point ≥ −0.05 and the CI contains 0, or the point ≥ 0.
  - **uncertain**: otherwise.
  - **both factors help**, at post-ask only.
  - t0 and post-ask are read separately and never combined. Omission is read with the same positive-control condition.
- **RC6 Failures.**
  - Attempts, failures and `wait()` fallbacks are reported per condition. Illegal actions are rejected by the schema and count as failed attempts.
  - Wrong and correct rates are computed including fallbacks (primary) and excluding them (sensitivity). Any context whose conditions differ by more than 5 points in fallback rate is flagged.
  - The gap of a fallback `wait()` is its own Q-gap.
- **RC7 Audit.**
  - Rubric v1 (two codes) was applied once *before* this gate. Its output is kept as `audit-v1-pregate.json` and labeled as such.
  - Rubric v2 adds code (v), "uses the courier's own belief", in priority with the others. A decision matching more than one code is "uncertain". The rubric's regexes are fixed here: the RUBRIC block of `scripts/audit_integration.py` has sha256 `fc45f08fff62f4d8aa57e3de24ed3e6351fcd6f049719f69a95d1231a3ca6ab7`, committed before v2 is run.
  - Example traces had been inspected earlier (repair-block gate).
  - The audit adds the symbolic content and posterior check for the asks that actually occurred in the 2a/2b/3a/3b reference episodes.
- **RC8 Freeze (Entry 2).** `integration-freeze.json` holds:
  - the seeds, state IDs and ask list;
  - the note hashes and the implication-table hash;
  - per-condition prompt hashes, with the t0 duplicates proven byte-identical;
  - the per-state Bayes-optimal action sets at both contexts;
  - source hashes, including `report_integration.py`;
  - the dispatch order;
  - the cache policy: no cache; the draw is in the record key; nothing is replayed.
- **RC9 API.**
  - Index = `int(hexdigest, 16) % 8`.
  - Worst-case input = a conservative ceiling of 1 token per 2 characters of the full request, over the actual 16 prompts. Prices come from the API config.
  - Differences from local: 1 attempt vs 3; 2,000 vs 1,024 output tokens; no temperature sent vs 1.0; OpenAI Responses reasoning-effort semantics vs vLLM's. Reported as a descriptive per-context table only.
