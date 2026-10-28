# Round 1 results: fixed contexts under scoring v3

Runs: `unit-contexts-20261028-064729-654f39`, `unit-contexts-20261028-064818-7d5f71`, `unit-contexts-20261028-070945-72da94`, `unit-contexts-20261028-083007-1512c0`. Contexts: the 24 of `unit-contexts-v1` (r4 rows use `reports/autonomous-block/unit-contexts-v1-r4.jsonl`). Development data; exploratory.
Ambiguity policy: `reports/autonomous-block/reference-audit.json` (written before outputs). Primary block = 19 consistent contexts; ambiguous = uc02, uc06, uc07, uc10, uc11.
Hallucination-type = unsupported_committed + leakage. r3 rows are earlier runs rescored with v3 (contract r3, not re-run).

## Primary (consistent contexts): category counts (each row sums to n)

| cell (model/effort/rules/package) | cap | n | correct_supported | correct_unsupported | incorrect_supported | leakage | unsupported_committed | unsupported_hedged | ambiguous_reference | abstained | invalid | hallucination-type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 16000 | 19 | 12 | 0 | 3 | 0 | 1 | 3 | 0 | 0 | 0 | 1 |
| gpt-6.1-sol/low/r3/pilot-v2 | 16000 | 19 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 4096 | 19 | 11 | 0 | 2 | 0 | 3 | 3 | 0 | 0 | 0 | 3 |
| gpt-oss-20b/low/r3/pilot-v2 | 4096 | 19 | 7 | 0 | 1 | 0 | 2 | 0 | 0 | 9 | 0 | 2 |
| gpt-oss-20b/low/r4/pilot-v1 | 4096 | 19 | 12 | 0 | 0 | 2 | 4 | 1 | 0 | 0 | 0 | 6 |
| gpt-oss-20b/low/r4/pilot-v2 | 4096 | 19 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 14 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 4096 | 19 | 12 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 5 |
| gpt-oss-20b/medium/r3/pilot-v1 | 4096 | 19 | 11 | 0 | 2 | 0 | 5 | 1 | 0 | 0 | 0 | 5 |
| gpt-oss-20b/medium/r3/pilot-v2 | 4096 | 19 | 6 | 0 | 1 | 0 | 1 | 0 | 0 | 11 | 0 | 1 |

## Ambiguous contexts: category counts (each row sums to n)

| cell (model/effort/rules/package) | cap | n | correct_supported | correct_unsupported | incorrect_supported | leakage | unsupported_committed | unsupported_hedged | ambiguous_reference | abstained | invalid | hallucination-type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 16000 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-6.1-sol/low/r3/pilot-v2 | 16000 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-oss-20b/low/r3/pilot-v2 | 4096 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v1 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v2 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-oss-20b/medium/r3/pilot-v1 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| gpt-oss-20b/medium/r3/pilot-v2 | 4096 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |

## Proper scores and coverage (all 24 contexts)

Over all valid outputs (abstentions included through their distributions) and over attributed outputs only. Log score vs truth (higher better, 1e-3 floor); Brier, CE vs reference posterior and TV vs posterior: lower better.

| cell | coverage (attributed/24) | invalid | log score | Brier | CE vs post. | TV vs post. | log score (attributed) | mean tokens in/out/reasoning | incomplete attempts |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6.1-sol/low/r3/pilot-v1 | 24/24 | 0 | -0.95 | 0.53 | 0.93 | 0.34 | -0.95 | 891/828/12 | 1 |
| gpt-6.1-sol/low/r3/pilot-v2 | 4/24 | 0 | -1.09 | 0.56 | 1.08 | 0.34 | -0.16 | 1411/334/3 | 0 |
| gpt-oss-20b/low/r3/pilot-v1 | 24/24 | 0 | -1.36 | 0.65 | 1.38 | 0.36 | -1.36 | 785/199/111 | 0 |
| gpt-oss-20b/low/r3/pilot-v2 | 12/24 | 0 | -1.34 | 0.62 | 1.33 | 0.40 | -1.58 | 1285/327/187 | 0 |
| gpt-oss-20b/low/r4/pilot-v1 | 24/24 | 0 | -2.01 | 0.74 | 2.08 | 0.41 | -2.01 | 1041/200/118 | 0 |
| gpt-oss-20b/low/r4/pilot-v2 | 7/24 | 0 | -1.01 | 0.52 | 1.06 | 0.33 | -0.20 | 1541/359/230 | 0 |
| gpt-oss-20b/low/r4/pilot-v2.1 | 24/24 | 0 | -1.70 | 0.68 | 1.75 | 0.33 | -1.70 | 1782/329/194 | 0 |
| gpt-oss-20b/medium/r3/pilot-v1 | 24/24 | 0 | -2.49 | 0.84 | 2.44 | 0.43 | -2.49 | 820/1049/946 | 1 |
| gpt-oss-20b/medium/r3/pilot-v2 | 10/24 | 0 | -1.21 | 0.57 | 1.21 | 0.27 | -0.61 | 1393/1618/1407 | 1 |

