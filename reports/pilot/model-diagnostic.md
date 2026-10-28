# Pilot model diagnostic: interface repairs, fixed unit contexts, crossed comparison (2026-10-28)

> **Erratum (2026-10-28, autonomous block):** in the §2 table, the local medium pilot-v2 row showed Incorrect (supported) = 0, so the row summed to 23. The raw records and the generated `unit-contexts-results.md` give **1** (14 abstained + 8 + 1 + 1 + 0 = 24). It was a transcription error in this hand-copied table; the generated table was correct. Corrected in place. Verified independently from the raw records.

This follows the pilot review (`docs/decisions/2026-10-28-D013-pilot-review-repairs.md`). It is exploratory work on development data (dev-v2). The original pilot-v1 results, traces and reports are unchanged; an erratum sits at the top of `reports/pilot/pilot-report.md`.

**Status:** every planned cell has now run, local and API.
- The API key loads from the gitignored repo `.env`. The first key's account had no credits (HTTP 429, zero spend); Ashraf replaced the key.
- **API spend: USD 1.31** under the USD 5 cap, from 266 billed calls in the persistent ledger:
  - one smoke call, $0.0001;
  - fixed contexts, about $0.39;
  - crossed cells, about $0.92.
- This is below the pre-run estimate of USD 1.4–2.9. Costs are estimated from reported usage × the configured list prices of $2 / $10 per million tokens.

## 1. Repairs (shared renderer r3; package pilot-v2; scoring v2)
- **A. Evidence in the policy interface:**
  - mind notes now show each unit's cited evidence IDs and short excerpts;
  - pilot-v2 adds per-hypothesis support (observation / testimony / access_inference);
  - the validator remains structural only.
- **B.** `unknown` (the person has no belief) is now separate from `insufficient_evidence` (the robot cannot tell). Scoring v2 has five categories plus abstention, and proper scores against both the truth and the evidence-grounded posterior.
- **C.** One neutral public "how people come to believe things" paragraph, shared by all arms and packages.
- **D.** A physically refuted claim marks K(speaker) `fact_refuted` (the belief may persist); refresh is no longer forced.

## 2. Fixed unit contexts (`unit-contexts-v1`, frozen before any new output)
**Selection** (rule in `scripts/freeze_unit_contexts.py`):
- 24 contexts: the 9 prespecified intervention states plus 15 chosen in sha256 order under declared quotas;
- one context per group, at most 4 per family;
- by unit type: 14 K1, 6 K2, 2 R1, 2 R2. The R1 target of 4 was not reachable under the per-group cap;
- by history depth: 16 at k = 0, 8 at k = 1;
- 6 with truth `unknown`, 4 with default-violating content;
- 16 have a stored original pilot-v1 (r2) output.

The per-family cap was raised from 3 to 4 before any output, because a cap of 3 left R1 at 1.

**Runs:**
- Local gpt-oss-20b: `unit-contexts-20261028-064729-654f39` (low) and `…064818-7d5f71` (medium). 4,096 output-token cap, temperature 0, concurrency 1.
- API gpt-6.1-sol: `unit-contexts-20261028-070945-72da94` (low; clean commit `70e3754`).
  - 16,000 output-token cap, because the API counts reasoning toward it.
  - Temperature is not sent, so each output is a single draw at the provider's default sampling.
  - Concurrency 1; 341 s wall clock.

Full table: `reports/pilot/unit-contexts-results.md`.

