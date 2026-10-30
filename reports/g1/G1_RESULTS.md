# G1 results: symbolic twin of "cheap provenance, costly content" (D-023)

Date: 2026-10-30.
- **Pre-declared outcome: STOP.** A simple provenance rule performs as well as decision-value selection.
- One frozen evaluation pass. Protocol `G1_PROTOCOL.md`, frozen in `g1-freeze.json` at commit `ce3ac72` (freeze committed as `e921fb4`).
- `python scripts/g1_symbolic_twin.py run`, Windows CPython: 38.4 s CPU. Raw numbers in `g1-results.json`.
- No model calls, spending or text environment. Thresholds were not revised.

## Gate table (sparse condition; per-task return averaged over stakes ×1 and ×4)

| gate | measured | verdict |
|---|---|---|
| G1a sparsity | U_dv(0.04) = **0.137**. Return 0.9288 vs dense 0.9297 (−0.0009) | pass |
| G1b no cheap rule matches | `risk(θ)` with θ ∈ {0.05, 0.1, 0.2, 0.4} reaches within 0.02 of dv(0.04)'s return with *fewer* reads (θ = 0.05: 1.54 vs 1.63 reads/day, return 0.9271 vs 0.9288). `action_prov` equals dv's full-information point (0.9296 at 1.85 reads vs dv(0.005): 0.9297 at 1.85) | **stop** |
| G1c costly content matters | 37.8% of 10,584 comparable initial states have V_full − V_none ≥ 0.10 | pass |
| G1d allocation exists | STOP share 0.416 (in range), but **stakes flip share 0.000** | **stop** |
| G1e perspectives matter | dv's read set changes with the audience in 68.8% of chains, but dv beats perspective-blind `latest` by only +0.0016 return at 0.80× reads (the threshold is +0.02, or ≤ 0.6× reads). Perspective-aware `action_prov` scores 0.9228 vs dv's 0.9215 there | **stop** |
| **overall** | | **STOP** |

## Selector table (sparse; 2,000 days; 11.96 messages per day)

| selector | return | reads/day | U | dv(0.04) − selector [95% CI] |
|---|---|---|---|---|
| none (provenance only) | 0.8581 | 0 | 0 | +0.0708 [+0.069, +0.073] |
| dense (full information) | 0.9297 | 11.96 | 1.00 | — |
| structural (R or courier involved) | 0.9297 | 8.04 | 0.67 | −0.0008 |
| latest | 0.9271 | 1.97 | 0.165 | +0.0017 |
| **action_prov** | **0.9296** | **1.85** | 0.155 | −0.0008 |
| **risk(0.05)** and **risk(0.1)** | **0.9271** | **1.54** | 0.129 | +0.0017 |
| risk(0.2) / (0.4) / (0.8) / (1.6) | 0.9225 / 0.9144 / 0.8930 / 0.8665 | 1.43 / 1.23 / 0.74 / 0.17 | — | +0.006 / +0.014 / +0.036 / +0.062 |
| entropy(1) / (2) | 0.9274 / 0.9293 | 2.14 / 3.35 | — | +0.0015 / −0.0005 |
| random(1) / (2) | 0.9065 / 0.9232 | 2.14 / 3.35 | — | +0.022 / +0.006 |
| dv λ = 0.005 / 0.01 / 0.02 / **0.04** / 0.08 / 0.16 | 0.9297 / 0.9297 / 0.9297 / **0.9288** / 0.9272 / 0.8581 | 1.85 / 1.80 / 1.76 / **1.63** / 1.55 / 0 | — | — |

The CIs come from a paired bootstrap over days (2,000 resamples). Every return is identical at ×1 and ×4 except `risk` and `random`, for the reason given under "Why stakes never mattered" below.

**Dense-relevance control** (3 senders, all of them recipients; 4.45 messages per day; reported, not gated):
- dv(0.04) still reads only U = 0.229, with return 0.9365 vs full information 0.9374.
- `action_prov`: 0.9373 at U = 0.286. `risk(0.05)`: 0.9341 at U = 0.202.
- So even when every sender is a recipient, the decision needs only the latest message plus at most one courier source. The planned dense condition did not make relevance dense.

## What the result means

1. **There is something to buy, but a simple rule buys it.** Reading content is worth +0.07 per task over provenance alone (G1c passes), and only about 14% of messages are needed (G1a passes).
   - An action-specific provenance rule recovers all of that value: read R's latest message unless a courier heard it, plus that courier's source.
   - A recency × change-rate rule gets within 0.002 with fewer reads.
   - Exact decision-value selection adds nothing measurable. That is the stopping result D-023 anticipated.
2. **Perspectives change *which* read is needed, not the outcome margin.** In 69% of the paired chains, changing who heard which message changed dv's read set while the physical history stayed fixed. Example: when a courier heard R's latest message, dv reads nothing and gives, because provenance establishes alignment without revealing the office.
   - But a perspective-blind "read the latest" rule loses only 0.0016 return and spends 1.25× the reads. A perspective-aware simple rule (`action_prov`) matches dv.
3. **Why stakes never mattered.** In this generator, an uncertain handoff beats in-person search only if P(aligned) ≳ 0.93 at ×1.
   - Exact derivation: 0.9p − 0.8 ≥ 0.5s(1 − p), so p ≥ 0.929 at ×1, against search ≈ 0.75 + 0.1p.
   - The posterior almost never lands in (0.93, 1), so every selector gives only when alignment is certain and never risks the stakes-dependent error.
   - This is a property of the frozen generator (q ≥ 0.1, cheap 3-office search), not a code defect. It is reported, and it was not altered after measuring.

## Limitations

- **Symbolic twin only.** It says nothing about whether real text extraction is costly (G2), and G2 is not authorized.
- **Depth-1 couriers only.** Nested routing (what F thinks R believes) was not part of the frozen generator.
- **The `dense` condition did not create dense relevance in read terms.** That is reported as is.
- **Unit tests** (`tests/test_g1_twin.py`, 7 cases):
  - no messages means give;
  - provenance alignment without the value;
  - a perspective pair that changes the read;
  - the Markov prior;
  - the realized search order;
  - non-negative value of information;
  - determinism.

  A 5-day smoke on non-protocol seeds (99990000+) checked only code paths and invariants. No gate values were inspected before the pass.

## Consequence under D-023

**STOP.** With the decision-value advantage matched by simple provenance rules in its most favorable symbolic setting, the allocation claim returns to frozen (D-022 standing). No progression to G2.
