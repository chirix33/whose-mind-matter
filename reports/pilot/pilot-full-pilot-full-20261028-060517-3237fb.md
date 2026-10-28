# Pilot full results: run `pilot-full-20261028-060517-3237fb`

Frozen set `dev-v2` (set hash `3e8afe544f7e2900…`), commit `151846b`, model `gpt-oss-20b`, prompts `pilot-v1` renderer r2, decoding {'temperature': 0.0, 'max_tokens': 1024, 'reasoning_effort': 'low'}, concurrency 8. Development data: exploratory pilot, not a confirmatory result. Temperature 0 does not guarantee reproducibility under vLLM batching; serving settings are recorded in the manifest.

## Outcomes by arm

| arm | episodes | success | error | timeout | mean return | mean steps | units/episode | unit calls ok | unit top = truth | router STOPs | failed attempts | fallbacks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 80 | 0.85 | 0.04 | 0.11 | +0.617 | 3.54 | 0.00 | 0/0 | — | 0 | 0 | 0 |
| dense | 80 | 0.84 | 0.07 | 0.09 | +0.566 | 3.55 | 4.92 | 407/407 | 0.43 | 0 | 2 | 0 |
| random | 80 | 0.85 | 0.09 | 0.06 | +0.559 | 3.44 | 1.95 | 160/160 | 0.42 | 0 | 2 | 0 |
| router | 80 | 0.82 | 0.10 | 0.07 | +0.549 | 3.39 | 1.43 | 118/118 | 0.37 | 62 | 2 | 0 |
| symbolic | 80 | 0.85 | 0.05 | 0.10 | +0.636 | 3.40 | 0.50 | 44/44 | 0.57 | 0 | 0 | 0 |

## Compute per episode (means; API calls include retries)

| arm | call kind | calls | prompt tok | completion tok | reasoning tok | summed call latency (s) |
|---|---|---|---|---|---|---|
| direct | decision | 3.54 | 2265 | 321 | 244 | 2.43 |
| dense | decision | 3.55 | 3045 | 362 | 284 | 2.72 |
| dense | refresh | 0.16 | 127 | 31 | 15 | 0.23 |
| dense | unit | 4.95 | 3238 | 915 | 490 | 6.85 |
| random | decision | 3.44 | 2455 | 349 | 273 | 2.61 |
| random | refresh | 0.05 | 36 | 11 | 6 | 0.08 |
| random | unit | 1.98 | 1274 | 354 | 186 | 2.65 |
| router | decision | 3.41 | 2398 | 385 | 310 | 2.88 |
| router | refresh | 0.05 | 37 | 9 | 5 | 0.07 |
| router | router | 1.82 | 1235 | 398 | 351 | 2.96 |
| router | unit | 1.43 | 933 | 250 | 131 | 1.87 |
| symbolic | decision | 3.40 | 2221 | 339 | 264 | 2.53 |
| symbolic | refresh | 0.05 | 37 | 10 | 6 | 0.07 |
| symbolic | unit | 0.50 | 321 | 93 | 53 | 0.69 |

| arm | mean episode wall clock (s, monotonic) | median |
|---|---|---|
| direct | 2.43 | 1.87 |
| dense | 9.79 | 8.24 |
| random | 5.34 | 4.86 |
| router | 7.78 | 6.65 |
| symbolic | 3.30 | 2.67 |

Episode wall clock is measured per episode while other episodes ran concurrently (contention included); summed call latency is NOT elapsed time.

## Mean return by family and arm

| family | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|
| ambiguity | +0.800 | +0.794 | +0.794 | +0.581 | +0.812 |
| conflict | +0.319 | +0.150 | +0.287 | +0.294 | +0.319 |
| corroborated | +0.919 | +0.887 | +0.919 | +0.925 | +0.938 |
| directed_perspective | +0.500 | +0.500 | +0.450 | +0.506 | +0.512 |
| distractors | +0.787 | +0.800 | +0.781 | +0.787 | +0.819 |
| false_belief | +0.525 | +0.281 | +0.284 | +0.387 | +0.491 |
| nested_reliability | +0.806 | +0.794 | +0.806 | +0.662 | +0.806 |
| relevance_shift | +0.037 | +0.225 | +0.037 | +0.012 | +0.225 |
| stop | +0.950 | +0.950 | +0.950 | +0.950 | +0.950 |

## Paired unit interventions (controlled rollouts; one realized world each, so differences are samples)

| instance | unit | symbolic category (record) | symbolic delta_J | t0 action without → with | return without | return with | difference | LLM unit top / truth |
|---|---|---|---|---|---|---|---|---|
| dev-v2-false_belief-g0-stakes4-evidence0 | K(wen) | useful_current_action (grounded_typed/face_value) | +0.8000 | ask(wen,quinn_loc) → ask(wen,quinn_loc) | +0.80 | +0.80 | +0.00 | desk_9 / desk_9 |
| dev-v2-conflict-g1-stakes4 | K(judy) | useful_current_action (grounded_typed/face_value) | +0.0450 | move(hall) → move(hall) | +0.65 | +0.85 | +0.20 | office_a / office_b |
| dev-v2-corroborated-g3-evidence0 | K(grace) | useful_current_action (grounded_typed/face_value) | +0.0400 | move(hall) → move(hall) | +0.85 | +0.85 | +0.00 | lab_south / lab_south |
| dev-v2-ambiguity-g0-evidence1 | K(carol) | zero_value_stop (grounded_typed/face_value) | +0.0000 | ask(ivan,carol_loc) → ask(ivan,carol_loc) | -0.60 | +0.80 | +1.40 | unknown / office_a |
| dev-v2-distractors-g3-permuted1 | K(leo) | zero_value_stop (grounded_typed/face_value) | +0.0000 | ask(ravi,leo_loc) → ask(ravi,leo_loc) | +0.90 | +0.90 | +0.00 | unknown / room_12 |
| dev-v2-conflict-g3-stakes1 | K(mia) | zero_value_stop (grounded_typed/face_value) | +0.0000 | move(hall) → drop(room_7) | +0.85 | +0.95 | +0.10 | room_7 / room_7 |
| dev-v2-conflict-g2-stakes1 | K(heidi) | negative (grounded_scalar/face_value) | -0.1800 | ask(heidi,quinn_loc) → ask(heidi,quinn_loc) | +0.65 | +0.85 | +0.20 | desk_3 / desk_3 |
| dev-v2-directed_perspective-g2-permuted1 | K(yara) | negative (grounded_scalar/hedged) | -0.1500 | ask(tomas,meeting_room) → ask(tomas,meeting_room) | -0.40 | -0.40 | +0.00 | unknown / desk_9 |
| dev-v2-relevance_shift-g1-stakes1 | K(dave) | carryover (grounded_typed/face_value) | +0.2240 | ask(dave,yara_loc) → ask(dave,yara_loc) | -0.40 | -0.40 | +0.00 | lab_north / lab_north |
