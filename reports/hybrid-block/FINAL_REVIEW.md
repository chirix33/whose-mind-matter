# Hybrid feasibility block (D-019): final review

Date: 2026-10-30. Authority: `HYBRID_FEASIBILITY_AGENT_BRIEF.md` (D-019).
- Workstation: Windows 11 + WSL Ubuntu 24.04, RTX 5090, local gpt-oss-20b on vLLM 0.32.0.
- All results are **development/feasibility evidence**, not confirmatory, and the pilot is not powered for subgroup claims.

## 1. Decisions

| branch | pre-declared rule | outcome |
|---|---|---|
| Common foundation | stop both branches if semantics, joint inference or the information boundary are unsound | **Sound**: 1,008/1,008 engine-vs-enumeration checks; 0 boundary violations; 320 tests pass |
| Hybrid (H0–H5) | run the pilot only if the CPU gate shows a nontrivial allocation opportunity | **Not established in this block: selection economics fails.** Every relational computation costs about 20 µs and 0 tokens, and computing all of them costs the same as one. The 768-episode hybrid pilot was not run (brief §3) |
| Concept 2 fallback | continue only if (a) +0.05 vs direct, (b) the quality-or-efficiency screen vs **both** generic verification and ask-first, (c) not only suppression | **(a) pass, (c) pass, (b) fails against ask-first on token cost.** Under the frozen rule, **do not continue Concept 2 as specified** |

**The most important finding is a caveat on everything above.**
- In this regime the disclosed public model is executable. A CPU-only public-model Bayes planner, with no LLM at all, has an exact expected return of **0.885** on the pilot states at 4.3 s of CPU for all 192 states and 0 tokens.
- That is above every LLM condition, including the best (checker_gate, 0.564).
- So here the deterministic tracker does the work, and the LLM is the weak component. This is consistent with D-017's "zero Bayes value of notes" and with the CPU-gate result.
- Any further perspective-allocation claim needs a regime where the relevant public model is **not** machine-executable, so that relational inference genuinely costs model calls (§6).

## 2. What ran

| step | command | outcome | artifacts |
|---|---|---|---|
| Register D-019 | — | decision record, AGENTS pointer, repo copies (sha256 `3708e3f9…4d90`, `af840165…cdf3`) | `docs/decisions/2026-10-29-D019-hybrid-feasibility-block.md` |
| Common foundation | — | `src/vomi/relational.py` (provenance index, referent terms, shared latents, exact enumeration, dependency cache, gate); `src/officeminds/hybridfam.py` (4 families) | `tests/test_hybrid.py` |
| CPU gate | `python scripts/hybrid_cpu_gate.py` (1.3 s) | foundation sound; hybrid economics fails | `cpu-gate.md`, `cpu-gate.json` |
| Trigger audit, existing traces | `python3 scripts/hybrid_trigger_audit.py` (WSL, 37 s) | opportunity present | `trigger-audit.json`, `trigger-audit-rows.jsonl` |
| Token forecast | `~/venvs/vllm/bin/python scripts/hybrid_token_forecast.py` (offline tokenizer) | 1.18–1.63k tokens per prompt | `token-forecast.json`, `rendered-t0.json` |
| Smoke probes | `run_hybrid_fallback.py smoke` | 48/48 parsed (24 checks, 24 re-decisions); kept, no changes | `smoke.jsonl`, `smoke-summary.json` |
| Freeze | `run_hybrid_fallback.py freeze`, committed `b42589d` | code, prompts, protocol, seeds hashed | `fallback-freeze.json`, `fallback-protocol.md` |
| Fallback pilot | `run_hybrid_fallback.py pilot` | 1,536/1,536 episodes, 0 errored, 8/8 seed blocks, 1,503 s | run `~/officeminds-runs/hybrid/hybrid-fallback-20261029-233643-d93b61` (episodes.jsonl sha256 `a2ec3a4c…e74d`, manifest `3e3b420d…136d`, git `b42589d`, clean) |
| Analysis (pre-declared) | `python3 scripts/report_hybrid_fallback.py RUN` | §4 | `fallback-results.json`, `fallback-interventions.jsonl` |
| Descriptive Bayes reference | `python scripts/hybrid_bayes_reference.py` | 0.885 | `bayes-reference.json` |

**Resources used, against the limits:**
- Implementation: about 1 hour of agent wall-clock (2026-10-29 23:15 → 2026-10-30 00:15), against a 2-day limit.
- Active local serving: about 27 min (vLLM up 23:35 → 00:02), against 2 h.
- Rollouts: 1,536 of 2,304, plus 48 of 96 smoke probes.
- Paid calls: none. The API ledger is unchanged at USD 3.924 of 5.
- No code or schema repair was needed after the freeze.

