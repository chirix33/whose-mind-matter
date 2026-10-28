# Round 1 plan gate: Opus 5.5 scientific-validity review

- **Reviewer:** sub-agent, model opus (Opus 5.5). Read-only; it made no API calls.
- **Reviewed:** commit `03a52c1` (HEAD later `2e4fc95` plus an uncommitted frozen_notes edit).
- **Verdict:** PASS WITH REQUIRED CHANGES.

## Required changes, and what was done
1. **Rule 5 was false on part of the prior support.** The tests checked only realized draws. Two cases failed: (a) backstory updates passed on as `claim`s (32 directed_perspective heard_told worlds), where the speaker does not model the listener; (b) distrusting listeners of an `assert` (16 worlds), who flip their view of the speaker. → **Done as r5.** Clause tests now run over all positive-prior worlds. The 'no backstory claims' test, which passed only on realized draws, was replaced by a test that checks the update-in-passing case explicitly.
2. **Surface conflicts in the rules:** rule 1 (adoption) vs. rule 3 (no adoption); rule 2 'moving updates no one' vs. reported walks, which were witness events; no test of the assessment sentence. → **Done in r5:** rule 1 is scoped to before the task, rules 2 and 3 to during the task, and an `assess` test was added.
3. **Content categories must not depend on status.** pilot-v2's `insufficient_evidence` covers what v2.1 calls `uncertain`, so abstention-first categories bias Δhallucination. → **Done:** `content_category` is computed for every valid output, and H1b is judged on it plus CE/TV over the 19 consistent contexts.
4. **The committed/hedged line is inconsistent** (0.5/0.5 counts as committed, 0.4/0.4/0.2 as hedged). → **Done:** `unsupported_mass` is added; the categories are kept as declared, with the limitation stated.
5. **Proper scores for the 19 consistent contexts** are reported separately. → **Done.**
6. **API r3 → r4/r5 must be labelled** as rules + output cap + fresh draw, descriptive only, with incomplete attempts per cell reported. → **Done.**
7. **Timing and reviewer-exposure disclosure.** → **Done** in `experiment-plan.md`.

## Other points
- **Package:** pilot-v2.1 is a fair single revision. Its examples point at contexts that failed under r3 (rule 2 → uc04/05/21/24; rule 5 → uc14–19), so those contexts should be reported as a slice.
- **Scoring:** v3.1 partitions n and the tie rule is sound. The ambiguous block leans toward 'correct' because answers matching the reference are still credited; say so.
- **Flags:** none disputed.
  - uc15 depends on rule 5(a); it stays consistent because 5(a) was qualified, not dropped.
  - uc03, uc20, uc21 and uc22 have posterior 1.0 only because people without an incentive never lie in the generator; note that CE/TV there penalize hedges.
- **Invariants:**
  - (i) Pin render revisions: manifests now record them.
  - (ii) Round 2 policy and notes must use the same rules revision: both use r5.
  - (iii) Commit frozen_notes before use: done.
- **Optional items, both acted on:**
  - Leakage-vs-committed among all-unsupported ties: implemented.
  - The uc09 local v2.1 case ('unknown' 0.95 while its own note says Dave has a belief): kept for the evidence audit.
