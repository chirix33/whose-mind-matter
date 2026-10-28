# Stage 2 local pilot: report (2026-10-28)

> **Errata (from the pilot review, 2026-10-28; the original text below is unchanged):**
> 1. **Token overhead.** The 56% / 37% / 51% / 15% figures are the share of each arm's OWN tokens spent on routing, units and refreshes. They are not additional tokens relative to direct. Relative to direct (2,586 prompt+completion tokens per episode), total tokens per episode are:
>    - dense 7,718 (+198%);
>    - random 4,479 (+73%);
>    - router 5,647 (+118%);
>    - symbolic 3,020 (+17%).
>
>    The pilot is not a matched-compute comparison.
> 2. **Carryover family.** The direct vs. dense/symbolic difference (+0.037 vs. +0.225) does not isolate retention as the cause: memory, note generation and the subsequent model responses all differ together. It is a family-level association, distinct from the controlled interventions.
> 3. **Nondeterminism.** The r1 and r2 integration runs differed, but their rendered inputs changed. That does not demonstrate same-input nondeterminism. vLLM batching nondeterminism remains a documented possibility, unsupported by a controlled repeat here.
> 4. **Dirty tree.** The statement that only the generated integration report was dirty at launch is plausible but not proven by the manifest. Runs from now on record the dirty-path list.
> 5. **Two interface defects** found in review, both fixed in renderer r3 (`docs/decisions/2026-10-28-D013-pilot-review-repairs.md`):
>    - the policy's mind notes omitted each unit's cited evidence;
>    - the unit validator accepted a probability-1 attribution with no evidence.

**Exploratory pilot on development data (`dev-v2`).** These groups can never become confirmatory test data. All numbers trace to run `pilot-full-20261028-060517-3237fb`:
- `reports/pilot/pilot-full-pilot-full-20261028-060517-3237fb.md` (generated tables);
- `reports/pilot/pilot-analysis-pilot-full-20261028-060517-3237fb.md` (generated analysis);
- `reports/bundle/pilot-full-{manifest,summary}.json`.

No C1–C5 claim follows from this pilot. There is no requirement for any method to win.

## 1. What ran
| Item | Value |
|---|---|
| Frozen set | `dev-v2`, 36 groups / 80 instances, set hash `3e8afe544f7e2900…` (`reports/pilot/dev-v2-freeze.md`), frozen at commit `4bb749c` before any LLM call |
| Code | commit `151846b`. The run manifest says `git_dirty: true`; the only uncommitted file at launch was the generated integration report from the preceding run. Code and prompts were exactly `151846b` |
| Model / serving | local `gpt-oss-20b` (MXFP4), vLLM 0.32.0, existing recipe (`--attention-backend TRITON_ATTN`, `--gpu-memory-utilization 0.85`, `--max-model-len 16384`); nothing upgraded |
| Decoding | temperature 0, `reasoning_effort` low, max_tokens 1024, JSON-schema structured output for every call. **Temperature 0 does not guarantee reproducibility under vLLM batching**; runs used 8 concurrent episodes |
| Prompts | `prompts/pilot-v1/*` (sha256 in the run manifest), renderer revision r2; one shared neutral policy prompt for all arms |
| Arms | direct (full transcript, no explicit units); dense (all eligible units); random (budget 2, seeded); router (prompted, per step, budget 2, STOP allowed); symbolic-reference allocation |
| Symbolic arm | picks the first best minimal set of the privileged `grounded_typed` annotation at t0, but the **content is LLM-inferred**. A reference-selected allocation, not an oracle-optimal LLM allocation |
| Failure protocol | 3 attempts per call. Then the unit abstains, the router STOPs, or the policy falls back to `wait()`; all attempts are logged |
| Cache | none; every call is fresh |
| Volume | 400 episodes + 9 paired interventions (18 rollouts); episode phase 289 s, total 337 s wall clock (monotonic) |
| GPU | nvidia-smi `memory.used` 30,277 → 30,397 MiB of 32,607. This is the vLLM reservation (KV cache pre-allocated), **not** an activation peak; no peak measurement was available |

