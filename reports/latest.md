# Milestone report — through the redesign concept (2026-10-29)

> **Latest: redesign concept delivered (D-018).** See **[reports/redesign-concept/CONCEPT.md](redesign-concept/CONCEPT.md)**. It is a concept only.
> - Optimizing the current implementation stopped (D-018). The METHOD_REVIEW corrections are applied, including the cost per requested unit: 4,027 tokens, 77% of B0.
> - The concept has two parts:
>   - referential, provenance-carrying unit content with an agent-side relation layer (hand-derived: it determines the handoff relation in 9/9 audited rows vs 4/9 for marginals);
>   - a sequential "office day" Tier 1 task in which perspective content is reused and the log grows causally, with full-history, reasoning and generic-memory baselines kept.
> - Gates G0–G4 each have an abandon criterion. Recommendation: authorize at most G0 (CPU only); otherwise freeze the negative findings.
> - No code, model or API use. A literature check was done (sources in concept §9).
>
> **Earlier: method review delivered (D-017).** See **[reports/method-review/METHOD_REVIEW.md](method-review/METHOD_REVIEW.md)**. It is a proposal; nothing was launched.
> - CPU-only. No LLM calls, paid calls or new seeds.
> - Commands run: `python scripts/method_review_audit.py` (12 s) and `python scripts/method_review_selector.py`.
> - **Bayes over the full history:** every note value and interaction is exactly 0, checked on 36 rows.
> - **Existing symbolic bounded actor:** zero in 5 of 6 constructions; the remaining one, 2c, reflects a default artifact.
> - **Free correct notes for the local actor:** an oracle per-cell choice gains +0.044 in-sample and −0.001 cross-fitted. One unit costs about +63% of a no-note episode.
> - **Relationship audit:** give's outcome depends on the joint of the routing unit and K(R), and the notes expose only marginals. Robot confidence is anti-aligned with success. The pair determines 3b, not 3a.
> - **Recommendation:** stop optimizing this implementation. An optional, bounded closure test of the 3b pair (local, USD 0) has a pre-declared stop rule. Versioned redesigns are listed but not proposed.
>
> **Earlier: integration diagnostic complete (D-016).** See **[reports/integration-block/FINAL_REVIEW.md](integration-block/FINAL_REVIEW.md)**.
> - 1,536 single-decision probes on fresh seeds (3b and 2b, with positive controls 3a and 2a) and a 16-call API check (USD 0.055).
> - Neither the action-consequence line nor omitting the stale label helped. The line harmed at t0 in 3b (descriptive); omission harmed as a caution signal; the post-ask implication effect is unresolved.
> - The API policy was optimal on 8/8 contexts with and without notes (a ceiling result).
> - Outcome §5 bullet 4: stop content and display tuning; method/environment review.
>
> **Earlier blocks** below.

> **Latest: repair-and-validation block complete (D-015).** See **[reports/repair-block/FINAL_REVIEW.md](repair-block/FINAL_REVIEW.md)** (recommendation first).
> - **Stage 1:** the one package revision, pilot-v2.2 (citable public-model IDs, a prior-vs-posterior section, a matched note renderer), then a regression check, a precision simulation (K = 24), symbolic qualification of 576 fresh states, and a freeze.
> - **Stage 2:** 288 fresh base scenarios, 4,032 local episodes. Reference − none −0.024 [−0.074, +0.028] reads "no practical value"; inferred − none −0.043 [−0.098, +0.013] reads "fails". The pre-declared outcome is **§5(3), reconsider the method/environment fit**.
> - Headroom against the exact Bayes actor is about 0.50, but the policy does not turn correct notes into correct actions (3b: a correct note increases the wrong handoff). The proposed 2×2 integration diagnostic needs research review. No paid calls.
>
> **Earlier: the dev-v3 block and the autonomous block** (below).

