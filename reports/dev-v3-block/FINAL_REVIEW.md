# dev-v3 qualification block: final review (for the research conversation)

Authority: D-014 (`POST_BLOCK_RESEARCH_DECISIONS.md`). Two rounds, both gated: Opus checked validity and Sonnet independently recomputed the numbers. All of it is development data. Date: 2026-10-28.

## Recommendation
1. **Do not start allocation learning.** The deployable candidate, inferred notes, showed no reliable value on dev-v3, and the ruling reserves that decision for research review anyway.
2. **Next: inference and integration work, tested on fresh dev-v3 seeds.**
   - Give the public-model block citable IDs. 5 of 24 notes failed because the model invented a `PUBLIC_MODEL` ID.
   - Make reliability notes integrate conflicting testimony with the disclosed rates. 6 of 8 4b outputs copied the prior.
3. **Research decision: how to measure the remaining headroom.** On dev-v3 the local policy succeeds in 44–48 of 48 episodes in every condition. The remaining headroom is:
   - (a) a tail of rare costly errors, concentrated in ×4 reliability states;
   - (b) a few extra steps, because the policy asks first instead of giving or dropping.

   Testing (a) needs a design powered for error rates: more draws on error-prone states, paired designs, and possibly the missing API backbone. Whether it is the right target within the original goal is for the research review.

## What was done
**Round A** (`roundA-summary.md`, `qualification.md`, `dev-v3-freeze.json`) built and qualified the dev-v3 generator, symbolically and without any LLM:
- 12 groups in 4 strata × stakes × name rotation = 48 instances;
- a visible prologue and a declared public model that the reference uses in full (aligned information);
- r6 rules tested over every world;
- exact ask-aware Q-values;
- a non-vacuous evidence-resolution check, via a card-consistent superset prior;
- same-physical-state social pairs, and depth-2 certification relative to Π≤1 (not path direction);
- stratum-4 stakes flips;
- a with-chute counterfactual.

The gates caught real problems, all fixed before the freeze:
- vacuous checks;
- mis-specified pairs;
- agent-visible text that contradicted the simulator (quiet-conversation "others present", the public-model header, lobby sightings);
- two name-order cues;
- weak tests, whose earlier rewrite had silently failed to apply.

**Round B** (`roundB-summary.md`) ran 16 hash-selected t0 states (1c, 2a, 3c, 4b) × 4 conditions × 3 draws = 192 local episodes (gpt-oss-20b), with frozen notes. Results:
- **Pre-declared reading:** reference "headroom present"; inferred "inconclusive"; privileged "headroom present" (not deployable).
- **Fragile:** the reference reading rests on 3 rare `none` failures in 48 (2 errors, 1 timeout) and becomes inconclusive without them.
- **Clearest pattern** (single group, single hidden draw): in 4b, episodes with a correct reliability posterior had 0 errors in 24; episodes without one had 5 in 24.
- **3c:** notes removed the 3 of 12 wrong-office visits made under `none`. But the usable content equals R's own belief, so this is not depth-2-specific.
- **Missing API confirmation:** the B2 API batch was not run. Its estimated cost (USD 1.3–2.7) exceeds the USD 0.80 allowance, so it was skipped under the ruling's cannot-fit clause.

## How the ruling's six points were handled
1. r5 and pilot-v2.1 stay versioned diagnostic artifacts. dev-v3 uses r6, which is new for dev-v3 semantics. pilot-v2.1 has not been re-validated, and it has the citation gap above.
2. dev-v3 is a new-template development set; it is now inspected development data.
3. The F1/F2/F4/F5 state design is built: distractors in a balanced block, depth pairs, holder swaps and stakes, with a departed informant in 2b and 3*.
4. The reference conditions only on the declared public model and the visible history (tested). The s9 calibration claim is not repeated. The stratum-4 risk checks now use disclosed rates.
5. Labels are ask-aware: asking is legal in every reference value and every rollout. Ask values are reported per family.
6. No caution reminder was added to any arm.

## Decisions for the research review
1. Approve the inference/integration fixes (citable public-model IDs; integrating conflicting testimony) as a package revision. It would then be validated on fresh dev-v3 seeds.
2. Choose the headroom target: the error tail (rare costly errors at ×4) or step efficiency. Then approve a design powered for it, including whether to fund the API backbone. About USD 1.13 of the original cap remains.
3. Decide whether 3c-type evidence needs a K(R) depth-1 control before any depth-2 claim. Planned: yes.

## Status and resources
- Code is at the head of the `main` branch; the test suite has 298 tests, all passing.
- No paid calls; the ledger stays at USD 3.8690 of 5.00.
- The vLLM server is stopped. No cloud sessions were used.
- Bundle index: `evidence/README.md`.
