# D-019: Hybrid feasibility block, with a Concept 2 fallback

- Status: **accepted** (research-driver ruling via Ashraf, 2026-10-29).
  - `research-reviews/HYBRID_FEASIBILITY_AGENT_BRIEF.md`: repo copy `HYBRID_FEASIBILITY_AGENT_BRIEF.md`, sha256 `3708e3f9bc46a8db741ed5c620615f87e197fcc0a81b87f8e3f1a8a101994d90`.
  - Rationale: `research-reviews/CONCEPT_COMPARISON_AND_HYBRID_RECOMMENDATION.md`, repo copy sha256 `af8401651a66f883d81f92810f11505fa5a62f6a6abfba915a02f1933ba5cdf3`.
- Supersedes D-018's "no new experiment" instruction **for this block only**. All frozen data and negative findings are preserved.
- Block directory: `reports/hybrid-block/`. Prototype code lives in new modules; dev-v3 and the frozen reports are not modified.

## Binding points, restated

1. **Objective.** Test whether an agent can choose which *joint perspective computation* to perform, refresh, reuse or skip by its expected decision value and cost.
   - A hard-coded action-to-query mapping is a baseline, not evidence for the contribution.
2. **Limits.**
   - At most 2 working days of implementation and 2 h of active local serving.
   - At most 2,304 completed episode rollouts (hybrid + fallback combined), plus at most 96 single-decision smoke probes.
   - No new paid calls (ledger stays about USD 3.924 of 5), router training, full office-day generator, backbone search, future-controller labels or confirmatory evaluation.
   - One frozen configuration per branch. Only demonstrable code or schema defects may be repaired (versioned and logged); there is no behavioral prompt tuning.
3. **Common foundation (CPU first).**
   - Provenance and joint relations, with a clean information boundary.
   - Four qualification families: certain-but-wrong route, uncertain-but-aligned route, STOP, reuse/refresh.
   - A strong cheap tracker with measured costs.
   - A complete decision-interface state machine, using `J_commit = -0.05 + p - (1-p)*0.5*stakes` against a feasible alternative from the same history and horizon (no universal V_safe).
   - A CPU gate record before any model call.
4. **Branch rule.**
   - If the shared semantics are unsound, stop both branches.
   - If only the hybrid's selection economics fails, go to the fallback (§6) with no extra approval.
   - A hybrid pass ends the block with a proposal.
5. **Fallback (§6).**
   - First, a CPU trigger-coverage audit on existing no-note traces.
   - Then one frozen pilot of at most 1,536 episodes with four conditions: direct; targeted checker + gate; generic verification + the same gate; simple ask/search-before-commit.
   - Same screening criteria as hybrid §5(2), with return and full cost.
6. **Deliverable.** One bundle, `reports/hybrid-block/FINAL_REVIEW.md` and its artifacts. No further methodological round starts automatically.

## Outcome (2026-10-30; awaiting research review)

Handoff: `reports/hybrid-block/FINAL_REVIEW.md`.
- **Foundation:** sound.
- **Hybrid:** not established. Selection economics fails: every relational computation costs about 20 µs and 0 tokens, so the 768-episode pilot was not run.
- **Fallback pilot:** 1,536 episodes, frozen at `b42589d`.
  - checker_gate − direct: +0.261 [+0.186, +0.336].
  - Beats generic_gate by +0.131 [+0.068, +0.194] at 0.76× its tokens.
  - Beats ask_first by +0.294, but at 1.26× its tokens, so criterion (b) fails, and the pre-declared decision is: do not continue Concept 2 as specified.
- **Caveat:** a CPU public-model Bayes planner reaches 0.885 (exact expectation) with no LLM. Any continuation needs a regime where perspective relations are not cheaply compilable.
