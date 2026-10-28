# Fixed unit-context diagnostic: model × package

Runs: `unit-contexts-20261028-064729-654f39`, `unit-contexts-20261028-064818-7d5f71`. Contexts: `reports/pilot/unit-contexts-v1.md` (24 frozen contexts; renderer r3 for fresh runs). Scoring v2 (`src/vomi/fidelity.py`): categories over ATTRIBUTED outputs; proper scores over all valid outputs. Development data; exploratory.

| model | effort | package | n | valid | incomplete attempts | abstained | correct_supported | correct_unsupported | incorrect_supported | unsupported_incorrect | leakage | top-1 | log score (truth) | Brier | CE vs evidence posterior | mean in/out/reasoning tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | low | pilot-v1 | 24 | 24 | 0 | 0 | 13 | 0 | 2 | 9 | 0 | 0.54 | -1.36 | 0.65 | 1.38 | 785/199/111 |
| gpt-oss-20b | low | pilot-v1 (original r2 run) | 16 | 16 | 0 | 0 | 11 | 0 | 1 | 4 | 0 | 0.69 | -1.87 | 0.72 | 1.99 | — |
| gpt-oss-20b | low | pilot-v2 | 24 | 24 | 0 | 12 | 8 | 0 | 1 | 3 | 0 | 0.67 | -1.34 | 0.62 | 1.33 | 1285/327/187 |
| gpt-oss-20b | medium | pilot-v1 | 24 | 24 | 1 | 0 | 13 | 0 | 2 | 9 | 0 | 0.54 | -2.49 | 0.84 | 2.44 | 820/1049/946 |
| gpt-oss-20b | medium | pilot-v2 | 24 | 24 | 1 | 14 | 8 | 0 | 1 | 1 | 0 | 0.54 | -1.21 | 0.57 | 1.21 | 1393/1618/1407 |

Categories count attributed (non-abstained) outputs only; `abstained` = pilot-v2 status insufficient_evidence. Log score uses a 1e-3 floor; lower Brier/CE is better, higher log score is better.

## Paired effects on the same contexts (mean difference; positive = better)

| comparison | contexts | Δ log score (truth) | Δ CE vs posterior (negated) | Δ unsupported+leakage rate |
|---|---|---|---|---|
| package: gpt-oss-20b/low/pilot-v1 (original r2 run) vs gpt-oss-20b/low/pilot-v1 | 16 | -0.19 | -0.24 | +0.12 |
| package: gpt-oss-20b/low/pilot-v2 vs gpt-oss-20b/low/pilot-v1 | 24 | +0.02 | +0.05 | +0.25 |
| model: gpt-oss-20b/medium/pilot-v1 vs gpt-oss-20b/low/pilot-v1 | 24 | -1.13 | -1.06 | +0.00 |
| package: gpt-oss-20b/low/pilot-v2 vs gpt-oss-20b/low/pilot-v1 (original r2 run) | 16 | +0.36 | +0.43 | +0.06 |
| model: gpt-oss-20b/medium/pilot-v2 vs gpt-oss-20b/low/pilot-v2 | 24 | +0.13 | +0.12 | +0.08 |
| package: gpt-oss-20b/medium/pilot-v2 vs gpt-oss-20b/medium/pilot-v1 | 24 | +1.28 | +1.23 | +0.33 |

## Per-context outputs (top value / category; abstention shown as ABST)

