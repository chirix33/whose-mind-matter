# Autonomous research block: final review (2026-10-28)

**Block:** `AUTONOMOUS_RESEARCH_BRIEF.md`, three rounds, all complete. Development data only (dev-v2); every result is exploratory and in-sample.
- Each round was pre-registered in `experiment-plan.md`.
- Gating:
  - Opus 5.5 checked scientific validity of every plan and every set of results.
  - Sonnet 5.5 independently recomputed the numbers for every set of results and for the Round 1 plan's reference audit.
  - The Round 2 and Round 3 plans were gated by Opus only.
- Every required change was applied before the gated conclusion was recorded. The 9 gate reports are in `reviews/`.

## Recommendation
**Do not start allocation learning (VoMI-Router training, label generation) yet.**

On the nine prespecified states, legally inferred mental-state notes produced **no reproducible decision value** beyond direct reasoning. The development-level diagnosis (brief §8) is:
1. **Little headroom here, judged by realized outcome.** The API direct policy already succeeds in 8 of 9 states, using asks and physical search.
   - This is partly luck. At s1 it dropped on possibly stale testimony in 2 of 3 Round 2 draws at ×4 stakes, and succeeded only because the recipient had not moved.
2. **Privileged-information dependence.** The only consistent gain came from privileged true-belief content, which reveals the delivery target in 8 of 9 states.
3. **A policy risk-calibration failure.**
   - At s9 the policy drops the package on possibly stale testimony: none 0/7 and reference 0/7 across rounds.
   - Under the reference model, P(recipient still at the stated room) = 0.70, while dropping is optimal only above 0.929. This relies on the generator's undisclosed moving base rate.
   - The true-content note only repeated the answer the policy had already heard, and did not change this.
   - A note expressing 0.2 doubt did: 7/8 in the pre-registered Round 3 replication (10/11 descriptively, including the Round 2 draws that motivated it).
   - This is consistent with a generic caution cue, not content value.

**Recommended next milestone, for research review, not started:** a pre-registered, generator-produced state set built from the outline's own factors, followed by a fresh, out-of-sample rerun of the four-condition value-of-notes diagnostic. It should be built from:
- **F2:** depth minimal pairs, including a relayed-message depth-2 path where the informant is not present at decision time;
- **F4:** information-holder permutations;
- **F5:** stakes pairs where a stale or false belief is consequential;
- **F1:** distractors.

The **state proportions must be fixed before generation**, including zero-value/STOP and distractor states, so that harm (C3) and overhead stay measurable.

Requirements:
- the needed mental content must be **inferable from the shared visible history** (otherwise the outcome is privileged-dependence again);
- K(recipient)-of-own-location units are **separately labelled** (excluding them needs review);
- any caution or risk text is **identical across all arms**, including the direct baseline, and frozen before outputs;
- **no reward change** (asking stays −0.05, like any step);
- the states must be uninspected; this needs a decision.

## What was tested

| Round | Change | Data / design | Result |
|---|---|---|---|
| 1 | **Public rules r5** (the simulator contract; every clause tested over all positive-prior worlds; r4 superseded after a gate found rule 5 false on part of the prior). **Package pilot-v2.1** (person has no belief / robot unsure / abstain; rule citations). **Scoring v3.1** (categories partition n; status-agnostic content category; unsupported mass; ambiguity policy; tie rule disclosed as post-inspection) | 24 frozen fixed contexts × {pilot-v1, v2, v2.1} × {local gpt-oss-20b, API gpt-6.1-sol} at r5; the local r4 run kept as superseded | API v2.1 at r5: 24/24 coverage, 0 hallucination-type outputs, TV 0.14 on 19 consistent contexts. All gains sit in the 10 targeted contexts (in-sample). H1b holds on the API only; locally v2.1 adds committed `unknown` errors. H1c: package effects do not hold across models |
| 2 | Frozen-note injection; 5 conditions with the same API policy and fixed allocation | 9 prespecified states × {none, inferred (v2.1, API), inferred_bare (matched presentation), reference (evidence posterior), privileged (true content)} × 3 draws = 135 episodes | No condition "reliable". privileged +0.057 (fewer steps; target leakage). reference +0.017. inferred +0.039 (reversed by one draw). inferred_bare +0.130, entirely from s9 |
| 3 | Replication plus one matched control (brief option 4) | 9 states × {none, reference, reference_doubt} × 4 draws, + s9 inferred_bare × 4 = 112 episodes | H3a and H3b hold: s9 none and reference 0/4; the doubt prompt 7/8. H3c holds narrowly and fragilely: −0.031 vs. reference (−0.021 without the confounded s6); +0.000 vs. none |