## Paired comparisons on the same contexts (B vs A; positive Δ log / Δ CE = B better)

| effect | B vs A | contexts | Δ log score | Δ CE (negated) | Δ abstentions | Δ hallucination-type (primary) |
|---|---|---|---|---|---|---|
| package (same rules) | gpt-6.1-sol/low/r3/pilot-v2 vs gpt-6.1-sol/low/r3/pilot-v1 | 24 | -0.13 | -0.15 | +20 | -1 |
| model (same effort/rules/package) | gpt-oss-20b/low/r3/pilot-v1 vs gpt-6.1-sol/low/r3/pilot-v1 | 24 | -0.40 | -0.45 | +0 | +2 |
| model (same effort/rules/package) | gpt-oss-20b/low/r3/pilot-v2 vs gpt-6.1-sol/low/r3/pilot-v2 | 24 | -0.25 | -0.25 | -8 | +2 |
| package (same rules) | gpt-oss-20b/low/r3/pilot-v2 vs gpt-oss-20b/low/r3/pilot-v1 | 24 | +0.02 | +0.05 | +12 | -1 |
| rules r3 -> r4 (same package) | gpt-oss-20b/low/r4/pilot-v1 vs gpt-oss-20b/low/r3/pilot-v1 | 24 | -0.65 | -0.71 | +0 | +3 |
| rules r3 -> r4 (same package) | gpt-oss-20b/low/r4/pilot-v2 vs gpt-oss-20b/low/r3/pilot-v2 | 24 | +0.33 | +0.27 | +5 | -2 |
| package (same rules) | gpt-oss-20b/low/r4/pilot-v2 vs gpt-oss-20b/low/r4/pilot-v1 | 24 | +1.00 | +1.03 | +17 | -6 |
| package (same rules) | gpt-oss-20b/low/r4/pilot-v2.1 vs gpt-oss-20b/low/r4/pilot-v1 | 24 | +0.31 | +0.33 | +0 | -1 |
| package (same rules) | gpt-oss-20b/low/r4/pilot-v2.1 vs gpt-oss-20b/low/r4/pilot-v2 | 24 | -0.69 | -0.69 | -17 | +5 |
| package (same rules) | gpt-oss-20b/medium/r3/pilot-v2 vs gpt-oss-20b/medium/r3/pilot-v1 | 24 | +1.28 | +1.23 | +14 | -4 |

## Per-context top value / category

