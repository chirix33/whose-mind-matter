# Pilot analysis: `pilot-full-20261028-060517-3237fb`

Descriptive statistics on development data (exploratory pilot; no hypothesis tests; n = 80 instances in 36 groups, so instances within a group are not independent). Symbolic categories are privileged evaluator annotations (`grounded_typed/face_value`).

## Paired per-instance return differences

| comparison | mean diff | wins | losses | ties |
|---|---|---|---|---|
| dense − direct | -0.051 | 10 | 20 | 50 |
| random − direct | -0.058 | 12 | 17 | 51 |
| router − direct | -0.068 | 14 | 20 | 46 |
| symbolic − direct | +0.019 | 14 | 14 | 52 |
| router − random | -0.010 | 18 | 18 | 44 |
| dense − router | +0.017 | 15 | 19 | 46 |

## Mean return by symbolic category (does the symbolic category transfer?)

| category | n | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|
| carryover | 8 | +0.037 | +0.225 | +0.037 | +0.012 | +0.225 |
| mixed_flip_and_carryover | 19 | +0.463 | +0.458 | +0.442 | +0.405 | +0.466 |
| useful_current_action | 13 | +0.669 | +0.512 | +0.523 | +0.646 | +0.642 |
| zero_value_stop | 40 | +0.789 | +0.704 | +0.731 | +0.694 | +0.797 |

| category | n | success rate: direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|
| carryover | 8 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 |
| mixed_flip_and_carryover | 19 | 0.79 | 0.79 | 0.79 | 0.74 | 0.79 |
| useful_current_action | 13 | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| zero_value_stop | 40 | 0.95 | 0.93 | 0.95 | 0.93 | 0.95 |

## Typed-unit fidelity (LLM top hypothesis vs true content; privileged scoring)

| unit type | calls | valid | top = truth | mean top-p (valid) | top=truth when top-p ≥ 0.8 | top = unknown |
|---|---|---|---|---|---|---|
| K1 | 435 | 435 | 0.44 | 0.75 | 0.43 (n=241) | 0.42 |
| K2 | 239 | 239 | 0.43 | 0.66 | 0.65 (n=89) | 0.34 |
| R1 | 38 | 38 | 0.42 | 0.62 | 0.21 (n=14) | 0.03 |
| R2 | 17 | 17 | 0.24 | 0.56 | 0.33 (n=3) | 0.65 |

Unit types: K1 = K(j), K2 = K(j→k), R1 = R(j), R2 = R(j→k).

## Router / STOP behaviour

- Router calls: 146; STOP decisions: 62 (0.42).
- Mean units per episode: router 1.43, random 1.95, dense 4.92.
- Router instantiated zero units in 11/40 symbolic zero-value instances and in 3/40 others.
- Mean Jaccard(router allocation, symbolic reference set): 0.38.

## Do decisions respond to variant knobs? (first action differs within a single-knob pair)

| knob | pairs | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|
| stakes | 16 | 4 | 4 | 4 | 3 | 3 |
| evidence | 16 | 8 | 6 | 5 | 7 | 4 |

## Overhead share of tokens (prompt + completion, means per episode)

| arm | decision | unit | refresh | router | router+unit share |
|---|---|---|---|---|---|
| direct | 2586 | 0 | 0 | 0 | 0.00 |
| dense | 3407 | 4153 | 158 | 0 | 0.56 |
| random | 2803 | 1628 | 47 | 0 | 0.37 |
| router | 2783 | 1184 | 46 | 1634 | 0.51 |
| symbolic | 2560 | 414 | 47 | 0 | 0.15 |

## Invalid outputs and retries

- Calls with at least one failed attempt: 4; failure reasons: {'cites_non_visible_evidence': 3, 'probabilities_not_normalized': 1, 'not_json': 2}.
- Calls that exhausted all attempts (fallback/abstain): 0.
  - random / dev-v2-stop-g0-bystander0 / unit K(nadia): [['cites_non_visible_evidence'], ['cites_non_visible_evidence'], None]
  - dense / dev-v2-stop-g3-bystander1 / unit K(zane->alice): [['probabilities_not_normalized'], None]
  - dense / dev-v2-ambiguity-g2-evidence0 / unit K(alice): [['cites_non_visible_evidence'], None]
  - router / dev-v2-ambiguity-g3-evidence0 / decision policy: [['not_json'], ['not_json'], None]

## Paired interventions: symbolic vs realized

- 9 states; first action changed in 1; sign agreement between symbolic delta_J and realized return difference (non-zero cases): 1/2.