> **Latest: dev-v3 qualification block complete (D-014).** See **[reports/dev-v3-block/FINAL_REVIEW.md](dev-v3-block/FINAL_REVIEW.md)** (recommendation first).
> - **Round A** (symbolic): a new dev-v3 generator, 12 groups × 4 variants. It has a visible prologue and a declared public model that the reference uses in full. r6 rules are tested over every world, Q-values are exact and ask-aware, and the evidence-resolution check is non-vacuous. It was frozen before any LLM call.
> - **Round B** (local gpt-oss-20b): 192 episodes. The pre-declared reading gives reference notes "headroom present", but that rests on 3 rare no-note failures; inferred notes read "inconclusive". The inferred notes have an interface gap (an invented public-model citation ID, 5/24 notes failed) and 4b content that copies the prior.
> - Recommendation: no allocation learning; inference/integration fixes first; the headroom design goes to research review. No paid calls; the API confirmation was skipped on cost.
>
> **Earlier: the autonomous research block** (below).

> **Latest: autonomous research block complete.** See **[reports/autonomous-block/FINAL_REVIEW.md](autonomous-block/FINAL_REVIEW.md)** (recommendation first).
> - Three rounds were pre-registered and gated (Opus + Sonnet reviewers).
> - On the nine prespecified states, legally inferred notes give no reproducible decision value beyond direct reasoning. The diagnosis is little headroom, privileged-information (target) leakage, and one policy risk-calibration failure that a doubt cue fixes.
> - Recommendation: no allocation learning yet; first a causally justified state design and an out-of-sample rerun (for review).
> - Block API spend USD 2.5566; ledger USD 3.8690 of 5.00.
> - The sections below are the earlier pilot record.


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

## Step 2: frozen development set `dev-v1` (before any LLM output)
Frozen by `scripts/freeze_dev_groups.py` at clean commit `4f1ae8a`, seed 20261028, run manifest in `data/pilot/dev-v1/manifest.json`. Record: [reports/pilot/dev-v1-freeze.md](pilot/dev-v1-freeze.md); committed manifest: `reports/pilot/dev-v1-manifest.json`. Set hash `a52414a40294701c93cb3cc3a8673e4c352890a2f52df04cb2d505f4efb1a474`. **Development data only; never confirmatory.**

- **36 groups / 80 instances:** 9 families × 4 groups (stop, ambiguity, false belief, distractors, conflict, nested reliability, directed perspective, relevance shift, corroborated).
- **Variants stay in their group and share one hidden world,** sampled after the public prior was fixed:
  - stakes ×1/×4: false belief, conflict, relevance shift;
  - evidence absent/present: ambiguity, false belief, corroborated;
  - name/holder permutation: distractors, nested reliability, directed perspective;
  - bystander: stop.
- Names (25-name pool) and office labels (5 sets, both orders) vary per group.
- **Exclusions:** rules E1–E4 were declared in the script and applied identically; 0 exclusions.
- **Generator audit (D-008, logged only):** 12 instances have jointly unsatisfiable face-value defaults at h.
- **Symbolic categories** (grounded_typed, face value; multi-label; privileged annotations that may not transfer to the LLM): {'carryover': 8, 'mixed_flip_and_carryover': 19, 'useful_current_action': 13, 'zero_value_stop': 40}.
  - Half the instances need no mental unit under the symbolic actor: the STOP / no-model-needed cases the review asked to keep.
- **Required depth** (typed, face value): depth 2 only in directed perspective (8 instances); depth 1 in false belief (evidence absent), nested reliability, relevance shift, and some conflict and corroborated instances.
- **9 prespecified paired-intervention states:** 3 useful, 3 zero/STOP, 2 negative, 1 carryover.
  - Chosen by a fixed sha256 order of instance ids, independent of any LLM outcome.
  - Both negatives come from the declared fallback to the scalar records, because the typed record has no negative units in dev-v1.
  - Only one carryover state exists because carryover occurs in a single family (relevance shift) and the rule allows one family per category.
- One instance changes category with the record: `conflict-g2-stakes1` is zero-value under the typed record but negative (−0.18) under the scalar face-value record.