| ctx | ref | unit | truth | posterior top (p) | gpt-6.1-sol/low/r3/pilot-v1 | gpt-6.1-sol/low/r3/pilot-v2 | gpt-oss-20b/low/r3/pilot-v1 | gpt-oss-20b/low/r3/pilot-v2 | gpt-oss-20b/low/r4/pilot-v1 | gpt-oss-20b/low/r4/pilot-v2 | gpt-oss-20b/low/r4/pilot-v2.1 | gpt-oss-20b/medium/r3/pilot-v1 | gpt-oss-20b/medium/r3/pilot-v2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| uc01 | ok | K(wen) | desk_9 | desk_3 (0.50) | desk_3 0.40 / incorrect_supported | desk_3 0.45 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed | desk_9 0.50 / correct_supported [attributed] | desk_9 0.50 / correct_supported | desk_9 0.50 / correct_supported [attributed] | desk_9 0.50 / correct_supported [uncertain] | desk_9 0.50 / correct_supported | desk_9 0.50 / correct_supported [attributed] |
| uc02 | AMB | K(judy) | office_b | office_b (0.95) | office_a 0.40 / ambiguous_reference | office_a 0.50 / abstained [insufficient_evidence] | unknown 0.90 / ambiguous_reference | unknown 0.34 / abstained [insufficient_evidence] | office_a 0.50 / ambiguous_reference | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.50 / ambiguous_reference [uncertain] | unknown 1.00 / ambiguous_reference | office_a 0.50 / abstained [insufficient_evidence] |
| uc03 | ok | K(grace) | lab_south | lab_south (1.00) | lab_south 0.80 / correct_supported | lab_south 0.90 / correct_supported [attributed] | lab_south 1.00 / correct_supported | lab_south 1.00 / correct_supported [attributed] | lab_south 1.00 / correct_supported | lab_south 1.00 / correct_supported [attributed] | lab_south 1.00 / correct_supported [grounded] | lab_south 1.00 / correct_supported | lab_south 0.90 / correct_supported [attributed] |
| uc04 | ok | K(carol) | office_a | office_a (0.50) | office_a 0.45 / correct_supported | office_a 0.50 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed | office_b 0.33 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed | office_b 0.33 / abstained [insufficient_evidence] | office_a 0.50 / correct_supported [uncertain] | office_b 0.33 / incorrect_supported | office_b 0.50 / abstained [insufficient_evidence] |
| uc05 | ok | K(leo) | room_12 | room_12 (0.50) | unknown 0.33 / unsupported_hedged | room_12 0.45 / abstained [insufficient_evidence] | unknown 0.90 / unsupported_committed | room_12 0.33 / abstained [insufficient_evidence] | unknown 0.90 / unsupported_committed | room_12 0.33 / abstained [insufficient_evidence] | room_12 0.50 / correct_supported [uncertain] | unknown 1.00 / unsupported_committed | room_12 0.50 / abstained [insufficient_evidence] |
| uc06 | AMB | K(mia) | room_7 | room_7 (0.97) | room_7 0.45 / correct_supported | room_7 0.55 / abstained [insufficient_evidence] | room_7 1.00 / correct_supported | room_7 1.00 / correct_supported [attributed] | room_7 1.00 / correct_supported | room_7 1.00 / correct_supported [attributed] | room_7 1.00 / correct_supported [grounded] | room_7 0.90 / correct_supported | room_7 1.00 / correct_supported [attributed] |
| uc07 | AMB | K(heidi) | desk_3 | desk_3 (0.87) | desk_3 0.80 / correct_supported | desk_3 0.80 / correct_supported [attributed] | desk_3 0.50 / correct_supported | unknown 0.34 / ambiguous_reference [attributed] | desk_3 1.00 / correct_supported | desk_3 1.00 / correct_supported [attributed] | desk_3 1.00 / correct_supported [grounded] | desk_3 0.85 / correct_supported | desk_3 1.00 / correct_supported [attributed] |
| uc08 | ok | K(yara) | desk_9 | desk_3 (0.50) | desk_9 0.45 / correct_supported | desk_3 0.50 / abstained [insufficient_evidence] | desk_9 0.50 / correct_supported | desk_9 0.33 / abstained [insufficient_evidence] | desk_9 0.50 / correct_supported | desk_9 0.33 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed [grounded] | unknown 1.00 / unsupported_committed | desk_9 0.50 / abstained [insufficient_evidence] |
| uc09 | ok | K(dave) | lab_north | lab_north (0.50) | lab_north 0.40 / correct_supported | lab_north 0.48 / abstained [insufficient_evidence] | lab_north 0.50 / correct_supported | lab_north 0.50 / correct_supported [attributed] | lab_north 0.50 / correct_supported | lab_north 0.50 / correct_supported [attributed] | unknown 0.95 / unsupported_committed [uncertain] | lab_north 0.50 / correct_supported | lab_north 0.50 / correct_supported [attributed] |
| uc10 | AMB | R(uma->vik) | cooperative | cooperative (0.91) | unknown 0.55 / ambiguous_reference | obstructive 0.45 / abstained [insufficient_evidence] | obstructive 0.60 / ambiguous_reference | cooperative 0.33 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference | cooperative 0.33 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference [grounded] | unknown 0.70 / ambiguous_reference | cooperative 0.50 / abstained [insufficient_evidence] |
| uc11 | AMB | R(zane->ravi) | cooperative | cooperative (0.65) | unknown 0.60 / ambiguous_reference | obstructive 0.40 / abstained [insufficient_evidence] | unknown 0.50 / ambiguous_reference | cooperative 0.34 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / ambiguous_reference [grounded] | unknown 1.00 / ambiguous_reference | cooperative 0.50 / abstained [insufficient_evidence] |
| uc12 | ok | R(nadia) | cooperative | cooperative (0.50) | obstructive 0.45 / incorrect_supported | obstructive 0.65 / abstained [insufficient_evidence] | obstructive 0.70 / incorrect_supported | obstructive 0.90 / incorrect_supported [attributed] | cooperative 0.33 / correct_supported | cooperative 0.50 / abstained [insufficient_evidence] | obstructive 0.90 / incorrect_supported [uncertain] | cooperative 0.40 / correct_supported | obstructive 0.50 / abstained [insufficient_evidence] |
| uc13 | ok | R(grace) | obstructive | cooperative (0.50) | unknown 0.45 / unsupported_hedged | obstructive 0.65 / abstained [insufficient_evidence] | obstructive 0.80 / correct_supported | obstructive 0.80 / correct_supported [attributed] | obstructive 0.80 / correct_supported | cooperative 0.50 / abstained [insufficient_evidence] | obstructive 0.90 / correct_supported [uncertain] | cooperative 0.85 / incorrect_supported | cooperative 0.90 / incorrect_supported [attributed] |
| uc14 | ok | K(wen->leo) | unknown | unknown (1.00) | room_12 0.45 / unsupported_hedged | room_12 0.50 / abstained [insufficient_evidence] | room_7 0.40 / unsupported_hedged | unknown 0.34 / abstained [insufficient_evidence] | room_7 0.50 / unsupported_committed | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | room_7 0.50 / unsupported_committed | room_7 0.50 / abstained [insufficient_evidence] |
| uc15 | ok | K(vik->ivan) | office_b | office_a (0.50) | office_a 0.45 / incorrect_supported | office_a 0.48 / abstained [insufficient_evidence] | office_a 0.50 / incorrect_supported | unknown 1.00 / unsupported_committed [attributed] | unknown 1.00 / unsupported_committed | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / unsupported_committed [grounded] | unknown 0.40 / unsupported_hedged | office_a 0.50 / abstained [insufficient_evidence] |
| uc16 | ok | K(alice->wen) | unknown | unknown (1.00) | unknown 0.50 / correct_supported | office_a 0.45 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported | office_a 0.50 / unsupported_committed [attributed] | unknown 1.00 / correct_supported | office_a 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] |
| uc17 | ok | K(tomas->vik) | unknown | unknown (1.00) | unknown 0.90 / correct_supported | suite_east 0.34 / abstained [insufficient_evidence] | suite_east 0.40 / unsupported_hedged | unknown 0.34 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported | suite_east 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | suite_east 0.50 / abstained [insufficient_evidence] |
| uc18 | ok | K(quinn->uma) | unknown | unknown (1.00) | unknown 0.90 / correct_supported | office_a 0.40 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | office_a 0.50 / leakage | office_a 0.33 / abstained [insufficient_evidence] | office_a 0.95 / leakage [grounded] | unknown 1.00 / correct_supported | office_a 0.34 / abstained [insufficient_evidence] |
| uc19 | ok | K(omar->leo) | unknown | unknown (1.00) | unknown 0.55 / correct_supported | lab_north 0.50 / abstained [insufficient_evidence] | unknown 0.90 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] | lab_north 0.85 / leakage | lab_north 0.33 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 0.70 / correct_supported | unknown 0.33 / abstained [insufficient_evidence] |
| uc20 | ok | K(ivan) | office_a | office_a (1.00) | office_a 0.80 / correct_supported | office_a 0.80 / correct_supported [attributed] | office_a 1.00 / correct_supported | office_a 0.90 / correct_supported [attributed] | office_a 1.00 / correct_supported | office_a 1.00 / correct_supported [attributed] | office_a 1.00 / correct_supported [grounded] | office_a 0.90 / correct_supported | office_b 0.90 / unsupported_committed [attributed] |
| uc21 | ok | K(frank) | room_7 | room_7 (1.00) | unknown 0.80 / unsupported_committed | room_7 0.50 / abstained [insufficient_evidence] | unknown 0.34 / unsupported_hedged | room_12 0.33 / abstained [insufficient_evidence] | unknown 0.34 / unsupported_hedged | room_12 0.33 / abstained [insufficient_evidence] | room_12 0.50 / unsupported_committed [uncertain] | unknown 1.00 / unsupported_committed | room_12 0.50 / abstained [insufficient_evidence] |
| uc22 | ok | K(alice) | desk_9 | desk_9 (1.00) | desk_9 0.80 / correct_supported | desk_9 0.90 / correct_supported [attributed] | desk_9 1.00 / correct_supported | desk_9 0.95 / correct_supported [attributed] | desk_9 1.00 / correct_supported | desk_9 1.00 / correct_supported [attributed] | desk_9 1.00 / correct_supported [grounded] | desk_9 0.50 / correct_supported | desk_9 1.00 / correct_supported [attributed] |
| uc23 | ok | K(alice) | unknown | unknown (1.00) | unknown 0.90 / correct_supported | unknown 0.50 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] | unknown 1.00 / correct_supported | lab_south 0.50 / abstained [insufficient_evidence] | unknown 1.00 / correct_supported [grounded] | unknown 1.00 / correct_supported | unknown 1.00 / correct_supported [attributed] |
| uc24 | ok | K(vik) | office_a | office_a (0.50) | office_a 0.45 / correct_supported | office_a 0.50 / abstained [insufficient_evidence] | office_a 0.33 / correct_supported | office_b 0.33 / abstained [insufficient_evidence] | office_a 0.33 / correct_supported | office_a 0.50 / abstained [insufficient_evidence] | office_b 0.50 / incorrect_supported [uncertain] | unknown 1.00 / unsupported_committed | office_b 0.50 / abstained [insufficient_evidence] |