## 2. Before running: input check and the fixes it forced
`scripts/check_pilot_inputs.py` compares **fully rendered** requests (task card with stakes-scaled rewards, ledger, physical summary, legal actions) across single-knob variant pairs (`reports/pilot/input-check-dev-v{1,2}.md`):
- **dev-v1: 10 violations.** Evidence was emitted only when its hidden condition held, so evidence pairs whose hidden condition was false rendered identically (4 ambiguity + 6 false-belief pairs).
- **Stakes pairs:** identical histories, but different rendered requests (the reward line carries −0.5 × stakes). The model does see the changed consequences, and there is no cache key to drop them.
- **A role-order cue the check also found:** the public roster was listed in role order (the holder first).
- **dev-v2** makes evidence visibly informative either way and sorts the roster: **0 violations**.
  - The only identical rendered pairs left are two plausible-distractor name permutations, where nothing visible distinguishes the holder (a hidden-role permutation by design).
- dev-v1 is preserved and still regenerates byte-identically (test).

**Integration revision.** Both runs are kept:
- **Pre-revision** `pilot-integration-20261028-060221-70b781`, renderer r1: valid citations were rejected, because the ledger IDs carried a speaker suffix the model omitted.
- **Post-revision** `pilot-integration-20261028-060439-f22f04`, renderer r2: 0 failed attempts.

The full run used r2.

## 3. Results
**Outcomes by arm** (80 episodes each):

| Arm | Success | Error | Timeout | Mean return | Units / ep. | Calls / ep. (decision + unit + router + refresh) | Episode wall clock mean (s) |
|---|---|---|---|---|---|---|---|
| direct | 0.85 | 0.04 | 0.11 | **+0.617** | 0 | 3.54 | 2.43 |
| dense | 0.84 | 0.07 | 0.09 | +0.566 | 4.92 | 8.66 | 9.79 |
| random (2) | 0.85 | 0.09 | 0.06 | +0.559 | 1.95 | 5.47 | 5.34 |
| router (2, STOP) | 0.82 | 0.10 | 0.07 | +0.549 | 1.43 | 6.71 | 7.78 |
| symbolic-reference | 0.85 | 0.05 | 0.10 | +0.636 | 0.50 | 3.95 | 3.30 |

**Paired per instance vs. direct** (mean diff; wins / losses / ties):

| Arm | Mean diff | Wins / losses / ties |
|---|---|---|
| dense | −0.051 | 10 / 20 / 50 |
| random | −0.058 | 12 / 17 / 51 |
| router | −0.068 | 14 / 20 / 46 |
| symbolic | +0.019 | 14 / 14 / 52 |
| router − random | −0.010 | 18 / 18 / 44 |

Instances within a group are not independent, and no tests were run.

**By symbolic category** (mean return; do symbolic categories transfer?):

| Category | n | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|
| zero_value_stop | 40 | +0.789 | +0.704 | +0.731 | +0.694 | +0.797 |
| useful_current_action | 13 | +0.669 | +0.512 | +0.523 | +0.646 | +0.642 |
| mixed_flip_and_carryover | 19 | +0.463 | +0.458 | +0.442 | +0.405 | +0.466 |
| carryover | 8 | +0.037 | **+0.225** | +0.037 | +0.012 | **+0.225** |