Tests: `tests/test_devgen.py` (determinism, prior independent of the hidden stream, balance, pairing, no hidden parameters in agent views, true world in support, registry replay, stakes variants differ only in stakes). Full suite: **235 passed** at `4f1ae8a`.

## Step 3: input check, dev-v2, and the five-arm local pilot
Full write-up: **[reports/pilot/pilot-report.md](pilot/pilot-report.md)**. Questions for review: `reports/review-request.md`.

- **Input check** over fully rendered requests (`scripts/check_pilot_inputs.py`):
  - dev-v1 had 10 evidence-pair violations and a roster role-order cue.
  - **dev-v2** fixes both and has 0 violations. It was frozen at `4bb749c` before any LLM call; dev-v1 is preserved and byte-reproducible.
  - Stakes pairs differ in the rendered reward line.
- **Integration run**, one episode per arm: it found rejected-but-valid evidence citations. Renderer r2 fixed them, and both integration runs are kept.
- **Full pilot** (`pilot-full-20261028-060517-3237fb`, code `151846b`): 400 episodes + 9 paired interventions, 337 s.

  | Arm | Mean return | Mean diff vs. direct |
  |---|---|---|
  | direct | +0.617 | — |
  | dense | +0.566 | −0.051 |
  | random | +0.559 | −0.058 |
  | router | +0.549 | −0.068 |
  | symbolic-reference | +0.636 | +0.019 (15% token overhead) |

  - Typed-unit fidelity is about 0.43, and is poorly calibrated.
  - Unsupported unit content is the main failure mode.
  - Retained state helps in the carryover family (+0.225 vs. +0.037, n = 8).
- Exploratory development data only; no C1–C5 claim.

## Step 4: pilot model diagnostic (after the pilot review; D-013)
Write-up: **[reports/pilot/model-diagnostic.md](pilot/model-diagnostic.md)**. Questions: `reports/review-request.md`.

- **Repairs (commit `90bca99`):**
  - renderer r3, shared by all arms: people-rules paragraph, evidence-bearing notes, fact-only refutation;
  - pilot-v2 grounding package: per-hypothesis support, plus an `insufficient_evidence` status distinct from person-level `unknown`;
  - scoring v2;
  - OpenAI Responses adapter with a hard spend cap;
  - pilot report erratum.
- **24 frozen fixed unit contexts:**
  - local gpt-oss-20b at low effort: pilot-v2 vs. v1 gives Δ log score +0.02, with v2 over-abstaining (12/24);
  - at medium effort: v1 gets worse (−1.13) and v2 improves (+1.28 over v1);
  - leakage 0 everywhere.
- **Audit (10 contexts):** the scoring reference conflicts with the public rules for overheard statements; recipients' self-knowledge is missed; v2 support can be a rationalization.
- **Crossed (12 instances, fixed all-t0 allocation):** local/local +0.587 vs. local direct +0.696.
- **API cells (gpt-6.1-sol, low effort; runs `unit-contexts-20261028-070945-72da94`, `crossed-20261028-071537-f647df`; spend USD 1.31 of the USD 5 cap):**
  - API notes are better calibrated: +0.40 log score over local on pilot-v1.
  - pilot-v2 abstains on 20/24 contexts on the API model, so the over-abstention is a package problem.
  - Crossed: API/API +0.833, API/local +0.750, API/direct +0.742, local/API +0.554. The policy model drives the gain (policy swap +0.163, 9/1/2); the notes model does not (−0.033).
  - Notes show no reliable gain under either policy. The API/API edge over API/direct is one instance won by policy exploration, not by note content.
- **Ledger fix** (`dffe4c6`): the spend ledger is now thread-safe, with in-flight reservations and atomic writes. 254 tests pass.

## Not done (next steps of the authorized pilot)
1. ~~Freeze dev groups~~ (done, step 2).
2. ~~Server, prompts, five arms, accounting, paired interventions, report and bundle~~ (done, step 3).
3. ~~API cells~~ (done, step 4).
4. Next: the review of `reports/review-request.md` (Q1 scoring vs. public rules; Q2 pilot-v2.1; Q3 replicated oracle-content crossed run before more package work).