## 3. CPU gate in brief (full record: `cpu-gate.md`)

**Representation (four families, every hidden world):**
- **2d** has identical route and recipient marginals for two couriers (½ / ½) but joint P(route = recipient) of 1 vs 0. The product of marginals gives 0.5 to both and would veto the correct handoff.
- **2e** has uncertain shared provenance (P = ¾). Union-find cannot represent it; exact enumeration can.
- **3b vs 3c** share a certain route but differ in relation (0 vs 1), depending on R's provenance.
- **Answers** update the robot's estimate and never a person's term.
- **The cache** reuses through irrelevant events, refreshes on person-state changes, and refreshes to P = ½ after an unobserved interval. Reused values always equal a fresh computation.

**Value structure exists:**
- relations license handoffs: +0.10 to +0.15;
- vetoes are worth +0.2 to +3.0 under a committing default;
- STOP applies when deliver() or an announcement settles the case;
- refresh can change which courier is right.

**Economics.** After cheap compilation, nothing costly is left to allocate:
- index build 6–9 µs; one relation 17–28 µs; all relations 19–31 µs;
- the independent world enumeration takes 0.1–1.4 ms;
- a policy decision costs about 1,660 processed tokens.

The only costly step outside this regime, compiling an unseen public-model template from text, is per task and covers all persons and paths at once.

## 4. Fallback pilot results

- **Setup:** 96 fresh base scenarios (8 seeds × 12 dev-v3 constructions) × stakes ×1/×4 × 2 draws × 4 conditions.
- **Means:** per episode.
- **Paired differences:** per base scenario, with a construction-stratified bootstrap 95% CI over 10,000 resamples.

| condition | return | success | error | timeout | steps | processed tokens | call attempts | episode wall s |
|---|---|---|---|---|---|---|---|---|
| direct | 0.303 | 0.724 | 0.229 | 0.047 | 3.08 | 5,168 | 3.12 | 4.6 |
| **checker_gate** (public-model tracker; 368 ms CPU for the whole run) | **0.564** | **0.815** | **0.031** | 0.154 | 4.48 | 8,676 | 5.04 | 7.9 |
| generic_gate (one LLM check per trigger) | 0.433 | 0.750 | 0.086 | 0.164 | 4.54 | 11,430 | 6.47 | 11.5 |
| ask_first | 0.270 | 0.729 | 0.211 | 0.060 | 4.03 | 6,873 | 4.05 | 5.9 |
| *public-model Bayes planner (exact expectation; not an LLM condition)* | *0.885* | — | — | — | — | *0* | *0* | — |

| paired difference | mean | 95% CI |
|---|---|---|
| **checker_gate − direct (primary)** | **+0.261** | [+0.186, +0.336] |
| generic_gate − direct | +0.130 | [+0.040, +0.221] |
| ask_first − direct | −0.033 | [−0.139, +0.064] |
| checker_gate − generic_gate | +0.131 | [+0.068, +0.194] |
| checker_gate − ask_first | +0.294 | [+0.217, +0.375] |

**Criteria (frozen in `fallback-protocol.md`):**
- **(a) Pass:** +0.261 ≥ +0.05.
- **(b) vs generic_gate, pass on both routes:** +0.131 at 0.76× its tokens.
- **(b) vs ask_first, fail.** The return difference is +0.294, but checker_gate uses **1.26×** ask_first's processed tokens. The quality route allows at most 1.10×, and the efficiency route requires at most 0.80×.
  - The extra tokens are not checker cost (the checker costs 0 tokens). They come from re-decision calls (193 vetoes, 0.50 per episode) and 0.45 more steps per episode, spent walking to deliver in person.
  - The criterion was frozen before outcomes, so it is reported as failed, not reinterpreted.
- **(c) Pass:** success 0.815 vs 0.724. Correct-commitment endings fell from 0.464 to 0.380, and timeouts rose from 0.047 to 0.154. Part of the error reduction became timeouts.
- **Pre-declared decision:** `continue_concept2 = false`. Generic verification is **not** similar to the targeted checker: the gap is +0.131 with a CI excluding 0.

**Vetoes, judged against what the vetoed action would have done (evaluation replay):**

| condition | vetoes | would have failed | would have succeeded | social handoffs: fail / succeed | physical drops: fail / succeed | testimony drops: fail / succeed |
|---|---|---|---|---|---|---|
| checker_gate | 193 | 123 | 70 | **49 / 0** | 60 / 40 | 14 / 30 |
| generic_gate | 253 | 123 | 130 | 37 / 41 | 67 / 57 | 19 / 32 |
| ask_first (substituted asks) | 167 | 57 | 110 | 25 / 39 | 23 / 50 | 9 / 21 |

