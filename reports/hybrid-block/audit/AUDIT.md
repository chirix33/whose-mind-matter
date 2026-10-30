# D-020 audit: input contract and evidence export (hybrid block)

Date: 2026-10-30. Authority: `HYBRID_FALLBACK_RESULTS_REVIEW.md` (D-020).
- CPU only, on existing artifacts. No model calls, new seeds or paid calls; vLLM stays stopped.
- Commands:
  - `python3 scripts/hybrid_input_audit.py RUN` (WSL, 25 s)
  - `python3 scripts/hybrid_export_bundle.py RUN`
- RUN = `~/officeminds-runs/hybrid/hybrid-fallback-20261029-233643-d93b61` (frozen pilot, git `b42589d`, clean).

## 1. What each component received at runtime

Classes: (i) the same public task card and visible history the LLM saw; (ii) task-specific engineering supplied in advance; (iii) generator or simulator metadata of the realized instance that the agent does not see as such.

| component | runtime inputs | class |
|---|---|---|
| LLM policy (all four conditions) | task card r7 (people-rules r6 + numbered public-model text), visible ledger (actions, notices with who was present, answers), physical summary, legal actions; after a veto, one line with p, J, V_alt and the reduced legal list | (i) |
| generic_gate check (LLM) | the same card, ledger and summary, plus the proposed action | (i) |
| ask_first rule | the proposal, people present, the robot's own past asks | (i) |
| gate arithmetic (J, V_alt, offices visited empty, recipient visible) | public `WorldConfig` fields (layout, offices, horizon, stakes, recipient) and the visible history | (i) |
| **checker_gate tracker** (`tracker_check(sc, hist, a)`) | **`inst.scenario`**: the disclosed hidden-variable prior plus the generator builder. The builder closes over the **construction ID, the role→name mapping, distractor level and office order**. Plus the visible history | **(ii) and (iii)** |
| **public-model Bayes reference / planner** | the same `inst.scenario` plus the visible history | **(ii) and (iii)** |
| referent engine (`relational.py`; CPU qualification only, never deployed in the pilot) | a hand-compiled `PublicModelSpec` per template, **selected by construction label**, plus the visible history | (ii) and (iii) label |

So the deployed checker and the Bayes reference did **not** literally receive only what the LLM received. That was not stated in FINAL_REVIEW and is disclosed here.

## 2. Was the instance metadata informative? (`input-audit.json`, `input-audit-checks.jsonl`)

**Card-compiled public model.** Built from what the LLM saw:
- Enumerate every generator pattern whose rendered r7 task card is **byte-identical** to the LLM's card. Patterns cover all 12 constructions × 3 distractor levels × every assignment of roster names to roles × the disclosed rate options.
- Mix those patterns uniformly, each with its own disclosed prior.
- This uses the generator only as a template library (class ii). No realized-instance metadata is used.

| check | result |
|---|---|
| card class contains the true pattern | 192 / 192 states |
| card-class size | 1–3. Size > 1 in 128 states: {1a, 1c} share a card, and {3a, 3b, 3c} share a card. All role→name assignments are pinned by the card text |
| t0 Bayes value, instance vs card-compiled | max \|Δ\| = **0** (192 states) |
| t0 best first action | **0** disagreements |
| every checker_gate check in the pilot: p, location distribution, gate verdict | **380 checks**: max \|Δp\| = 0, max \|Δloc\| = 0, **0** verdict changes |
| logged pilot p / verdict vs recomputed | 0 differences |
| visible history pins one pattern | 192/192 t0 states and 380/380 checks, so the uniform pattern weighting cannot matter |
| replayed observations equal the recorded agent views | 0 mismatches (384 checker episodes) |

**Conclusion.** For these templates, the instance metadata was informationally redundant given the card and the history. The deployed checker is **output-equivalent** to a public model compiled from the same task card the LLM saw.

That compilation relies on the generator's template library: hand-written, task-specific engineering (class ii). It does **not** parse arbitrary text. On an unseen template it would need a compile step whose cost and reliability were not measured. The pilot result should be described as "symbolic checker using a hand-compiled public model of these templates", not "inferred from text".

## 3. Bayes reference: expectation vs realized rollout

| quantity (192 pilot states) | instance model | card-compiled model |
|---|---|---|
| exact expected return at t0 (expectimax over the posterior) | 0.8846 | 0.8846 |
| **realized return of the deterministic planner on each state's actual hidden draw** (CPU evaluation in this audit; not part of the frozen pilot) | 0.8719 | 0.8719 (×1: 0.871; ×4: 0.873) |

- The realized figure is one deterministic rollout per state. The planner has no sampling, so there is one value per state, not a distribution over policy draws.
- It is computed on the same 192 states and hidden draws the LLM conditions faced.
- On those states it exceeds every LLM condition: checker_gate 0.564, generic 0.433, direct 0.303, ask_first 0.270.