| Model | Effort | Package | Abstained | Correct (supported) | Incorrect (supported) | Unsupported | Leakage | Top-1 | Log score ↑ | CE vs. posterior ↓ | Tokens in / out / reasoning |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | low | pilot-v1 (original r2 run, stored, 16 ctx) | 0 | 11 | 1 | 4 | 0 | 0.69 | −1.87 | 1.99 | — |
| gpt-oss-20b | low | pilot-v1 (r3 replay) | 0 | 13 | 2 | 9 | 0 | 0.54 | −1.36 | 1.38 | 785 / 199 / 111 |
| gpt-oss-20b | low | pilot-v2 | 12 | 8 | 1 | 3 | 0 | 0.67 | −1.34 | 1.33 | 1,285 / 327 / 187 |
| gpt-oss-20b | medium | pilot-v1 | 0 | 13 | 2 | 9 | 0 | 0.54 | −2.49 | 2.44 | 820 / 1,049 / 946 |
| gpt-oss-20b | medium | pilot-v2 | 14 | 8 | **1** | 1 | 0 | 0.54 | −1.21 | 1.21 | 1,393 / 1,618 / 1,407 |
| **gpt-6.1-sol** | low | pilot-v1 | 0 | 14 | 3 | 7 | 0 | 0.58 | **−0.95** | **0.93** | 891 / 828* / 12 |
| **gpt-6.1-sol** | low | pilot-v2 | **20** | 4 | 0 | 0 | 0 | 0.50 | −1.09 | 1.08 | 1,411 / 334 / 3 |

\* The mean includes one incomplete attempt (uc02, pilot-v1). That attempt produced 16,000 output tokens with no reported reasoning before it was cut off. It cost about $0.16, was recorded as an incomplete attempt (not parsed), and the retry succeeded.

**Model effect** (paired, same 24 contexts and package):
- gpt-6.1-sol at low effort beats local gpt-oss-20b at low effort by **+0.40 log score** on pilot-v1 (CE +0.45).
- It also beats local at medium effort: +1.53 on pilot-v1 and +0.12 on pilot-v2.
- The categorical improvement is small: 7 vs. 9 unsupported-incorrect, top-1 0.58 vs. 0.54.
- The gain is mostly calibration (less confident mass on wrong values), not more correct top answers.
- At low effort the API model reports almost no reasoning tokens (mean 12 for pilot-v1, 3 for pilot-v2).

**Package effect depends on the model:**
- On the API model, pilot-v2 is **worse** than v1 (Δ log score −0.13).
- It abstains on **20/24** contexts (local low: 12; local medium: 14), including contexts whose evidence posterior is 1.00 (uc17–uc19, uc21, uc23).
- Its 4 attributed outputs are all correct-supported. The low unsupported rate is therefore almost entirely abstention.
- **The stronger model makes pilot-v2's over-abstention worse, not better.** This points to the package (instructions and status design), not model capacity: this is review question 2.

**Shared misses:**
- **uc21** (K(frank), posterior 1.00): every model and package cell outputs `unknown` or abstains.
- **uc02** (posterior 0.95): every model and package cell outputs a wrong value or abstains.
- **uc14** (overheard `say`; review question 1): the API model also attributes a location (room_12). This is consistent with the public rules, so it is still the scoring-reference conflict.

**Leakage: 0** in every cell.

## 3. Evidence audit (10 contexts; `reports/pilot/unit-contexts-audit.md`)
The audit was done by the agent, on a sample chosen after viewing the local results (not blind). It covers the local runs only. The API outputs were not separately audited.
- **Scoring-reference artifact (uc14, uc16).** The simulator never creates nested beliefs from statements people overhear (`say` events update no one). The r3 public rules invite exactly those inferences, so the evidence posterior penalizes publicly defensible answers. This needs a ruling (review question 1).
- **Recipients know where they themselves are; the model often misses it** (3/10, both packages).
- **pilot-v2 support can be a rationalization:** contradictory hypotheses cite the same utterance (uc07), or a cited support contradicts the hypothesis (uc15). Structural validation is not entailment.
- **Reliability is over-read from a stated incentive** (0.8–0.9 against an evidence posterior of 0.5).
- **One case of the robot's own suspicion projected onto another person** (uc10, v1).

## 4. Crossed comparison (prespecified 12 instances; fixed allocation = every t0 candidate; pilot-v2; r3)
**Runs:**
- `crossed-20261028-065424-77d5cb`: local cells, concurrency 4.
- `crossed-20261028-071537-f647df`: API cells, clean commit `dffe4c6`, concurrency 4, 243 s.

**Settings:**
- Output-token caps: local 4,096; API 16,000.
- Each API episode is one stochastic draw. Local decoding is temperature 0.
- There are no replicates, so the API cells carry sampling noise that this table does not show.

