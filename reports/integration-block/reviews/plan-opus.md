# Plan gate review (Opus, scientific validity): integration diagnostic, Entry 1

Reviewer: Opus 5.5 (scientific validity). Date: 2026-10-29. Scope: `reports/integration-block/experiment-plan.md` Entry 1 against `REPAIR_BLOCK_RESEARCH_DECISIONS.md` (D-016) §3–§4. No model calls. One symbolic read-only check ran on an **already-inspected** repair seed (20261100), not on the fresh probe seeds. Script: scratchpad `chk_notes.py`.

## Verdict: PASS WITH REQUIRED CHANGES

The design follows the ruling. It uses fresh seeds and the four required constructions with positive controls. The reference notes are exact and frozen once. The factorial uses t0 and post-ask contexts, with `none` included in both. The 1,536-call arithmetic is correct: 4 × 8 × 2 × (3 + 5) × 3 = 64 states × 8 × 3 = 1,536. The API check is hash-selected, fixed at 16 calls, capped and run once. The changes below concern four things: an ambiguity in the ask rule, an inaccurate description of the stale factor, a confound in the implication line that has to be stated before any outputs, and gaps in the reading map that would let a reading be chosen after the results are seen.

### What I verified
- **Fresh seeds.** `20261200+k` appears nowhere in the repo except this plan. The repair block used `SEED0 = 20261100`.
- **Note allocation.** It matches the repair block's primary `reference` condition (`G.focal_units`). The stratum-3 `reference_KR` depth condition is correctly excluded.
- **Reference notes on the inspected seed 20261100** (unpermuted 2a, 2b, 3a and 3b):
  - 2a: K(H) = {two other offices: 0.5/0.5}; K(N) = {announced office: 1.0}.
  - 2b: K(N) = {announced: 1.0}.
  - 3a: K(F→R) = {0.5/0.5}.
  - 3b: K(F→R) = {announced: 1.0}.
- **Stale semantics.** `PerspectiveGraph.advance` marks a unit `stale` whenever any path member is *seen*, *speaks* or is *mentioned* after the note's timestamp (`graph.py:95,102`, `visible_evidence`). `fact_refuted` requires a later physical observation in the claimed room, which one ask cannot produce.
- **Handoff semantics.** A courier whose belief is `unknown` delivers to `UNKNOWN` (`world.py:202`). The public model text says only "forward them to the office where they believe R is" (`devgen3.py:236`, `:244`). It never says what happens with an `unknown` belief.

## Required changes

1. **Ask subject for depth-2 units, and 2a heterogeneity.**
   - "The person in the first focal unit" is ambiguous for K(F→R). Specify subject = `path[0]` (F). R has left and cannot legally be asked.
   - In 2a, alphabetical order of the two courier names effectively randomizes whether the informed courier H or the stale courier N is asked. On seed 20261100 it is N ("omar" < "tomas"). Asking H reveals the recipient's location; asking N reveals nothing new.
   - Freeze the per-state (subject, fact, subject role) list before any call.
   - Report 2a post-ask results split by subject role.
   - Report the symbolic check (does the ask leave the true content unchanged? does it leave the posterior unchanged?) per state. Expected: in 3a the posterior moves to certainty after asking F, and in 3b it is unchanged.

2. **Describe the stale factor accurately.**
   - At the post-ask context, every focal unit is stale because its people were **seen or mentioned** at t1. In 2a both couriers stand in the lobby. In 3a/3b, F speaks and R is mentioned in F's answer. The label is not specifically caused by the ask: a `wait` would produce it too.
   - "Omit only the after-ask stale warning" is therefore identical to "omit every `stale` status line" in the post-ask prompt. State this, and implement it that way for all units.
   - Compute post-ask statuses with the unchanged `advance` on the real post-ask history, never set by hand.
   - Assert that the only non-fresh status is `stale`. If any other status appears, keep it and report it.
   - Log each unit's triggering evidence IDs (said, seen or mentioned).
   - Interpretation: an omission effect concerns the evidence-touch label, not ask-specific invalidation.
   - In audit A, split stale-label exposure into "after an ask" versus "after a sighting or mention only".