Caveats:
- It is a CPU evaluation added in this audit, not a pre-registered pilot condition.
- Zero LLM tokens is not zero compute. The audit's planner computations took seconds of CPU across 192 states (expectimax at every step).
- It depends on the same hand-compiled template library (class ii).

## 4. Exported evidence (this directory)

Convention: columns or keys prefixed `eval_`, and the `evaluator_only` blocks in traces, are evaluation-only (replay with the hidden draw, or the exact reference). They were never inputs to a deployed condition.

| file | content |
|---|---|
| `episodes.csv` | 1,536 rows: state, seed, base scenario (grouping unit), construction, stakes, condition, draw, outcome, return, steps, checks, vetoes, substituted asks, wall clock, checker CPU ms. Per call kind (decision / redecision / check): calls, attempts, failed attempts, fallbacks, prompt / completion / reasoning tokens, reasoning-known flag, latency. Processed tokens, action string. `eval_bayes_v_t0`, `eval_bayes_first_action` |
| `interventions.csv` | 909 rows (every check, cache or cap event and substituted ask in the three intervention conditions): proposal, class, p, J, V_alt, allow, veto, re-decision, second-check verdict, scripted fallback, executed action, episode outcome; `eval_proposal_would_have` |
| `episodes-agent.jsonl.gz` | full per-episode records **without** the privileged block (agent view, steps, all call attempts with text and reasoning, usage) |
| `episodes-privileged.jsonl` | hidden draws only, keyed by (state, condition, draw) |
| `input-audit.json`, `input-audit-checks.jsonl` | §2–3 per-state and per-check rows |
| `traces/*.json` | representative traces (§5) |
| `run-manifest/` | the pilot's start and final manifests and progress file |
| `source-ef77ad6.zip` | `git archive` of commit `ef77ad6`: all `src/`, the hybrid scripts, prompts (pilot-v1, hybrid-v1), tests, configs, the D-019 / D-020 records and the three ruling copies |
| `diff-0440ff3..ef77ad6.patch` | source diff of the whole block, from before D-019 to this audit |
| `HASHES.sha256` | sha256 of every exported byte in this directory |

Already in `reports/hybrid-block/`: protocol and freeze, CPU gate, trigger audit, token forecast, smoke probes, analysis outputs and the Bayes reference.

## 5. Representative traces (`traces/`; all from seed 20261400)

1. **`1_social_discrimination_checker`** (3b ×1, checker_gate): the robot asks the courier, then proposes `give(F)`. The checker gives p = 0, J = −0.55 < V_alt = 0.85, and vetoes. On re-decision the robot walks and delivers: success, 0.80. Evaluator: the vetoed handoff would have failed.
   - **`…_direct_same_state`:** on the same state and draw, direct proposes the same `give(F)` and executes it: error, −0.60.
2. **`1_social_generic_vetoes_correct_handoff`** (2a ×1, generic_gate): the LLM check estimates p = 0.50 for a handoff to the informed courier and vetoes it. The robot then asks, walks and delivers (0.80). The handoff would have succeeded (Bayes: give, 0.95).
3. **`2_ex_ante_rejection_of_lucky_drop`** (4a ×4, checker_gate): `drop` with p = 0.95 has J = 0.80 < V_alt = 0.8425, so it is vetoed twice. The robot walks and delivers (0.75). The drop would have succeeded in this draw, but the veto is the ex-ante better choice, matching the Bayes first action `move(hall)`.
4. **`3_gate_induced_timeout`** (2b ×1, checker_gate): `drop` with p = 0.5 is vetoed, and that drop *would have failed*. The policy then re-entered the same empty office and timed out (−0.40, vs −0.60 for the error). Timeouts of this kind reflect the policy's search inefficiency after a veto.
5. **`4_missed_opportunity`** (3a ×1, checker_gate, draw 1): Bayes would give to the aligned courier at t0 (0.95). The policy never proposes a commitment, oscillates between hall and offices, and times out (−0.40). A veto gate cannot help here.

## 6. Corrections and status

- **FINAL_REVIEW §4, 3c sentence, corrected to:** "is consistent with sampling variability; no check fired in the cited failing checker episodes." The absence of a check does not establish the cause of the whole condition difference.
- **FINAL_REVIEW §1 and §5, input contract:** "the public model is executable" should read "the checker uses a hand-compiled model of these templates. It received instance metadata, which this audit shows to be output-equivalent to compiling the LLM's own task card."
- **Not addressed, as stated in the review:**
  - no deployed marginal-vs-joint ablation exists, so the pilot gain is not attributed to the joint relational representation;
  - the reviewer has not yet reproduced the CIs, the 1,008 qualification checks or the tests.

  Everything needed is in the source zip and data files above.
- **Spend ledger:** USD 3.92404 of 5; 1,130 calls; 0 unresolved. It was unchanged through D-019 and D-020.
- **Services:** vLLM stopped (GPU at 2.0 GB idle).
