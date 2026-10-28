# Round 1 results: fixed contexts under scoring v3

Runs: `unit-contexts-20261028-064729-654f39`, `unit-contexts-20261028-064818-7d5f71`, `unit-contexts-20261028-070945-72da94`, `unit-contexts-20261028-083007-1512c0`, `unit-contexts-20261028-084100-d7f4d5`, `unit-contexts-20261028-084229-e8ab65`. Contexts: the 24 of `unit-contexts-v1` (r4 rows use `reports/autonomous-block/unit-contexts-v1-r4.jsonl`). Development data; exploratory.
Ambiguity policy: `reports/autonomous-block/reference-audit.json` (written before outputs). Primary block = 19 consistent contexts; ambiguous = uc02, uc06, uc07, uc10, uc11.
Hallucination-type = unsupported_committed + leakage. r3 rows are earlier runs rescored with v3 (contract r3, not re-run).

## Primary (consistent contexts): category counts (each row sums to n)

| cell (model/effort/rules/package) | cap | n | correct_supported | supported_spread | correct_unsupported | incorrect_supported | leakage | unsupported_committed | unsupported_hedged | ambiguous_reference | abstained | invalid | hallucination-type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 16000 | 19 | 8 | 7 | 0 | 1 | 0 | 1 | 2 | 0 | 0 | 0 | 1 |
| gpt-6.1-sol/low/r3/pilot-v2 | 16000 | 19 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 |
| gpt-6.1-sol/low/r5/pilot-v1 | 6000 | 19 | 10 | 8 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gpt-6.1-sol/low/r5/pilot-v2 | 6000 | 19 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 |
| gpt-6.1-sol/low/r5/pilot-v2.1 | 6000 | 19 | 10 | 8 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 4096 | 19 | 8 | 4 | 0 | 1 | 0 | 3 | 3 | 0 | 0 | 0 | 3 |
| gpt-oss-20b/low/r3/pilot-v2 | 4096 | 19 | 5 | 2 | 0 | 1 | 0 | 2 | 0 | 0 | 9 | 0 | 2 |
| gpt-oss-20b/low/r4/pilot-v1 | 4096 | 19 | 7 | 5 | 0 | 0 | 2 | 4 | 1 | 0 | 0 | 0 | 6 |
| gpt-oss-20b/low/r4/pilot-v2 | 4096 | 19 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 14 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 4096 | 19 | 9 | 5 | 0 | 1 | 1 | 3 | 0 | 0 | 0 | 0 | 4 |
| gpt-oss-20b/low/r5/pilot-v1 | 4096 | 19 | 9 | 5 | 0 | 0 | 1 | 3 | 1 | 0 | 0 | 0 | 4 |
| gpt-oss-20b/low/r5/pilot-v2 | 4096 | 19 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 |
| gpt-oss-20b/low/r5/pilot-v2.1 | 4096 | 19 | 10 | 6 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 3 |
| gpt-oss-20b/medium/r3/pilot-v1 | 4096 | 19 | 7 | 5 | 0 | 1 | 0 | 5 | 1 | 0 | 0 | 0 | 5 |
| gpt-oss-20b/medium/r3/pilot-v2 | 4096 | 19 | 4 | 2 | 0 | 1 | 0 | 1 | 0 | 0 | 11 | 0 | 1 |

## Ambiguous contexts: category counts (each row sums to n)

| cell (model/effort/rules/package) | cap | n | correct_supported | supported_spread | correct_unsupported | incorrect_supported | leakage | unsupported_committed | unsupported_hedged | ambiguous_reference | abstained | invalid | hallucination-type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 16000 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-6.1-sol/low/r3/pilot-v2 | 16000 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| gpt-6.1-sol/low/r5/pilot-v1 | 6000 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-6.1-sol/low/r5/pilot-v2 | 6000 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| gpt-6.1-sol/low/r5/pilot-v2.1 | 6000 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 4096 | 5 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-oss-20b/low/r3/pilot-v2 | 4096 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v1 | 4096 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v2 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 4096 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-oss-20b/low/r5/pilot-v1 | 4096 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-oss-20b/low/r5/pilot-v2 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| gpt-oss-20b/low/r5/pilot-v2.1 | 4096 | 5 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| gpt-oss-20b/medium/r3/pilot-v1 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-oss-20b/medium/r3/pilot-v2 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |

## Primary contexts: status-agnostic content categories (Opus gate item 3)

