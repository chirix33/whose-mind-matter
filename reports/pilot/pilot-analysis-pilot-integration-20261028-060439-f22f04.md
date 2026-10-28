# Pilot analysis: `pilot-integration-20261028-060439-f22f04`

Descriptive statistics on development data (exploratory pilot; no hypothesis tests; n = 80 instances in 36 groups, so instances within a group are not independent). Symbolic categories are privileged evaluator annotations (`grounded_typed/face_value`).

## Paired per-instance return differences

| comparison | mean diff | wins | losses | ties |
|---|---|---|---|---|
| dense − direct | +0.000 | 0 | 0 | 1 |
| random − direct | +0.000 | 0 | 0 | 1 |
| router − direct | +0.050 | 1 | 0 | 0 |
| symbolic − direct | -0.050 | 0 | 1 | 0 |
| router − random | +0.050 | 1 | 0 | 0 |
| dense − router | -0.050 | 0 | 1 | 0 |

## Mean return by symbolic category (does the symbolic category transfer?)

| category | n | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|
| zero_value_stop | 1 | +0.850 | +0.850 | +0.850 | +0.900 | +0.800 |

| category | n | success rate: direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|
| zero_value_stop | 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Typed-unit fidelity (LLM top hypothesis vs true content; privileged scoring)

| unit type | calls | valid | top = truth | mean top-p (valid) | top=truth when top-p ≥ 0.8 | top = unknown |
|---|---|---|---|---|---|---|
| K1 | 5 | 5 | 1.00 | 0.60 | 1.00 (n=1) | 0.20 |
| K2 | 7 | 7 | 0.14 | 0.57 | 1.00 (n=1) | 0.14 |

Unit types: K1 = K(j), K2 = K(j→k), R1 = R(j), R2 = R(j→k).

## Router / STOP behaviour

- Router calls: 2; STOP decisions: 1 (0.50).
- Mean units per episode: router 1.00, random 2.00, dense 9.00.
- Router instantiated zero units in 0/1 symbolic zero-value instances and in 0/0 others.
- Mean Jaccard(router allocation, symbolic reference set): 0.00.

## Do decisions respond to variant knobs? (first action differs within a single-knob pair)

| knob | pairs | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|---|

## Overhead share of tokens (prompt + completion, means per episode)

| arm | decision | unit | refresh | router | router+unit share |
|---|---|---|---|---|---|
| direct | 2215 | 0 | 0 | 0 | 0.00 |
| dense | 3411 | 8044 | 0 | 0 | 0.70 |
| random | 2532 | 1794 | 0 | 0 | 0.41 |
| router | 1524 | 894 | 0 | 1869 | 0.64 |
| symbolic | 2918 | 0 | 0 | 0 | 0.00 |

## Invalid outputs and retries

- Calls with at least one failed attempt: 0; failure reasons: none.
- Calls that exhausted all attempts (fallback/abstain): 0.
