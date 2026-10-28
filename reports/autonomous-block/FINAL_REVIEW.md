# Autonomous research block: final review (2026-10-28)

**Block:** `AUTONOMOUS_RESEARCH_BRIEF.md`, three rounds, all complete. Development data only (dev-v2); every result is exploratory and in-sample.
- Each round was pre-registered in `experiment-plan.md`.
- Each round was gated by two reviewer sub-agents: Opus 5.5 checked scientific validity, and Sonnet 5.5 recomputed every number independently. All reviews are in `reviews/`.
- Every required change was applied before the corresponding outputs were recorded as conclusions.

## Recommendation
**Do not start allocation learning (VoMI-Router training, label generation) yet.**

On the nine prespecified states, legally inferred mental-state notes produced **no reproducible decision value** beyond direct reasoning. The development-level diagnosis (brief §8) is:
1. **Little headroom here.** The API direct policy already succeeds in 8 of 9 states, using asks and physical search.
2. **Privileged-information dependence.** The only consistent gain came from privileged true-belief content, which reveals the delivery target in 8 of 9 states.
3. **A policy risk-calibration failure.** At s9 the policy drops the package on possibly stale testimony (0/14 across rounds). True mental content does not fix this; a note expressing 0.2 doubt does (10/11). That doubt is a generic caution cue, not content value.

**Recommended next milestone, for research review, not started:** a causally justified state design within the original outline, followed by a fresh, out-of-sample rerun of the four-condition value-of-notes diagnostic. The design needs states where:
- (a) the relevant mental content cannot be obtained by one cheap ask: the informant is absent, unreachable, or asking is costly;
- (b) a false or outdated belief matters at realistic stakes;
- (c) the unit's content does not reveal the target. Exclude or separately label K(recipient)-of-own-location units.

The baseline keeps the same legal observations and an equally cautious prompt, so headroom is not manufactured.

## What was tested

| Round | Change | Data / design | Result |
|---|---|---|---|
| 1 | **Public rules r5** (simulator contract, every clause tested over all positive-prior worlds; r4 was superseded after a gate found rule 5 false on part of the prior). **Package pilot-v2.1** ("person has no belief" vs. "robot unsure" vs. abstain; rule citations). **Scoring v3.1** (categories partition n; status-agnostic content category; unsupported mass; ambiguity policy; tie rule disclosed as post-inspection) | 24 frozen fixed contexts × {pilot-v1, v2, v2.1} × {local gpt-oss-20b, API gpt-6.1-sol} at r5; the local r4 run is kept as superseded | API v2.1 at r5: 24/24 coverage, 0 hallucination-type outputs, TV 0.14 on 19 consistent contexts. All gains sit in the 10 contexts the rules target (in-sample). H1b holds on the API only; locally v2.1 adds committed `unknown` errors. Package effects do not hold across models (H1c: no) |
| 2 | Frozen-note injection; 5 conditions with the same API policy and fixed allocation | 9 prespecified states × {none, inferred (v2.1, API), inferred_bare (matched presentation), reference (evidence posterior), privileged (true content)} × 3 draws = 135 episodes | No condition "reliable". privileged +0.057 (fewer steps; target leakage). reference +0.017. inferred +0.039 (reversed by one draw). inferred_bare +0.130, entirely from s9 |
| 3 | One matched control plus replication (brief option 4) | 9 states × {none, reference, reference_doubt} × 4 draws, + s9 inferred_bare × 4 = 112 episodes | H3a and H3b hold: s9 none and reference 0/4; doubt prompt 7/8. H3c holds narrowly: −0.031 vs. reference in 8 states, +0.000 vs. none |

## Answers to the brief's three questions
1. **Are the public rules, labels and scoring consistent?**
   - **Now consistent for 19 of 24 contexts, with the residue disclosed.** r5 states the simulator's actual belief contract and is tested over the full prior support.
   - 5 contexts remain ambiguous (`reference-audit.json`). In three of them (uc02, uc06, uc07) the reference posterior depends on undisclosed generator base rates; in two (uc10, uc11, R(j→k)), on undisclosed backstory templates. They are reported separately and never counted as model errors.
   - The scoring reference also relies on generator honesty rates (posterior 1.0 at uc03, uc20, uc21, uc22).
   - **Open:** whether to disclose base rates publicly or change the label target.
2. **Do legally inferred notes give reproducible decision value in any prespecified situation?**
   - **No, on these nine states.**
   - inferred vs. none: +0.039 overall, 3 states better and 4 worse, and the sign flips if a single draw is removed.
   - The one large effect (s9) comes from expressed doubt, not correct content. The reference model does not support that doubt, and the true note did not help.
3. **If value exists, what limits it?** No content value was found, so the bottleneck question is answered as **headroom and state design**, plus one **policy calibration** failure.
   - Inference quality is not shown to be limiting. Inferred ≈ reference holds by construction outside s2 and s6, and there is only one informative consistent state (s3).
   - Integration of false-belief content is **untested**: at s9 the policy heard the false belief directly in every episode, so a note carrying it added nothing.
   - Allocation was not tested; the allocation was fixed by design.
   - Compute: notes add 29% decision-prompt tokens (USD 0.0092 vs. 0.0072 per episode), plus note generation (USD 0.0610 for 9 notes).