Every valid output is categorized by its content, whatever its status, so a package cannot hide content inside abstentions (pilot-v2's insufficient_evidence covers what pilot-v2.1 calls uncertain). Coverage by status is its own column. Unsupported mass = mean probability on values the reference gives < 0.2 (item 4). **Limitation:** the committed/hedged line (top p >= 0.5) is crude; unsupported mass complements it.

| cell | n | correct_supported | supported_spread | correct_unsupported | incorrect_supported | leakage | unsupported_committed | unsupported_hedged | ambiguous_reference | invalid | hallucination-type (content) | mean unsupported mass | status-abstained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 19 | 8 | 7 | 0 | 1 | 0 | 1 | 2 | 0 | 0 | 1 | 0.29 | 0 |
| gpt-6.1-sol/low/r3/pilot-v2 | 19 | 5 | 8 | 0 | 1 | 2 | 1 | 2 | 0 | 0 | 3 | 0.30 | 16 |
| gpt-6.1-sol/low/r5/pilot-v1 | 19 | 10 | 8 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.18 | 0 |
| gpt-6.1-sol/low/r5/pilot-v2 | 19 | 8 | 7 | 0 | 1 | 2 | 0 | 1 | 0 | 0 | 2 | 0.27 | 16 |
| gpt-6.1-sol/low/r5/pilot-v2.1 | 19 | 10 | 8 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.12 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 19 | 8 | 4 | 0 | 1 | 0 | 3 | 3 | 0 | 0 | 3 | 0.31 | 0 |
| gpt-oss-20b/low/r3/pilot-v2 | 19 | 7 | 9 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 2 | 0.36 | 9 |
| gpt-oss-20b/low/r4/pilot-v1 | 19 | 7 | 5 | 0 | 0 | 2 | 4 | 1 | 0 | 0 | 6 | 0.37 | 0 |
| gpt-oss-20b/low/r4/pilot-v2 | 19 | 4 | 13 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0.33 | 14 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 19 | 9 | 5 | 0 | 1 | 1 | 3 | 0 | 0 | 0 | 4 | 0.23 | 0 |
| gpt-oss-20b/low/r5/pilot-v1 | 19 | 9 | 5 | 0 | 0 | 1 | 3 | 1 | 0 | 0 | 4 | 0.29 | 0 |
| gpt-oss-20b/low/r5/pilot-v2 | 19 | 7 | 10 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0.29 | 13 |
| gpt-oss-20b/low/r5/pilot-v2.1 | 19 | 10 | 6 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 3 | 0.18 | 0 |
| gpt-oss-20b/medium/r3/pilot-v1 | 19 | 7 | 5 | 0 | 1 | 0 | 5 | 1 | 0 | 0 | 5 | 0.36 | 0 |
| gpt-oss-20b/medium/r3/pilot-v2 | 19 | 5 | 9 | 0 | 1 | 1 | 3 | 0 | 0 | 0 | 4 | 0.25 | 11 |

## Proper scores and coverage (all 24 contexts)

Over all valid outputs (abstentions included through their distributions) and over attributed outputs only. Log score vs truth (higher better, 1e-3 floor); Brier, CE vs reference posterior and TV vs posterior: lower better.

| cell | coverage (attributed/24) | invalid | log score | Brier | CE vs post. | TV vs post. | log score (attributed) | mean tokens in/out/reasoning | incomplete attempts |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 24/24 | 0 | -0.95 | 0.53 | 0.93 | 0.34 | -0.95 | 891/828/12 | 1 |
| gpt-6.1-sol/low/r3/pilot-v2 | 4/24 | 0 | -1.09 | 0.56 | 1.08 | 0.34 | -0.16 | 1411/334/3 | 0 |
| gpt-6.1-sol/low/r5/pilot-v1 | 24/24 | 0 | -0.76 | 0.44 | 0.77 | 0.26 | -0.76 | 1262/654/13 | 2 |
| gpt-6.1-sol/low/r5/pilot-v2 | 5/24 | 0 | -0.76 | 0.48 | 0.77 | 0.31 | -0.25 | 1721/331/13 | 0 |
| gpt-6.1-sol/low/r5/pilot-v2.1 | 24/24 | 0 | -0.67 | 0.42 | 0.68 | 0.22 | -0.67 | 1896/308/7 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 24/24 | 0 | -1.36 | 0.65 | 1.38 | 0.36 | -1.36 | 785/199/111 | 0 |
| gpt-oss-20b/low/r3/pilot-v2 | 12/24 | 0 | -1.34 | 0.62 | 1.33 | 0.40 | -1.58 | 1285/327/187 | 0 |
| gpt-oss-20b/low/r4/pilot-v1 | 24/24 | 0 | -2.01 | 0.74 | 2.08 | 0.41 | -2.01 | 1041/200/118 | 0 |
| gpt-oss-20b/low/r4/pilot-v2 | 7/24 | 0 | -1.01 | 0.52 | 1.06 | 0.33 | -0.20 | 1541/359/230 | 0 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 24/24 | 0 | -1.70 | 0.68 | 1.75 | 0.33 | -1.70 | 1782/329/194 | 0 |
| gpt-oss-20b/low/r5/pilot-v1 | 24/24 | 0 | -1.58 | 0.62 | 1.68 | 0.35 | -1.58 | 1095/195/116 | 0 |
| gpt-oss-20b/low/r5/pilot-v2 | 8/24 | 0 | -0.94 | 0.47 | 1.03 | 0.32 | -0.10 | 1595/412/270 | 0 |
| gpt-oss-20b/low/r5/pilot-v2.1 | 24/24 | 0 | -1.48 | 0.56 | 1.56 | 0.27 | -1.48 | 1842/345/206 | 0 |
| gpt-oss-20b/medium/r3/pilot-v1 | 24/24 | 0 | -2.49 | 0.84 | 2.44 | 0.43 | -2.49 | 820/1049/946 | 1 |
| gpt-oss-20b/medium/r3/pilot-v2 | 10/24 | 0 | -1.21 | 0.57 | 1.21 | 0.27 | -0.61 | 1393/1618/1407 | 1 |

## Proper scores on the 19 consistent contexts only (Opus gate item 5)

In the flagged contexts CE/TV mostly measure undisclosed generator base rates, so the primary comparison uses these rows. Note: uc03, uc20, uc21, uc22 have posterior 1.0 only because people without an incentive never lie in the generator; CE/TV there penalize hedges that rule 6 invites.

| cell | n | log score | Brier | CE vs post. | TV vs post. | mean unsupported mass |
|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 19 | -0.82 | 0.48 | 0.82 | 0.29 | 0.29 |
| gpt-6.1-sol/low/r3/pilot-v2 | 19 | -1.12 | 0.56 | 1.12 | 0.32 | 0.30 |
| gpt-6.1-sol/low/r5/pilot-v1 | 19 | -0.56 | 0.33 | 0.56 | 0.19 | 0.18 |
| gpt-6.1-sol/low/r5/pilot-v2 | 19 | -0.77 | 0.49 | 0.77 | 0.29 | 0.27 |
| gpt-6.1-sol/low/r5/pilot-v2.1 | 19 | -0.49 | 0.31 | 0.49 | 0.14 | 0.12 |
| gpt-oss-20b/low/r3/pilot-v1 | 19 | -1.38 | 0.62 | 1.40 | 0.33 | 0.31 |
| gpt-oss-20b/low/r3/pilot-v2 | 19 | -1.46 | 0.64 | 1.44 | 0.39 | 0.36 |
| gpt-oss-20b/low/r4/pilot-v1 | 19 | -1.77 | 0.70 | 1.81 | 0.38 | 0.37 |
| gpt-oss-20b/low/r4/pilot-v2 | 19 | -1.12 | 0.56 | 1.12 | 0.33 | 0.33 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 19 | -1.39 | 0.62 | 1.39 | 0.27 | 0.23 |
| gpt-oss-20b/low/r5/pilot-v1 | 19 | -1.23 | 0.54 | 1.29 | 0.31 | 0.29 |
| gpt-oss-20b/low/r5/pilot-v2 | 19 | -1.01 | 0.49 | 1.07 | 0.31 | 0.29 |
| gpt-oss-20b/low/r5/pilot-v2.1 | 19 | -1.32 | 0.47 | 1.37 | 0.21 | 0.18 |
| gpt-oss-20b/medium/r3/pilot-v1 | 19 | -2.28 | 0.78 | 2.20 | 0.38 | 0.36 |
| gpt-oss-20b/medium/r3/pilot-v2 | 19 | -1.42 | 0.64 | 1.36 | 0.28 | 0.25 |

## Paired comparisons on the same 19 consistent contexts (B vs A)

Positive Δ log / Δ CE / Δ TV = B better. Hallucination-type and unsupported mass use the status-agnostic content category. Δ abstentions counts all 24 contexts.

| effect | B vs A | contexts | Δ log score | Δ CE (negated) | Δ TV (negated) | Δ hallucination-type | Δ unsupported mass | Δ abstentions |
|---|---|---|---|---|---|---|---|---|
| package (same rules) | gpt-6.1-sol/low/r3/pilot-v2 vs gpt-6.1-sol/low/r3/pilot-v1 | 19 | -0.30 | -0.31 | -0.02 | +2 | +0.01 | +20 |
| rules r3 -> r5 + output cap [6000, 16000] + fresh sampled draw (descriptive only) | gpt-6.1-sol/low/r5/pilot-v1 vs gpt-6.1-sol/low/r3/pilot-v1 | 19 | +0.27 | +0.26 | +0.11 | -1 | -0.11 | +0 |
| model (same effort/rules/package) | gpt-oss-20b/low/r3/pilot-v1 vs gpt-6.1-sol/low/r3/pilot-v1 | 19 | -0.56 | -0.59 | -0.04 | +2 | +0.01 | +0 |
| rules r3 -> r5 + output cap [6000, 16000] + fresh sampled draw (descriptive only) | gpt-6.1-sol/low/r5/pilot-v2 vs gpt-6.1-sol/low/r3/pilot-v2 | 19 | +0.35 | +0.35 | +0.03 | -1 | -0.03 | -1 |
| model (same effort/rules/package) | gpt-oss-20b/low/r3/pilot-v2 vs gpt-6.1-sol/low/r3/pilot-v2 | 19 | -0.34 | -0.31 | -0.08 | -1 | +0.06 | -8 |
| package (same rules) | gpt-6.1-sol/low/r5/pilot-v2 vs gpt-6.1-sol/low/r5/pilot-v1 | 19 | -0.21 | -0.21 | -0.10 | +2 | +0.09 | +19 |
| package (same rules) | gpt-6.1-sol/low/r5/pilot-v2.1 vs gpt-6.1-sol/low/r5/pilot-v1 | 19 | +0.07 | +0.07 | +0.05 | +0 | -0.06 | +0 |
| model (same effort/rules/package) | gpt-oss-20b/low/r5/pilot-v1 vs gpt-6.1-sol/low/r5/pilot-v1 | 19 | -0.67 | -0.73 | -0.12 | +4 | +0.11 | +0 |
| package (same rules) | gpt-6.1-sol/low/r5/pilot-v2.1 vs gpt-6.1-sol/low/r5/pilot-v2 | 19 | +0.28 | +0.28 | +0.15 | -2 | -0.15 | -19 |
| model (same effort/rules/package) | gpt-oss-20b/low/r5/pilot-v2 vs gpt-6.1-sol/low/r5/pilot-v2 | 19 | -0.24 | -0.30 | -0.02 | -1 | +0.02 | -3 |
| model (same effort/rules/package) | gpt-oss-20b/low/r5/pilot-v2.1 vs gpt-6.1-sol/low/r5/pilot-v2.1 | 19 | -0.82 | -0.89 | -0.06 | +3 | +0.06 | +0 |
| package (same rules) | gpt-oss-20b/low/r3/pilot-v2 vs gpt-oss-20b/low/r3/pilot-v1 | 19 | -0.08 | -0.03 | -0.06 | -1 | +0.05 | +12 |
| rules r3 -> r4 (same package; combined rules effect) | gpt-oss-20b/low/r4/pilot-v1 vs gpt-oss-20b/low/r3/pilot-v1 | 19 | -0.39 | -0.41 | -0.05 | +3 | +0.06 | +0 |
| rules r3 -> r5 (same package; combined rules effect) | gpt-oss-20b/low/r5/pilot-v1 vs gpt-oss-20b/low/r3/pilot-v1 | 19 | +0.15 | +0.12 | +0.02 | +1 | -0.02 | +0 |
| rules r3 -> r4 (same package; combined rules effect) | gpt-oss-20b/low/r4/pilot-v2 vs gpt-oss-20b/low/r3/pilot-v2 | 19 | +0.34 | +0.31 | +0.06 | -1 | -0.02 | +5 |
| rules r3 -> r5 (same package; combined rules effect) | gpt-oss-20b/low/r5/pilot-v2 vs gpt-oss-20b/low/r3/pilot-v2 | 19 | +0.45 | +0.37 | +0.08 | -1 | -0.07 | +4 |
| package (same rules) | gpt-oss-20b/low/r4/pilot-v2 vs gpt-oss-20b/low/r4/pilot-v1 | 19 | +0.65 | +0.69 | +0.05 | -5 | -0.03 | +17 |
| package (same rules) | gpt-oss-20b/low/r4/pilot-v2.1 vs gpt-oss-20b/low/r4/pilot-v1 | 19 | +0.39 | +0.42 | +0.11 | -2 | -0.13 | +0 |
| rules r4 -> r5 (same package; combined rules effect) | gpt-oss-20b/low/r5/pilot-v1 vs gpt-oss-20b/low/r4/pilot-v1 | 19 | +0.54 | +0.52 | +0.07 | -2 | -0.08 | +0 |
| package (same rules) | gpt-oss-20b/low/r4/pilot-v2.1 vs gpt-oss-20b/low/r4/pilot-v2 | 19 | -0.26 | -0.26 | +0.06 | +3 | -0.10 | -17 |
| rules r4 -> r5 (same package; combined rules effect) | gpt-oss-20b/low/r5/pilot-v2 vs gpt-oss-20b/low/r4/pilot-v2 | 19 | +0.11 | +0.05 | +0.02 | +0 | -0.04 | -1 |
| rules r4 -> r5 (same package; combined rules effect) | gpt-oss-20b/low/r5/pilot-v2.1 vs gpt-oss-20b/low/r4/pilot-v2.1 | 19 | +0.07 | +0.02 | +0.07 | -1 | -0.05 | +0 |
| package (same rules) | gpt-oss-20b/low/r5/pilot-v2 vs gpt-oss-20b/low/r5/pilot-v1 | 19 | +0.22 | +0.22 | -0.00 | -3 | +0.00 | +16 |
| package (same rules) | gpt-oss-20b/low/r5/pilot-v2.1 vs gpt-oss-20b/low/r5/pilot-v1 | 19 | -0.09 | -0.09 | +0.10 | -1 | -0.10 | +0 |
| package (same rules) | gpt-oss-20b/low/r5/pilot-v2.1 vs gpt-oss-20b/low/r5/pilot-v2 | 19 | -0.30 | -0.30 | +0.10 | +2 | -0.10 | -16 |
| package (same rules) | gpt-oss-20b/medium/r3/pilot-v2 vs gpt-oss-20b/medium/r3/pilot-v1 | 19 | +0.86 | +0.84 | +0.11 | -1 | -0.11 | +14 |

## Per-context top value / category

| ctx | ref | unit | truth | posterior top (p) | gpt-6.1-sol/low/r3/pilot-v1 | gpt-6.1-sol/low/r3/pilot-v2 | gpt-6.1-sol/low/r5/pilot-v1 | gpt-6.1-sol/low/r5/pilot-v2 | gpt-6.1-sol/low/r5/pilot-v2.1 | gpt-oss-20b/low/r3/pilot-v1 | gpt-oss-20b/low/r3/pilot-v2 | gpt-oss-20b/low/r4/pilot-v1 | gpt-oss-20b/low/r4/pilot-v2 | gpt-oss-20b/low/r4/pilot-v2.1 | gpt-oss-20b/low/r5/pilot-v1 | gpt-oss-20b/low/r5/pilot-v2 | gpt-oss-20b/low/r5/pilot-v2.1 | gpt-oss-20b/medium/r3/pilot-v1 | gpt-oss-20b/medium/r3/pilot-v2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| uc01 | ok | K(wen) | desk_9 | desk_3 (0.50) | desk_9 0.40 / supported_spread | desk_9 0.45 / abstained [insufficient_evidence] | desk_9 0.35 / supported_spread | desk_9 0.45 / abstained [insufficient_evidence] | desk_9 0.45 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | desk_9 0.50 / supported_spread [attributed] | desk_9 0.50 / supported_spread | desk_9 0.50 / supported_spread [attributed] | desk_9 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | desk_9 0.50 / supported_spread [attributed] | unknown 1.00 / unsupported_committed [grounded] | desk_9 0.50 / supported_spread | desk_9 0.50 / supported_spread [attributed] |
| uc02 | AMB | K(judy) | office_b | office_b (0.95) | office_b 0.40 / supported_spread | office_b 0.50 / abstained [insufficient_evidence] | office_b 0.50 / supported_spread | office_b 0.50 / abstained [insufficient_evidence] | office_b 0.50 / supported_spread [uncertain] | unknown 0.90 / ambiguous_reference | unknown 0.34 / abstained [insufficient_evidence] | office_b 0.50 / supported_spread | office_b 0.50 / abstained [insufficient_evidence] | office_b 0.50 / supported_spread [uncertain] | office_b 0.50 / supported_spread | office_b 0.33 / abstained [insufficient_evidence] | office_b 0.50 / supported_spread [uncertain] | unknown 1.00 / ambiguous_reference | office_b 0.50 / abstained [insufficient_evidence] |
| uc03 | ok | K(grace) | lab_south | lab_south (1.00) | lab_south 0.80 / correct_supported | lab_south 0.90 / correct_supported [attributed] | lab_south 0.80 / correct_supported | lab_south 0.85 / correct_supported [attributed] | lab_south 0.85 / correct_supported [grounded] | lab_south 1.00 / correct_supported | lab_south 1.00 / correct_supported [attributed] | lab_south 1.00 / correct_supported | lab_south 1.00 / correct_supported [attributed] | lab_south 1.00 / correct_supported [grounded] | lab_south 1.00 / correct_supported | lab_south 1.00 / correct_supported [attributed] | lab_south 1.00 / correct_supported [grounded] | lab_south 1.00 / correct_supported | lab_south 0.90 / correct_supported [attributed] |
| uc04 | ok | K(carol) | office_a | office_a (0.50) | office_a 0.45 / supported_spread | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | office_a 0.33 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed | office_a 0.33 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | office_a 0.33 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread [uncertain] | office_a 0.33 / supported_spread | office_a 0.50 / abstained [insufficient_evidence] |
| uc05 | ok | K(leo) | room_12 | room_12 (0.50) | room_12 0.33 / supported_spread | room_12 0.45 / abstained [insufficient_evidence] | room_12 0.50 / supported_spread | room_12 0.50 / abstained [insufficient_evidence] | room_12 0.50 / supported_spread [uncertain] | unknown 0.90 / unsupported_committed | room_12 0.33 / abstained [insufficient_evidence] | unknown 0.90 / unsupported_committed | room_12 0.33 / abstained [insufficient_evidence] | room_12 0.50 / supported_spread [uncertain] | room_12 0.33 / supported_spread | room_12 0.33 / abstained [insufficient_evidence] | room_12 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | room_12 0.50 / abstained [insufficient_evidence] |
| uc06 | AMB | K(mia) | room_7 | room_7 (0.97) | room_7 0.45 / correct_supported | room_7 0.55 / abstained [insufficient_evidence] | room_7 0.50 / correct_supported | room_7 0.55 / correct_supported [attributed] | room_7 0.50 / correct_supported [uncertain] | room_7 1.00 / correct_supported | room_7 1.00 / correct_supported [attributed] | room_7 1.00 / correct_supported | room_7 1.00 / correct_supported [attributed] | room_7 1.00 / correct_supported [grounded] | room_7 1.00 / correct_supported | room_7 1.00 / correct_supported [attributed] | room_7 1.00 / correct_supported [grounded] | room_7 0.90 / correct_supported | room_7 1.00 / correct_supported [attributed] |
| uc07 | AMB | K(heidi) | desk_3 | desk_3 (0.87) | desk_3 0.80 / correct_supported | desk_3 0.80 / correct_supported [attributed] | desk_3 0.80 / correct_supported | desk_3 0.85 / correct_supported [attributed] | desk_3 0.85 / correct_supported [grounded] | desk_3 0.50 / supported_spread | unknown 0.34 / ambiguous_reference [attributed] | desk_3 1.00 / correct_supported | desk_3 1.00 / correct_supported [attributed] | desk_3 1.00 / correct_supported [grounded] | desk_3 1.00 / correct_supported | desk_3 1.00 / correct_supported [attributed] | desk_3 1.00 / correct_supported [grounded] | desk_3 0.85 / correct_supported | desk_3 1.00 / correct_supported [attributed] |
| uc08 | ok | K(yara) | desk_9 | desk_3 (0.50) | desk_9 0.45 / supported_spread | desk_9 0.50 / abstained [insufficient_evidence] | desk_9 0.50 / supported_spread | desk_9 0.48 / abstained [insufficient_evidence] | desk_9 0.50 / supported_spread [uncertain] | desk_9 0.50 / supported_spread | desk_9 0.33 / abstained [insufficient_evidence] | desk_9 0.50 / supported_spread | desk_9 0.33 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed [grounded] | desk_9 0.50 / supported_spread | desk_9 0.50 / abstained [insufficient_evidence] | desk_9 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | desk_9 0.50 / abstained [insufficient_evidence] |
| uc09 | ok | K(dave) | lab_north | lab_north (0.50) | lab_north 0.40 / supported_spread | lab_north 0.48 / abstained [insufficient_evidence] | lab_north 0.40 / supported_spread | lab_north 0.45 / abstained [insufficient_evidence] | lab_north 0.40 / supported_spread [uncertain] | lab_north 0.50 / supported_spread | lab_north 0.50 / supported_spread [attributed] | lab_north 0.50 / supported_spread | lab_north 0.50 / supported_spread [attributed] | unknown 0.95 / unsupported_committed [uncertain] | lab_north 0.50 / supported_spread | lab_north 0.50 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed [grounded] | lab_north 0.50 / supported_spread | lab_north 0.50 / supported_spread [attributed] |
| uc10 | AMB | R(uma->vik) | cooperative | cooperative (0.91) | unknown 0.55 / ambiguous_reference | obstructive 0.45 / abstained [insufficient_evidence] | unknown 0.90 / ambiguous_reference | obstructive 0.34 / abstained [insufficient_evidence] | unknown 0.90 / ambiguous_reference [grounded] | obstructive 0.60 / ambiguous_reference | cooperative 0.33 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference | cooperative 0.33 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference [grounded] | unknown 1.00 / ambiguous_reference | unknown 0.34 / abstained [insufficient_evidence] | obstructive 0.95 / ambiguous_reference [grounded] | unknown 0.70 / ambiguous_reference | cooperative 0.50 / abstained [insufficient_evidence] |
| uc11 | AMB | R(zane->ravi) | cooperative | cooperative (0.65) | unknown 0.60 / ambiguous_reference | obstructive 0.40 / abstained [insufficient_evidence] | unknown 0.90 / ambiguous_reference | obstructive 0.34 / abstained [insufficient_evidence] | unknown 0.80 / ambiguous_reference [uncertain] | unknown 0.50 / ambiguous_reference | cooperative 0.34 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference [grounded] | unknown 1.00 / ambiguous_reference | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference [grounded] | unknown 1.00 / ambiguous_reference | cooperative 0.50 / abstained [insufficient_evidence] |
| uc12 | ok | R(nadia) | cooperative | cooperative (0.50) | obstructive 0.45 / incorrect_supported | obstructive 0.65 / abstained [insufficient_evidence] | obstructive 0.55 / incorrect_supported | obstructive 0.65 / abstained [insufficient_evidence] | obstructive 0.70 / incorrect_supported [uncertain] | obstructive 0.70 / incorrect_supported | obstructive 0.90 / incorrect_supported [attributed] | cooperative 0.33 / supported_spread | cooperative 0.50 / abstained [insufficient_evidence] | obstructive 0.90 / incorrect_supported [uncertain] | unknown 0.50 / unsupported_committed | cooperative 0.50 / abstained [insufficient_evidence] | cooperative 0.50 / supported_spread [uncertain] | cooperative 0.40 / supported_spread | cooperative 0.50 / abstained [insufficient_evidence] |
| uc13 | ok | R(grace) | obstructive | cooperative (0.50) | unknown 0.45 / unsupported_hedged | obstructive 0.65 / abstained [insufficient_evidence] | obstructive 0.55 / correct_supported | obstructive 0.65 / abstained [insufficient_evidence] | obstructive 0.65 / correct_supported [uncertain] | obstructive 0.80 / correct_supported | obstructive 0.80 / correct_supported [attributed] | obstructive 0.80 / correct_supported | obstructive 0.50 / abstained [insufficient_evidence] | obstructive 0.90 / correct_supported [uncertain] | obstructive 0.90 / correct_supported | obstructive 0.90 / correct_supported [attributed] | obstructive 0.90 / correct_supported [grounded] | cooperative 0.85 / incorrect_supported | cooperative 0.90 / incorrect_supported [attributed] |
| uc14 | ok | K(wen->leo) | unknown | unknown (1.00) | room_12 0.45 / unsupported_hedged | room_12 0.50 / abstained [insufficient_evidence] | unknown 0.90 / correct_supported | unknown 0.34 / abstained [insufficient_evidence] | unknown 0.90 / correct_supported [grounded] | room_12 0.40 / unsupported_hedged | unknown 0.34 / abstained [insufficient_evidence] | room_12 0.50 / unsupported_committed | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | room_12 0.50 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | room_12 0.50 / unsupported_committed | room_12 0.50 / abstained [insufficient_evidence] |
| uc15 | ok | K(vik->ivan) | office_b | office_a (0.50) | office_b 0.45 / supported_spread | office_b 0.48 / abstained [insufficient_evidence] | office_b 0.45 / supported_spread | office_b 0.48 / abstained [insufficient_evidence] | office_b 0.45 / supported_spread [uncertain] | office_b 0.50 / supported_spread | unknown 1.00 / unsupported_committed [attributed] | unknown 1.00 / unsupported_committed | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed [grounded] | unknown 0.33 / unsupported_hedged | office_b 0.33 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed [grounded] | unknown 0.40 / unsupported_hedged | office_b 0.50 / abstained [insufficient_evidence] |
| uc16 | ok | K(alice->wen) | unknown | unknown (1.00) | unknown 0.50 / correct_supported | office_a 0.45 / abstained [insufficient_evidence] | unknown 0.80 / correct_supported | office_a 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | office_a 0.50 / unsupported_committed [attributed] | unknown 1.00 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] |
| uc17 | ok | K(tomas->vik) | unknown | unknown (1.00) | unknown 0.90 / correct_supported | suite_east 0.34 / abstained [insufficient_evidence] | unknown 0.80 / correct_supported | unknown 0.34 / abstained [insufficient_evidence] | unknown 0.80 / correct_supported [grounded] | suite_east 0.40 / unsupported_hedged | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | suite_west 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | suite_east 0.50 / abstained [insufficient_evidence] |
| uc18 | ok | K(quinn->uma) | unknown | unknown (1.00) | unknown 0.90 / correct_supported | office_a 0.40 / abstained [insufficient_evidence] | unknown 0.70 / correct_supported | office_a 0.34 / abstained [insufficient_evidence] | unknown 0.90 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | office_a 0.50 / leakage | unknown 0.33 / abstained [insufficient_evidence] | office_a 0.95 / leakage [grounded] | unknown 0.34 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | office_a 0.34 / abstained [insufficient_evidence] |
| uc19 | ok | K(omar->leo) | unknown | unknown (1.00) | unknown 0.55 / correct_supported | lab_north 0.50 / abstained [insufficient_evidence] | unknown 0.90 / correct_supported | lab_north 0.40 / abstained [insufficient_evidence] | unknown 0.96 / correct_supported [grounded] | unknown 0.90 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | lab_north 0.85 / leakage | unknown 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | lab_north 0.80 / leakage | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 0.70 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] |
| uc20 | ok | K(ivan) | office_a | office_a (1.00) | office_a 0.80 / correct_supported | office_a 0.80 / correct_supported [attributed] | office_a 0.85 / correct_supported | office_a 0.90 / correct_supported [attributed] | office_a 0.85 / correct_supported [grounded] | office_a 1.00 / correct_supported | office_a 0.90 / correct_supported [attributed] | office_a 1.00 / correct_supported | office_a 1.00 / correct_supported [attributed] | office_a 1.00 / correct_supported [grounded] | office_a 1.00 / correct_supported | office_a 1.00 / correct_supported [attributed] | office_a 1.00 / correct_supported [grounded] | office_a 0.90 / correct_supported | office_b 0.90 / unsupported_committed [attributed] |
| uc21 | ok | K(frank) | room_7 | room_7 (1.00) | unknown 0.80 / unsupported_committed | room_7 0.50 / abstained [insufficient_evidence] | room_7 0.50 / supported_spread | room_7 0.65 / abstained [insufficient_evidence] | room_7 0.50 / supported_spread [uncertain] | unknown 0.34 / unsupported_hedged | room_7 0.33 / abstained [insufficient_evidence] | unknown 0.34 / unsupported_hedged | room_7 0.33 / abstained [insufficient_evidence] | room_7 0.50 / supported_spread [uncertain] | room_7 0.50 / supported_spread | room_7 0.50 / abstained [insufficient_evidence] | room_7 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | room_7 0.50 / abstained [insufficient_evidence] |
| uc22 | ok | K(alice) | desk_9 | desk_9 (1.00) | desk_9 0.80 / correct_supported | desk_9 0.90 / correct_supported [attributed] | desk_9 0.80 / correct_supported | desk_9 0.80 / correct_supported [attributed] | desk_9 0.80 / correct_supported [grounded] | desk_9 1.00 / correct_supported | desk_9 0.95 / correct_supported [attributed] | desk_9 1.00 / correct_supported | desk_9 1.00 / correct_supported [attributed] | desk_9 1.00 / correct_supported [grounded] | desk_9 1.00 / correct_supported | desk_9 1.00 / correct_supported [attributed] | desk_9 1.00 / correct_supported [grounded] | desk_9 0.50 / supported_spread | desk_9 1.00 / correct_supported [attributed] |
| uc23 | ok | K(alice) | unknown | unknown (1.00) | unknown 0.90 / correct_supported | unknown 0.50 / abstained [insufficient_evidence] | unknown 0.60 / correct_supported | unknown 0.34 / abstained [insufficient_evidence] | unknown 0.50 / correct_supported [uncertain] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] | unknown 1.00 / correct_supported | lab_north 0.50 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] |
| uc24 | ok | K(vik) | office_a | office_a (0.50) | office_a 0.45 / supported_spread | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread [uncertain] | office_a 0.33 / supported_spread | office_a 0.33 / abstained [insufficient_evidence] | office_a 0.33 / supported_spread | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread [uncertain] | office_a 0.33 / supported_spread | office_a 0.33 / abstained [insufficient_evidence] | office_a 0.50 / supported_spread [uncertain] | unknown 1.00 / unsupported_committed | office_a 0.50 / abstained [insufficient_evidence] |