| Cell (policy / notes) | n | Success | Errors / timeouts | Mean return | Mean steps | Decision calls | Unit calls |
|---|---|---|---|---|---|---|---|
| local / local | 12 | 10 | 1 / 1 | +0.587 | 4.08 | 49 | 57 |
| local / direct (no units) | 12 | 11 | 1 / 0 | +0.696 | 3.58 | 43 | — |
| local / API | 12 | 10 | 2 / 0 | +0.554 | 3.92 | 47 | 57 |
| API / local | 12 | 11 | 1 / 0 | +0.750 | 2.50 | 30 | 57 (3 failed local attempts, retried) |
| API / API | 12 | **12** | 0 / 0 | **+0.833** | 3.33 | 40 | 57 |
| API / direct (no units) | 12 | 11 | 1 / 0 | +0.742 | 2.67 | 32 | — |

**Paired per-instance differences in return** (n = 12; better / worse / tie):

| Comparison | Mean Δ | B / W / T | What it isolates |
|---|---|---|---|
| API/local − local/local | **+0.163** | 9 / 1 / 2 | policy swap, notes fixed |
| local/API − local/local | −0.033 | 4 / 3 / 5 | notes swap, local policy fixed |
| API/API − API/local | +0.083 | 1 / 3 / 8 | notes swap, API policy fixed |
| local/local − local/direct | −0.108 | 2 / 5 / 5 | notes vs. none, local policy |
| local/API − local/direct | −0.142 | 2 / 7 / 3 | better notes vs. none, local policy |
| API/local − API/direct | +0.008 | 1 / 0 / 11 | notes vs. none, API policy |
| API/API − API/direct | +0.092 | 2 / 3 / 7 | better notes vs. none, API policy |
| API/direct − local/direct | +0.046 | 8 / 2 / 2 | policy swap, no notes |

**Reading (exploratory; n = 12; one draw per API episode; no inferential claim):**
- **The policy model drives the gain; the notes model does not.** Swapping in the API policy helps on 9 of 12 instances. Swapping in API notes under the local policy does not help (−0.033), and under the API policy it changes 4 of 12 outcomes in both directions.
- **The local policy is hurt by notes, whichever model wrote them** (−0.108 local notes, −0.142 API notes, vs. direct). So the earlier local/local deficit is not just poor local notes: this policy uses notes badly.
- **With the API policy, notes are roughly neutral.** API/local ties direct on 11 of 12. The API/API mean advantage (+0.092) comes from a single instance, `conflict-g0-stakes1` (+1.30); without it the mean is −0.018.
  - In that instance the API/API notes are nearly identical to the local/API notes. Both put about 0.9 on suite_east for the two obstructive speakers; the truth is suite_west.
  - The API/API policy succeeded by checking both suites rather than dropping at suite_east. That is a policy draw, not better note content.
- **The API policy also takes fewer steps** (2.5–3.3 vs. 3.6–4.1), uses few reasoning tokens at low effort (269–433 per cell, vs. 3,729–5,205 for the local policy), and produced no failed decision calls.
- **Answer to the review's crossed question, on this subset:**
  - better notes alone do not help;
  - the local policy struggles to use notes of either quality;
  - a stronger policy is better with or without notes and does not yet show a reliable gain from them.

## 5. Spend and cost accounting
- **Ledger:** `~/officeminds-runs/api-spend-ledger.json`; USD 1.3123 over 266 calls, including retries and the incomplete 16,000-token attempt.
- **Ledger fix before the crossed run** (commit `dffe4c6`): `SpendLedger` had no lock, and run_crossed shares it across 4 threads. Concurrent calls could lose increments, corrupt the file, or each pass the cap check. It now:
  - holds a lock;
  - reserves each in-flight call's worst case and releases it on transport errors;
  - writes the file atomically.

  The fixed-context run ran sequentially before this fix, so it was not affected.
- **Comparability:** tokens from the two tokenizers are not comparable compute. API latency includes network time and provider queueing. Local latency was measured at concurrency 4 on one RTX 5090 with the server warm.