## Answers to the brief's three questions
1. **Are the public rules, labels and scoring consistent?**
   - **Now consistent for 19 of 24 contexts, with the residue disclosed.** r5 states the simulator's actual belief contract and is tested over the full prior support.
   - 5 contexts remain ambiguous (`reference-audit.json`). In three of them (uc02, uc06, uc07) the reference posterior depends on undisclosed generator base rates; in two (uc10, uc11, R(j→k)), on undisclosed templates.
   - Example, uc02: the API v2.1 note gives office_a 0.5 / office_b 0.5, citing rule 2 plus the incentive remark and rule 6. The reference gives office_b 0.95, using the generator's accuracy rate for claimants with incentives. See `evidence/ambiguous-example-uc02.json`.
   - The reference also relies on generator honesty rates (posterior 1.0 at uc03, uc20, uc21, uc22) and on the moving base rate (the s1/s9 risk calculation).
2. **Do legally inferred notes give reproducible decision value in any prespecified situation?**
   - **No, on these nine states.**
   - inferred vs. none: +0.039, 3 states better and 4 worse, and the sign flips if a single draw is removed.
   - The one large effect (s9) comes from expressed doubt, not correct content. The reference model does not support that doubt.
3. **If value exists, what limits it?** No content value was found. The answer is **headroom and state design**, plus one **policy risk-calibration** failure.
   - Inference quality is not shown to be limiting. Inferred ≈ reference holds by construction outside s2 and s6, and there is only one informative consistent state (s3).
   - Integration of false-belief content is **untested**, because the policy heard the false belief directly.
   - Allocation was fixed by design.
   - Compute: in Round 2, inferred notes add 29% decision-prompt tokens per episode (+16% per call; USD 0.0092 vs. 0.0072 per episode), plus note generation (USD 0.0610 for 9 notes).

## Failure mechanisms observed
- **Risky drops on possibly stale testimony** at s9 and its twin s1: P(unmoved) = 0.70 under the reference, against thresholds of 0.929 and 0.966.
- **Target leakage through true-belief content**, especially K(recipient) about their own location.
- **Rule-citation rationalization in v2.1 support:**
  - "could have…" rule support attached to every value;
  - support fitted to an assumed spread while decisive testimony is ignored (uc21, uc23);
  - support shows that a value is possible, not that the evidence favours it.
- **The local model misapplies rules:** v2.1 outputs `unknown` 1.0 'grounded' where the person holds a belief (uc01, uc09, uc15). r4 wording made local pilot-v1 worse.
- **A list-order tie-break in notes** (s4).
- **Symbolic-label gap:** units belonging to askable informants are worth at most about one 0.05 step to an LLM policy that asks.

## Limitations
- 24 contexts and 9 states, all inspected development data.
- r5 and v2.1 were written after inspecting failures on the same contexts, so the Round 1 gains are in-sample.
- **Rounds 2–3 used one API policy** (gpt-6.1-sol, low effort). The headroom and notes findings do not transfer to the local policy, where the earlier pilot found that notes reduced return.
- Single note draws; 3–8 policy draws per cell.
- The reference uses undisclosed generator knowledge.
- Presentation and status differ between inferred and computed notes, which `inferred_bare` controls only partly.
- One state carries the doubt finding.
- The H3c cost comparison has confounded comparators (s6 base rates; s4 list order) and fails if s6 is excluded.
- Disclosed process deviations:
  - the local r4 cells ran before their plan gate returned;
  - the v3.1 tie rule was added after inspecting outputs;
  - the Round 2 notes stage ran before the Round 1 results gate returned (the package choice was pre-committed);
  - audit wording was corrected after outputs existed (no flag changed).

## Spend and resources
- **API spend in this block: USD 2.5566** (exact 2.556608, from tokens). The ledger went from USD 1.3123 to 3.86895 of the 5.00 cap, with 0 unresolved charges and 0 reservations.

  | Item | USD |
  |---|---|
  | Round 1 fixed contexts | 0.5446 |
  | Round 2 notes | 0.0610 |
  | Round 2 policy | 1.0379 |
  | Round 3 policy | 0.9130 |

  The rounded components sum to 2.5565.
