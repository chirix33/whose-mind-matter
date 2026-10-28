# Pilot model diagnostic: interface repairs, fixed unit contexts, crossed comparison (2026-10-28)

This follows the pilot review (`docs/decisions/2026-10-28-D013-pilot-review-repairs.md`). It is exploratory work on development data (dev-v2). The original pilot-v1 results, traces and reports are unchanged; an erratum sits at the top of `reports/pilot/pilot-report.md`.

**Status:** all local cells are done. **Every API cell is blocked:** `OPENAI_API_KEY` is not configured on this workstation (checked in both the Windows and WSL environments), so no paid call was made. The adapter, configuration, spend cap and frozen requests are ready (§5).

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

**Local gpt-oss-20b** (runs `unit-contexts-20261028-064729-654f39` (low) and `…064818-7d5f71` (medium); 4,096-token cap; concurrency 1). Full table: `reports/pilot/unit-contexts-results.md`.

| Effort | Package | Abstained | Correct (supported) | Incorrect (supported) | Unsupported | Leakage | Top-1 | Log score ↑ | CE vs. posterior ↓ | Tokens in / out / reasoning |
|---|---|---|---|---|---|---|---|---|---|---|
| low | pilot-v1 (original r2 run, stored, 16 ctx) | 0 | 11 | 1 | 4 | 0 | 0.69 | −1.87 | 1.99 | — |
| low | pilot-v1 (r3 replay) | 0 | 13 | 2 | 9 | 0 | 0.54 | −1.36 | 1.38 | 785 / 199 / 111 |
| low | pilot-v2 | 12 | 8 | 1 | 3 | 0 | 0.67 | −1.34 | 1.33 | 1,285 / 327 / 187 |
| medium | pilot-v1 | 0 | 13 | 2 | 9 | 0 | 0.54 | −2.49 | 2.44 | 820 / 1,049 / 946 |
| medium | pilot-v2 | 14 | 8 | 0 | 1 | 0 | 0.54 | −1.21 | 1.21 | 1,393 / 1,618 / 1,407 |

- **Package effect at low effort is small** on proper scores (Δ log score +0.02). pilot-v2 removes most person-level "unknown" assertions by abstaining instead, but it **over-abstains**: 12/24, including contexts the evidence settles.
  - The drop in the unsupported rate is partly mechanical, because abstentions leave the denominator.
- **At medium effort, pilot-v1 gets worse** (more confident wrong answers; Δ log score −1.13), while pilot-v2 improves (+1.28 over v1 at medium). So low effort is not the only limit, and package × effort interact.
- **Leakage (robot-known value attributed to a person without access): 0** in every cell. The audit found one robot-inference projection the rule misses (§3).
- **The original r2 outputs score worse than the r3 pilot-v1 replay** on the same 16 contexts (log score −0.19). That is a combined interface effect (people rules), not a pure model effect.

## 3. Evidence audit (10 contexts; `reports/pilot/unit-contexts-audit.md`)
The audit was done by the agent, on a sample chosen after viewing the results (not blind).
- **Scoring-reference artifact (uc14, uc16).** The simulator never creates nested beliefs from statements people overhear (`say` events update no one). The r3 public rules invite exactly those inferences, so the evidence posterior penalizes publicly defensible answers. This needs a ruling (review question 1).
- **Recipients know where they themselves are; the model often misses it** (3/10, both packages).
- **pilot-v2 support can be a rationalization:** contradictory hypotheses cite the same utterance (uc07), or a cited support contradicts the hypothesis (uc15). Structural validation is not entailment.
- **Reliability is over-read from a stated incentive** (0.8–0.9 against an evidence posterior of 0.5).
- **One case of the robot's own suspicion projected onto another person** (uc10, v1).

## 4. Crossed comparison (prespecified 12 instances; fixed allocation = every t0 candidate; pilot-v2; r3)
Run `crossed-20261028-065424-77d5cb` (concurrency 4; dirty paths recorded in the manifest).

| Cell (policy / notes) | n | Success | Mean return |
|---|---|---|---|
| local / local | 12 | 0.83 | +0.587 |
| local / direct (no units) | 12 | 0.92 | +0.696 |
| API / local, local / API, API / API, API / direct | — | **blocked** (no API key) | — |

With the repaired interface and grounding package, explicit notes for every t0 candidate still trail the local direct agent on this subset (n = 12; exploratory).

## 5. To run the API cells
1. Configure the key locally, in WSL (never in the repo or the chat), for example by adding `export OPENAI_API_KEY=...` to `~/.bashrc`. Optionally set the cap with `export OFFICEMINDS_API_CAP_USD=5` (the default is 5).
2. Then run:
   ```bash
   python3 scripts/run_unit_contexts.py --config configs/models/api_gpt_6_1_sol.json --effort low
   python3 scripts/run_crossed.py --cells api/local local/api api/api api/direct   # needs the local server for local sides
   python3 scripts/report_unit_contexts.py ~/officeminds-runs/unit-contexts/<local-low> ~/officeminds-runs/unit-contexts/<api-low>
   ```
3. The persistent ledger at `~/officeminds-runs/api-spend-ledger.json` refuses any call whose worst case would exceed the cap. Incomplete cells are recorded as blocked, not dropped.

**Spend estimate** (illustrative only, from the local runs' measured token volumes at Sol's listed $2 / $10 per million; tokenizers and reasoning use differ):
- fixed contexts: about $0.23 (or $0.48 with 3× output);
- the four crossed API cells: about $1.20 (or $2.38 with 3× output);
- total about $1.4–2.9.