## Failure mechanisms observed
- **Risk calibration (s9, and its twin s1).** After a sincere but possibly outdated answer, the policy drops irreversibly. At s9 this is optimal only if P(unchanged) > 0.929; at s1 (×4 stakes), only if P > 0.966. At s1, `none` took that drop in 2/3 Round 2 draws and was lucky.
- **Target leakage through true-belief content:** privileged notes, especially K(recipient) about their own location, which equals the target.
- **Rule-citation rationalization in v2.1 support** (Opus audit):
  - "could have…" rule support is attached to every value;
  - support is fitted to an assumed spread while decisive testimony is ignored (uc21, uc23);
  - support shows that a value is possible, not that the evidence favours it.
- **The local model misapplies rules:** v2.1 outputs `unknown` 1.0 'grounded' where the person holds a belief (uc01, uc09, uc15). r4 wording made local pilot-v1 worse.
- **A list-order tie-break in notes** (s4): note conditions visit the first-listed office first.
- **Symbolic-label gap.** "useful_current_action" units belong to people who can be asked for one step, so notes are worth at most about 0.05 to an LLM policy that asks.

## Limitations
- 24 contexts and 9 states, all inspected development data.
- r5 and v2.1 were written after inspecting failures on the same contexts, so the Round 1 gains are in-sample.
- Single note draws; 3–8 policy draws per cell.
- The reference uses undisclosed generator knowledge.
- Presentation and status differ between inferred and computed notes, which `inferred_bare` controls only partly.
- One state (s9) carries the doubt finding.
- Disclosed process deviations:
  - the local r4 cells ran before their plan gate returned;
  - the v3.1 tie rule was added after inspecting outputs;
  - the Round 2 notes stage ran before the Round 1 results gate returned (the package choice was pre-committed);
  - audit wording was corrected after outputs existed (no flag changed).

## Spend and resources
- **API spend in this block: USD 2.5566.** The ledger went from USD 1.3123 to 3.8690 of the 5.00 cap, with 0 unresolved charges and 0 reservations:
  - Round 1 fixed contexts: 0.5446;
  - Round 2 notes: 0.0610;
  - Round 2 policy: 1.0379;
  - Round 3 policy: 0.9130.
- **Remaining:** USD 1.1311. No billable work is pending.
- **Local:** gpt-oss-20b on the RTX 5090 (vLLM), for Round 1 only. The server is stopped.
- **Engineering fixes:**
  - the spend ledger is now file-locked across processes, with in-flight reservations, atomic writes, and ambiguous transport failures kept charged;
  - the r5 rule tests run over the full prior;
  - frozen-note injection;
  - the model-diagnostic hand-table erratum.

## Decisions that need research review
1. Adopt r5 and pilot-v2.1 as the working contract and package, pending an **out-of-sample** check on fresh dev-v2 contexts?
2. Approve the state-design expansion in the recommendation: absent or costly informants, consequential outdated beliefs, no K(recipient) target leakage, a cautious baseline. Approve a budget for its four-condition diagnostic. The remaining USD 1.13 covers only a small pilot.
3. Ambiguous references: disclose generator base rates in the public rules, or change the label target so the reference uses only disclosed structure?
4. The doubt finding: should "caution presentation" count as a legitimate controller or policy component, given that a fair test must give the direct baseline the same caution? Or should it be treated only as a calibration confound to remove from value estimates?

## Bundle
- `round1-summary.md`, `round2-summary.md`, `round3-summary.md`: per-round conclusions, as gated.
- `round1-results.md`, `round2-results.md`, `round3-results.md`: generated tables, including the corrected all-context coverage, category and proper-score tables, with denominators and the ambiguity policy.
- `experiment-plan.md`: pre-registrations, amendments and disclosures.
- `experiment-registry.json`: every configuration tried, including superseded and not-run branches.
- `reviews/`: all eight gate reports.
- `reference-audit.json`.
- `round2-notes-freeze.json`, `round3-notes-freeze.json`: payload and rendered-note hashes.
- `evidence/`: per-episode CSVs, representative traces (visible / privileged separated), all manifests, the final ledger, and the focused source diff.
- `unit-contexts-v1-r4.jsonl`, `unit-contexts-v1-r5.jsonl`: rendered requests.
- `checkpoint.md`.
- Source archive: `reports/autonomous-block/source-<commit>.zip` (gitignored).
- Revised prompt, rules and schema:
  - `prompts/pilot-v2.1/unit_system.txt`;
  - `PEOPLE_RULES_R5` in `src/vomi/pilot.py`;
  - `unit_output_schema_v21` and `validate_unit_output_v21` in `src/vomi/unit_schema.py`;
  - `score_output_v3` in `src/vomi/fidelity.py`;
  - tests: `tests/test_r4_rules.py`, `tests/test_round1.py`.
