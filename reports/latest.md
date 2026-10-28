# Milestone report — Stage 2, step 1: Stage 1 review corrections (2026-10-28)

**Scope.** The five corrections and Q1–Q6 rulings from the Stage 1 research review (recorded as D-007…D-012), plus one reporting error of mine found while updating memory. This is step 1 of the authorized Stage 2 pilot. **The pilot itself has not started:** no dev-group generation, no LLM calls, and the model server is still stopped. Nothing here is a C1–C5 result.

Archived Stage 1 reports, with errata at the top: `reports/archive/stage1-latest.md`, `reports/archive/stage1-review-request.md`.

## Corrections → what changed
| # | Review item | Change | Evidence |
|---|---|---|---|
| 1 | Depth claim | Required depth = min over reference-attaining subsets of max path length. The prefix definition is kept as historical. Spec prose no longer restates per-case numbers; the table is generated from records | `test_required_depth_never_exceeds_a_sufficient_sets_depth` (all cases × 4 records); `test_depth_claims_from_review`: nested_reliability **1**, path_asymmetry **2 (face value) / 0 (hedged)** |
| 2 | Keep mental content | New record `grounded_typed` (typed (content, default-holds) hypotheses). The Stage 1 record is renamed `grounded_scalar` (diagnostic). Typed LLM unit schema plus a validator with a declared failure protocol. "Leak" framing withdrawn (helpfulness ≠ leakage) | `test_typed_output_carries_content_and_can_legitimately_help` (typed K(alice) +0.045 vs. scalar 0 in `stakes_m4_q0.95`), `test_typed_outputs_are_identical_across_invisible_world_pair`, `test_typed_llm_unit_schema_and_failure_protocol`; `src/vomi/unit_schema.py` |
| 3 | Accounting names | `delta_j` (gross) and `net_vomi(lam)` everywhere. `UnitReport.lam` stated. Tables say delta_J | `src/vomi/oracle.py`, `reports/tiny-cases.md` |
| 4 | Best-subset reference | Primary reference = best admissible objective J − λ·cost (incl. ∅, optional budget). J(all) is historical. Gold matching, D4 conditional relevance, STOP and regret all use the declared reference. STOP and D4 use the conditional best-superset reference, which equals the primary reference at ∅ | `test_best_subset_reference_differs_from_j_all_when_non_monotone`; `src/vomi/allocation.py` |
| 5 | Probability polarity | Serialized scalar fields are `p_default_holds` / `p_default_violated`; `unknown` satisfies a Knowledge default. **The code polarity was already correct; only the report's prose was reversed** (from my Stage 1 sed edit) | `test_scalar_output_polarity_and_projection` (actor marginal after I-projection = `p_default_holds`), `test_unknown_counts_as_satisfying_a_knowledge_default` |
| 6 | My error: grounded `reversal_m*` units "0 at ×4" | Corrected: **+0.02908828 (×1), −0.04688857 (×4)** | errata in archived Stage 1 reports; D-011 |

## Rulings implemented
- **Q1 (D-007).**
  - Typed outputs are the main method; the scalar is a diagnostic. Exact generator marginals are an offline reference, not deployment-cheap.
  - Graph outputs carry a timestamp and visible status; contradicted units must be refreshed (counted) or abstained.
  - **Evidence-change trace** `reports/bundle/trace-evidence-change.json`: K(rec) has p_default_holds 0.7 at t1 (after "alice_loc = office_a"). It becomes contradicted at t3 when office_a is empty, then is refreshed to 0.0 at t3 with cost 2 calls; the old output is kept in history.
- **Q2 (D-008).** `generator_audit` diagnostic, not a filter.
  - No grounded case has an individually entailed violation.
  - Defaults are **jointly unsatisfiable** at h in path_asymmetry, reversal_m* and legacy depth2_handoff. The Stage 1 phrase "possible but not entailed" held per factor only.
- **Q3 (D-009).** Negative values kept, named symbolic partial-model/default-interaction failures.
- **Q4 (D-010).** Face value primary, hedged mandatory. Both appear in every table.
- **Q5 (D-011).** The grounded **unit-vs-STOP** pair is the isolating test (table below). The privileged two-unit reversal is a diagnostic only.
- **Q6 (D-012).** Carryover share reported per record.

## Results (generated in `reports/tiny-cases.md`, run `tiny-20261028-052241-354655`, commit `c80c81c`, clean tree)
**D-011 grounded unit-vs-STOP pair** (`reversal_m*`, `grounded_scalar`, face value; λ = 0.01 illustrative, held fixed):

| Stakes | K(bob): a0 → ay | delta_J | net VoMI (λ = 0.01) | P(flip) | D_memory | STOP preferred |
|---|---|---|---|---|---|---|
| ×1 | move(hall) → drop(office_a) | +0.02908828 | +0.01909 | 1 | 0 | no |
| ×4 | move(hall) → drop(office_a) | −0.04688857 | −0.05689 | 1 | 0 | **yes** |

- Identical at both stakes: visible history (except stakes), prior, candidate set, unit output (p_default_holds = 0.985528), baseline and post-computation actions, cost.
- The posterior-to-outcome table (4 worlds; error mass 0.014472 + 0.036179 = 35/691) is in `reports/tiny-cases.md` and `reports/bundle/stop-pair.json`.
- This shows a stop-vs-compute switch. It does not show better choice between two useful units.

**Carryover share** (positive-delta_J units, all cases):

| Record | Positive units | Carryover units | D_memory share |
|---|---|---|---|
| grounded_typed / face value | 16 | 1 | 0.611 |
| grounded_scalar / face value | 12 | 1 | 0.651 |
| grounded_scalar / hedged | 7 | 0 | 1.208 (>1: positive units with negative current-action parts) |
| privileged_bounded / face value | 40 | 1 | 0.107 |

Typed vs. scalar: the typed record gives positive value to more units (16 vs. 12), e.g. typed K(alice) in `stakes_m4_q0.95`. Whether this tracks LLM typed units is a pilot question.

## Commands run and outcomes (WSL, CPU, commit `c80c81c`, clean tree)
| Command | Outcome |
|---|---|
| `~/venvs/officeminds/bin/python -m pytest -q` | **227 passed** in 52 s |
| `~/venvs/officeminds/bin/python scripts/run_tiny_cases.py --seed 0` | run **`tiny-20261028-052241-354655`**: every episode replays identically and equals its label rollout; no early-failure incentive |

Bundle (`reports/bundle/`):
- `tiny-manifest.json` (commit `c80c81c`, `git_dirty: false`);
- `trace-false_belief.json` (paired visible / privileged / robot-graph trace);
- `trace-evidence-change.json` (D-007);
- `stop-pair.json` (D-011, with posterior-to-outcome tables).

The model server was not used; it has been stopped since 04:01.

## Not done (next steps of the authorized pilot)
1. Freeze 30–50 development scenario groups before any LLM output is inspected (balanced; variants within groups; exclusions recorded).
2. Restart the existing gpt-oss-20b server, and test the typed-unit and policy prompts.
3. Five arms (direct, dense, random, prompted router with STOP, symbolic-reference allocation passing LLM-inferred content), with full compute accounting.
4. 8–12 paired intervention states; the report and bundle the review specified.