**Typed-unit fidelity** (LLM top hypothesis vs. the person's true content at inference time; privileged scoring):

| Unit type | Calls | Valid | Top = truth | Mean top-p | Top = truth when top-p ≥ 0.8 |
|---|---|---|---|---|---|
| K(j) | 435 | 435 | 0.44 | 0.75 | 0.43 (n = 241) |
| K(j→k) | 239 | 239 | 0.43 | 0.66 | 0.65 (n = 89) |
| R(j) | 38 | 38 | 0.42 | 0.62 | 0.21 (n = 14) |
| R(j→k) | 17 | 17 | 0.24 | 0.56 | 0.33 (n = 3) |

**Other measurements:**
- **Router:** 146 calls, STOP 42% of the time. It used fewer units than random (1.43 vs. 1.95). But it instantiated nothing in only 11 of 40 symbolic zero-value instances. Mean Jaccard overlap with the symbolic reference set: 0.38.
- **Responsiveness:** within single-knob pairs, the first action differs in 4/16 stakes pairs and 8/16 evidence pairs for direct (dense 4 and 6; router 3 and 7; symbolic 3 and 4).
- **Overhead** (share of tokens on routing, units and refreshes): dense 0.56, router 0.51, random 0.37, symbolic 0.15. The router call alone averages about 1,634 tokens per episode, more than the units it buys (1,184).
- **Invalid outputs:** 4 calls needed a retry (3 citations of non-visible evidence, 1 unnormalized distribution, 2 non-JSON attempts on one call). No call exhausted all attempts.

**Paired interventions** (9 prespecified states; controlled rollouts in one realized world, so differences are samples, not expectations):
- The unit changed the first action in **1/9** states.
- Return differences arise mostly in later steps.
- Sign agreement between symbolic delta_J and realized difference holds in 1/2 informative cases.
- The two scalar-selected "negative" states are **exploratory probes only**, not established negative-value cases for typed or LLM inference. Neither showed a negative realized difference: 0.00 and +0.20.

## 4. What this suggests (exploratory; dev data)
1. **The task elicits mental inference, but explicit typed units from this prompt do not help on average.** The direct LLM, which reasons implicitly over the full transcript, is the strongest arm apart from the symbolic-reference allocation (which ties it while using 0.5 units per episode).
2. **The dominant failure is unsupported unit content.** When a person's true belief is `unknown`, units often assert a specific room with confidence (K(j) top = truth is only 0.43 even at top-p ≥ 0.8). The policy acts on these notes:
   - `false_belief-g2-stakes4-evidence0`: dense drops at the wrong office and scores −2.10, against direct's −0.40 (trace `reports/bundle/pilot-traces/unsupported-unit-content-error.json`).
   - `ambiguity-g2-evidence1`: the router's K(alice) = suite_west, while her true belief is unknown (trace `router-unsupported-unit.json`).

   This is the C3 mechanism (harm from unsupported mental attributions) **observed in the LLM**, but on development data without the planned controls. It is a reason to design the RQ3 intervention, not evidence for C3.
3. **One positive signal: retained state.** In the carryover family, instantiating and retaining the reference unit raises mean return from +0.037 to +0.225 (dense and symbolic alike; trace `carryover-signal.json`). That is n = 8 instances in 4 groups.
4. **Selective computation has signal, but the router does not yet use it.**
   - Symbolic-reference selection, with LLM content, matches direct at 15% token overhead, while dense spends 56% of tokens and loses return.
   - The prompted router STOPs often, but not where the symbolic reference says it should, and its own call costs more tokens than the units it buys.
5. **Stakes are visible to, and sometimes used by, the model:** the first action differs in a quarter of stakes pairs.

## 5. Limitations
- Development data; 36 groups; no statistical tests.
- One realized world per instance; temperature-0 runs under batching are not bitwise reproducible (the integration reruns differed).
- Fidelity scoring treats any value other than the true content as wrong, including unknown vs. a value. It does not yet separate false, unsupported and leaked attributions (RQ3 taxonomy).
- The router prompt is a single zero-shot design. Budget 2 for random and router was not tuned.
- No activation-peak VRAM measurement. Episode wall clock includes contention from 8 concurrent episodes.

## 6. Questions for the next review
See `reports/review-request.md`.