- **Remaining:** USD 1.1311. No billable work is pending.
- **Local:** gpt-oss-20b on the RTX 5090 (vLLM), for Round 1 only. The server is stopped.
- **Engineering fixes:**
  - the spend ledger is file-locked across processes, with in-flight reservations, atomic writes, and ambiguous failures kept charged;
  - the rule tests run over the full prior;
  - frozen-note injection;
  - the model-diagnostic hand-table erratum.

## Decisions that need research review
1. Adopt r5 and pilot-v2.1 as the working contract and package, pending an out-of-sample check?
2. **Which contexts are out-of-sample?** All of dev-v2 has been inspected. Options: a new seed, a dev-v3 generated under the same generator before any inspection, or a held-out family split.
3. Approve the state design in the recommendation (F1/F2/F4/F5 factors; pre-registered proportions with STOP and distractor controls; identical caution text across arms; no reward change) and a budget for its diagnostic. USD 1.13 covers only a small pilot.
4. **Reference semantics:** the reference posterior relies on undisclosed generator base rates, honesty rates and templates. Should these be disclosed in the public rules, or should the label target change so the reference uses only disclosed structure?
5. **Label target and oracle semantics:** should VoMI labels account for the LLM policy's ask option? Units belonging to askable informants are worth at most about one step.
6. **The doubt finding:** is a caution presentation a legitimate method component (tested fairly, with the same caution given to the baseline), or a calibration confound to remove from value estimates?

## Commands run and outcomes (WSL, `~/venvs/officeminds`; see `evidence/manifests/` for the configurations)
- **Tests:** `python -m pytest -q` → **279 passed** at block end. The rule tests `tests/test_r4_rules.py` give 9 passed, over all positive-prior worlds.
- **Contexts:** `python3 scripts/render_unit_contexts.py --rev 5` → `unit-contexts-v1-r5.jsonl` (sha256 `bb7835eb…`). The same script at `--rev 3` reproduces the frozen r3 requests exactly.
- **Round 1:**
  - `scripts/run_unit_contexts.py --contexts reports/autonomous-block/unit-contexts-v1-r5.jsonl --packages pilot-v1 pilot-v2 pilot-v2.1 --effort low`, run twice:
    - with the local config at `--max-tokens 4096`: 72 records;
    - with the API config at `--max-tokens 6000`: 72 records, 2 incomplete attempts retried.
  - The r4 local run is the same command on the r4 file.
  - Report: `scripts/report_round1.py <6 run dirs>`.
- **Round 2:**
  - `scripts/run_notes_value.py notes` → 9/9 notes produced on the first attempt;
  - `… render`;
  - `OFFICEMINDS_API_CAP_USD=3.318 … policy --replicates 3 --concurrency 4` → 135 episodes, 0 blocked;
  - `scripts/report_round2.py <run>`.
- **Round 3:**
  - `scripts/run_notes_value.py doubt`;
  - `OFFICEMINDS_API_CAP_USD=4.156 … policy --round 3 --replicates 4` → 112 episodes, 0 blocked;
  - `scripts/report_round3.py <r3 run> <r2 run>`.

## Bundle (brief §9)
1. This review.
2. `experiment-registry.json`: every configuration tried, including superseded and not-run branches.
3. `round1-results.md`: the corrected all-context coverage, category and proper-score tables, with denominators and the ambiguity policy (`reference-audit.json`).
4. `round2-results.md`, `round3-results.md` and `evidence/episodes-round{2,3}.csv`: per state, condition and replicate, with payload hashes (`round{2,3}-notes-freeze.json`). Representative traces are in `evidence/traces/` (visible / privileged separated; the privileged-condition trace shows privileged content by design), with an ambiguous-context example in `evidence/ambiguous-example-uc02.json`.
5. **Prompts, rules and schema:**
   - `prompts/pilot-v2.1/unit_system.txt`;
   - `PEOPLE_RULES_R5` in `src/vomi/pilot.py`;
   - `unit_output_schema_v21` and `validate_unit_output_v21` in `src/vomi/unit_schema.py`;
   - `score_output_v3` in `src/vomi/fidelity.py`;
   - tests `tests/test_r4_rules.py` and `tests/test_round1.py`;
   - the readable diff `evidence/block-source-diff.patch`;
   - commands are listed above.
6. `evidence/manifests/` (commits, dirty paths, configurations, prompt hashes), `evidence/api-spend-ledger-final.json`, `checkpoint.md`. No source archive was generated: `block-source-diff.patch` is the focused diff, and an archive can be regenerated with `git archive <final commit>`.

Per-round conclusions: `round{1,2,3}-summary.md`. Pre-registrations, amendments and disclosures: `experiment-plan.md`. Gate reports: `reviews/`.