| ctx | unit | k | truth | evidence-posterior top (p) | gpt-oss-20b/low/pilot-v1 | gpt-oss-20b/low/pilot-v1 (original r2 run) | gpt-oss-20b/low/pilot-v2 | gpt-oss-20b/medium/pilot-v1 | gpt-oss-20b/medium/pilot-v2 |
|---|---|---|---|---|---|---|---|---|---|
| uc01 | K(wen) | 0 | desk_9 | desk_3 (0.50) | unknown / unsupported_incorrect | desk_9 / correct_supported | desk_9 / correct_supported | desk_9 / correct_supported | desk_9 / correct_supported |
| uc02 | K(judy) | 0 | office_b | office_b (0.95) | unknown / unsupported_incorrect | unknown / unsupported_incorrect | ABST (unknown) | unknown / unsupported_incorrect | ABST (office_a) |
| uc03 | K(grace) | 0 | lab_south | lab_south (1.00) | lab_south / correct_supported | lab_south / correct_supported | lab_south / correct_supported | lab_south / correct_supported | lab_south / correct_supported |
| uc04 | K(carol) | 0 | office_a | office_a (0.50) | unknown / unsupported_incorrect | unknown / unsupported_incorrect | ABST (office_b) | office_b / incorrect_supported | ABST (office_b) |
| uc05 | K(leo) | 0 | room_12 | room_12 (0.50) | unknown / unsupported_incorrect | room_12 / correct_supported | ABST (room_12) | unknown / unsupported_incorrect | ABST (room_12) |
| uc06 | K(mia) | 0 | room_7 | room_7 (0.97) | room_7 / correct_supported | room_7 / correct_supported | room_7 / correct_supported | room_7 / correct_supported | room_7 / correct_supported |
| uc07 | K(heidi) | 0 | desk_3 | desk_3 (0.87) | desk_3 / correct_supported | desk_3 / correct_supported | unknown / unsupported_incorrect | desk_3 / correct_supported | desk_3 / correct_supported |
| uc08 | K(yara) | 0 | desk_9 | desk_3 (0.50) | desk_9 / correct_supported | desk_9 / correct_supported | ABST (desk_9) | unknown / unsupported_incorrect | ABST (desk_9) |
| uc09 | K(dave) | 0 | lab_north | lab_north (0.50) | lab_north / correct_supported | lab_north / correct_supported | lab_north / correct_supported | lab_north / correct_supported | lab_north / correct_supported |
| uc10 | R(uma->vik) | 1 | cooperative | cooperative (0.91) | obstructive / unsupported_incorrect | — | ABST (cooperative) | unknown / unsupported_incorrect | ABST (cooperative) |
| uc11 | R(zane->ravi) | 0 | cooperative | cooperative (0.65) | unknown / unsupported_incorrect | obstructive / incorrect_supported | ABST (cooperative) | unknown / unsupported_incorrect | ABST (cooperative) |
| uc12 | R(nadia) | 1 | cooperative | cooperative (0.50) | obstructive / incorrect_supported | — | obstructive / incorrect_supported | cooperative / correct_supported | ABST (obstructive) |
| uc13 | R(grace) | 0 | obstructive | cooperative (0.50) | obstructive / correct_supported | obstructive / correct_supported | obstructive / correct_supported | cooperative / incorrect_supported | cooperative / incorrect_supported |
| uc14 | K(wen->leo) | 0 | unknown | unknown (1.00) | room_7 / unsupported_incorrect | room_7 / unsupported_incorrect | ABST (unknown) | room_7 / unsupported_incorrect | ABST (room_7) |
| uc15 | K(vik->ivan) | 0 | office_b | office_a (0.50) | office_a / incorrect_supported | unknown / unsupported_incorrect | unknown / unsupported_incorrect | unknown / unsupported_incorrect | ABST (office_a) |
| uc16 | K(alice->wen) | 0 | unknown | unknown (1.00) | unknown / correct_supported | unknown / correct_supported | office_a / unsupported_incorrect | unknown / correct_supported | unknown / correct_supported |
| uc17 | K(tomas->vik) | 1 | unknown | unknown (1.00) | suite_east / unsupported_incorrect | — | ABST (unknown) | unknown / correct_supported | ABST (suite_east) |
| uc18 | K(quinn->uma) | 1 | unknown | unknown (1.00) | unknown / correct_supported | — | ABST (unknown) | unknown / correct_supported | ABST (office_a) |
| uc19 | K(omar->leo) | 1 | unknown | unknown (1.00) | unknown / correct_supported | — | ABST (unknown) | unknown / correct_supported | ABST (unknown) |
| uc20 | K(ivan) | 1 | office_a | office_a (1.00) | office_a / correct_supported | — | office_a / correct_supported | office_a / correct_supported | office_b / unsupported_incorrect |
| uc21 | K(frank) | 1 | room_7 | room_7 (1.00) | unknown / unsupported_incorrect | — | ABST (room_12) | unknown / unsupported_incorrect | ABST (room_12) |
| uc22 | K(alice) | 1 | desk_9 | desk_9 (1.00) | desk_9 / correct_supported | — | desk_9 / correct_supported | desk_9 / correct_supported | desk_9 / correct_supported |
| uc23 | K(alice) | 0 | unknown | unknown (1.00) | unknown / correct_supported | unknown / correct_supported | unknown / correct_supported | unknown / correct_supported | unknown / correct_supported |
| uc24 | K(vik) | 0 | office_a | office_a (0.50) | office_a / correct_supported | office_a / correct_supported | ABST (office_b) | unknown / unsupported_incorrect | ABST (office_b) |