3. **Symbolic qualification of the implication line before freezing** (ruling §3D).
   - Add a pre-output table over all 64 states. For each courier line, list the frozen note distribution, the line text, the derived destination distribution, and the public-model P(success | give) and P(wrong | give).
   - Assert that the line is a function only of (frozen note, `handoff_routes`).
   - Confirm that no line has `unknown` mass; none is expected. Then drop the "is not forwarded … (a wrong delivery)" clause. If unknown mass did occur, that clause would import a consequence rule the public model does not state.
   - The line inherits the note's "as of step 0" and is never recomputed after the ask.
   - Hash the template and the table.

4. **Pre-register the certainty confound in the positive controls.** On the inspected seed, the line shows a **certain** destination exactly when the handoff is wrong (2b, 3b, and N in 2a). It shows a **50/50** destination exactly when the handoff succeeds (H in 2a, F in 3a), because the destination marginal is not the success probability.
   - Declare now that the implication may lower correct handoffs in the positive controls for this reason.
   - Declare that such a drop is attributed to the marginal-only mapping as specified.
   - Declare that no joint or success-probability line will be added in this block; that would need review.
   - Disclose that the probe has no case with a certain *and* correct destination. It therefore cannot separate correct use of the mapping from a certainty-keyed heuristic.

   With these statements, the positive controls are a fair and honest, if demanding, test.

5. **Make the reading map exhaustive and protect it from post-hoc choices.**
   - (a) "Mapping helps" also requires the negative-pair impl − none wrong-rate point estimate < 0, and the positive-pair impl − none correct-handoff point estimate ≥ −0.10. If impl beats only `content`, the reading is "repairs note-induced harm only".
   - (b) Add a gap co-criterion. The negative-pair impl − content gap point estimate must be ≤ 0, and the positive-pair gap increase must not exceed a declared tolerance (suggested +0.10).
   - (c) Add a "both factors help" outcome.
   - (d) "Neither helps" requires practical smallness: both point estimates ≥ −0.05 in wrong rate. A CI that contains 0 with a larger negative point estimate is "uncertain".
   - (e) Add a "harm" outcome: wrong-rate CI lower bound > 0, or positive-control correct-handoff CI upper bound < 0.
   - (f) Label the t0 and post-ask readings separately. Never combine them to reach a "helps" reading.
   - Apply the same positive-control condition to omission.

6. **Failures and fallbacks.**
   - Report attempts, failures, `wait()` fallbacks and illegal actions per condition.
   - Compute wrong rate and correct-handoff rate including fallbacks (primary) and excluding them (sensitivity).
   - Flag any contrast whose arms differ by more than 5 points in fallback rate. Implication lines lengthen prompts and could raise truncations, which would mechanically lower wrong handoffs.
   - Define the gap for no-op or illegal actions.

7. **Audit rubric and existing asks.**
   - Add the code (v): "uses the courier's own belief (F knows the current office) instead of F's belief about R". This is the ruling's own-belief versus other-person's-belief distinction, and the likely 3b failure.
   - Freeze the keyword rules as an appended, hashed entry before any reasoning text is coded.
   - Disclose that example traces were inspected earlier.
   - Extend the symbolic content/posterior check to the asks that actually occurred in the existing 2a, 2b, 3a and 3b traces (ruling §3A: "which example asks").

8. **Pre-output freeze entry (append-only Entry 2).** It records:
   - the seed and state IDs and the ask list (RC1);
   - note hashes and the implication table hash (RC3);
   - per-condition prompt hashes, with proof that the duplicate t0 prompts are byte-identical;
   - the per-state Bayes-optimal action sets at both contexts;
   - the analysis-script hash;
   - the dispatch order;
   - the cache policy: the draw index is part of the cache key, and nothing is replayed.

9. **API precision.**
   - Index = `int(hexdigest, 16) % 8`.
   - Compute the worst-case input from the actual 16 prompts with a token count or a conservative ceiling, not a loose estimate.
   - Take the prices from the ledger config.
   - List the differences from the local configuration: one attempt versus three, 2000 versus 1024 output tokens, temperature, and effort semantics.
   - Pre-declare a descriptive per-context table only.

## Optional
- Report the positive-pair wrong rate too (for example, giving N in 2a).
- Add an exact paired sign-flip test alongside the bootstrap, which is anti-conservative with 8 seeds.
- Report the implication's added input tokens as its cost.
- Include the inferred condition in audit A's tables.