- **checker_gate vetoes of commitments that "would have succeeded"** are ex-ante low-value commitments: p ≈ ½ drops, and ×4 testimony drops, where in-person search has the higher expected value. They are not checker errors.
- **The generic LLM check is indiscriminate.** It vetoes about as many correct as wrong social handoffs (41 vs 37).
- **Stakes:** at ×1, checker_gate scores 0.542 vs direct 0.416. At ×4 it scores 0.585 vs 0.190: the gate's value grows with the error cost.
- **By construction:** the gain is concentrated where the audit predicted, in 1b, 2b, 2c and 3b. For example 3b moves from −0.366 to +0.698 and 2c from −0.439 to +0.381.
  - The 3c drop (0.733 → 0.528) is policy-draw variance: no check fired in any failing 3c checker episode.
  - Per-construction cells have n = 32 and are descriptive only.

## 5. Remaining uncertainty and limitations

- **One backbone and one prompt configuration.** No competent larger policy or escalation baseline was run (no API batch was authorized).
- **The checker is exact because the public model is executable.**
  - Its 0-token cost and perfect social-handoff vetoes reflect that, not a learned or inferred relation.
  - The generic check shows what a model-based estimate of the same quantity achieves with this backbone.
- **The token criterion compares processed tokens only.** Wall-clock: checker_gate 7.9 s vs ask_first 5.9 s per episode, at concurrency 8 with prefix caching at the vLLM default. That would also fail a 10% time tolerance.
- **The gate's alternative value is a declared search lower bound,** not the best non-commit continuation. Missed opportunities, where the policy never proposes a good commitment, are not addressed by a veto gate. The audit attributes 0.06 per episode of lost return to them.
- **The selection-economics verdict is specific to this regime:** scripted public rules plus a declared finite model. It is not a proof that no perspective-allocation architecture can work.

## 6. Surviving claims and recommendation

**Original claims.**
- **C1/C2 (decision-value allocation beats alternatives at matched compute):** not supported here. Nothing costly remained to allocate.
- **C3–C5:** untested in this block.

**What does survive (development evidence only):**
1. A **joint, provenance-based relation representation** is necessary and sufficient for the handoff decisions in these constructions, where marginals are not (2d, 3a, 2e). This is a qualified engineering result and an elementary diagnostic, not a headline contribution.
2. An **action gate fed by an exact public-model checker** removes most of the local LLM's irreversible errors, especially wrong social handoffs (49/49 vetoes correct). It is clearly better than generic LLM verification at lower token cost.

   It is, however, a "call a symbolic solver" result. In this regime the solver alone (the Bayes planner, 0.885) outperforms every LLM-based condition, and the result does not support selective theory of mind.

**Recommendation:** freeze both branches as specified, and record the negative and positive findings above. If the research conversation wants to continue, the only direction this evidence motivates is a **regime change** in which perspective relations cannot be compiled cheaply:
- natural-language Tier 2 role-play with private information, where public rules are not machine-executable;
- comparing a targeted model-based relational check (courier route vs recipient belief, inferred jointly) against generic verification, with the frozen gate and the ask-first control.

**Measured cost basis for planning** (local backbone, per episode):
- direct: about 5.2k processed tokens and 4.6 s;
- gate with re-decisions: about 8.7k tokens;
- model-based checks add about 2.8k tokens per episode (1.18 checks per episode in generic_gate).

Choosing that regime is a scope decision for research review. Nothing beyond this block is started.

## 7. Bundle index

All evidence is under `reports/hybrid-block/`:
- `FINAL_REVIEW.md`, `cpu-gate.md` / `.json`;
- `trigger-audit.json` / `-rows.jsonl`, `token-forecast.json`, `rendered-t0.json`;
- `smoke.jsonl` / `smoke-summary.json`;
- `fallback-protocol.md`, `fallback-freeze.json`;
- `fallback-results.json`, `fallback-interventions.jsonl`, `bayes-reference.json`;
- `checkpoint.md`.

Source:
- `src/vomi/relational.py`, `src/officeminds/hybridfam.py`;
- `scripts/hybrid_*.py`, `scripts/run_hybrid_fallback.py`, `scripts/report_hybrid_fallback.py`;
- `prompts/hybrid-v1/check_system.txt`, `tests/test_hybrid.py`.

Commits: foundation `6d0579e`, freeze `b42589d`, results (this commit). Raw episodes live outside Git at the run path above, identified by the hashes listed.
