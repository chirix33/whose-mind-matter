# Hybrid block (D-019): Concept 2 fallback pilot protocol

Frozen before any pilot outcome. Its sha256 is pinned in `fallback-freeze.json` together with the code and prompts. Runner: `scripts/run_hybrid_fallback.py`. Analysis: `scripts/report_hybrid_fallback.py`, committed before the pilot starts.

**Question (brief §6).** Does action-triggered relational verification improve episode outcomes enough to justify its cost, beyond generic verification and a simple legal alternative? This is narrower than the original decision-value allocation claim.

## Design

- **Scenarios.** The dev-v3 generator's 12 constructions × 8 **fresh** seeds (20261400–07, never used before). Each seed gives each construction its own public and hidden draw.
  - Unpermuted variants only, at stakes ×1 and ×4: 192 states.
  - **Base scenario** = (seed, construction): 96 units.
- **Draws.** 2 policy draws per state and condition (temperature 1.0).
- **Conditions.** 4, so **1,536 episodes**: within the 2,304-rollout cap, with no hybrid rollouts used.
- **Model.** Local gpt-oss-20b (`openai/gpt-oss-20b@6cee5e8…`, vLLM 0.32.0, mxfp4).
  - Decoding: temperature 1.0, max_tokens 1024, reasoning effort low.
  - Up to 3 attempts per call; a truncation counts as a failed attempt. Concurrency 8.
- **Direct policy.** Unchanged from the repair block's `none` condition: `prompts/pilot-v1/policy_system.txt`, render r7 task card (people-rules r6 plus the numbered public model), visible ledger, physical summary, "MIND NOTES: (none …)". A test checks that the prompt is byte-identical.
- **Order.** Complete seed blocks (192 episodes), with condition order rotated within each block. Pairs share the state and environment; policy draws are independent.
- **Resume.** Interrupted blocks are logged in `aborted-episodes.jsonl` and re-run in full. No seed is selected or replaced.
- **Serving-time cap.** A seed block starts only if at least 15 min of the 2 h cap remains. Partial completion is reported as such.

## Conditions

1. **direct.** The policy's proposed action executes. A failed call falls back to `wait()`.
2. **checker_gate.** The direct policy plus the action gate below. The checker is the **public-model posterior tracker**:
   - exact enumeration of the disclosed finite hidden-variable model, conditioned on the robot-visible history only;
   - for give(c): P(c's route = recipient's room); for drop(o): P(recipient in o); plus the recipient-location distribution.
   - It is qualified equal to the referent engine on the hybrid families (cpu-gate §1).
   - Cost: CPU time, measured. No tokens.
3. **generic_gate.** The same policy and the identical gate. The checker is **one generic LLM verification call** (`prompts/hybrid-v1/check_system.txt`):
   - it sees the same task card, full history and physical summary, plus the proposed action;
   - it returns `p_success` and a probability for each office (JSON schema);
   - the location distribution is renormalized over offices not yet visited empty.
4. **ask_first.** The direct policy, plus one declared rule:
   - The *first* irreversible commitment proposed in the episode is replaced by `ask(person, query fact)`. The person is the proposed courier if present and not yet asked; otherwise the alphabetically first present person not yet asked.
   - The policy then decides normally, with the answer (possibly uninformative or misleading) in its history. Later commitments execute.
   - No extra calls beyond the ordinary decision for the extra step.

## Gate state machine (identical for both gate conditions)

1. The policy proposes an action. Non-commitments (move, ask, wait, deliver) execute.
2. **Trigger:** `give(person)` or `drop(office)`.
3. **Check.**
   - The estimates (p, location) are cached per (action, evidence signature). The signature covers every utterance and notice so far, the offices visited empty, and whether the recipient is visible.
   - A cache hit is free and does not count.
   - At most **4 counted checks per episode**. After that, commitments execute unchecked (logged).
   - A check that fails after 3 attempts lets the commitment execute unchecked (logged).
4. **Verdict.** Allow iff `J = -0.05 + p - (1-p)*0.5*stakes >= V_alt`.
   - V_alt is the declared in-person search: offices not yet visited empty, in descending estimated probability (ties in config order); deliver on sight; exact expected return within the remaining steps; timeouts are not penalized.
   - If the recipient is visible, V_alt = 0.95 (deliver now).
   - This is a capped approximate gate, **not a safety guarantee**.
5. **Veto.** One re-decision call. The blocked action is removed from the legal list, and one fixed line reports p, J and V_alt.
   - If the re-decision proposes another commitment, it is checked once (it counts, and is subject to the cap). If vetoed, the scripted search step executes.
   - If the re-decision fails after 3 attempts, the scripted search step executes.
6. **Scripted search step** (declared, counted): `deliver()` if the recipient is visible; otherwise a move toward the most probable office not yet visited empty, under that check's location estimate.

## Accounting (per episode)

- Calls by kind (decision, redecision, check), with attempts, failed attempts and fallbacks.
- Prompt, completion and reasoning tokens. The reasoning count is flagged when unknown.
- Summed call latency and episode wall-clock time (monotonic).
- Checker CPU seconds (checker_gate).
- **Processed tokens = prompt + completion**, all attempts. Completion includes reasoning for this backbone.
- Tokens are a within-backbone proxy. vLLM prefix caching is left at its default and reported; cached prefixes are not discounted.

## Analysis (pre-declared; `scripts/report_hybrid_fallback.py`)

- **Unit.** The base scenario (96). Per unit and condition, average the episodes over stakes and draws (4 each). Paired differences are taken per unit.
- **Intervals.** 95% stratified bootstrap over base scenarios, stratified by construction, 10,000 resamples, seed 0.
- **Primary.** Pooled mean return difference, checker_gate − direct.
- **Continue Concept 2 only if all hold:**
  - **(a)** checker_gate − direct ≥ **+0.05** (point estimate; CI reported).
  - **(b)** Against **each** of generic_gate and ask_first, either:
    - (i) Δreturn ≥ +0.03 with mean processed tokens at most 1.10× the comparator's; or
    - (ii) mean processed tokens at most 0.80× the comparator's, with Δreturn ≥ 0 and paired CI lower bound > −0.05.

    Route (ii) is labelled an efficiency signal. Latency and CPU are reported, and a material time regression is not hidden.
  - **(c)** The gain is not explained solely by suppressing valid commitments. checker_gate's success rate (episodes ending in success) must be ≥ direct's success rate − 0.05. Error, timeout and correct-commitment rates are all reported.
- **If a CI leaves (a) or (b) unresolved,** report "unresolved at this sample". The run is not extended.
- **If generic_gate ≈ checker_gate** (|Δ| < 0.03 and CI covering 0), report generic verification as the likely surviving contribution. It is not relabelled as perspective allocation.
- **Secondary, descriptive only:**
  - results by construction, by stakes, and by commitment class (social-belief give / physical drop / testimony drop);
  - vetoes of commitments that would have failed vs succeeded (evaluation replay);
  - re-decision outcomes, scripted fallbacks, cache hits, cap hits, check failures;
  - tokens and latency per condition.
- **Exclusions.** None. Errored episodes are reported and counted as missing pairs. Catastrophic failures are never deleted.
