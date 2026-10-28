# Pilot integration results: run `pilot-integration-20261028-060439-f22f04`

Frozen set `dev-v2` (set hash `3e8afe544f7e2900…`), commit `151846b`, model `gpt-oss-20b`, prompts `pilot-v1` renderer r2, decoding {'temperature': 0.0, 'max_tokens': 1024, 'reasoning_effort': 'low'}, concurrency 1. Development data: exploratory pilot, not a confirmatory result. Temperature 0 does not guarantee reproducibility under vLLM batching; serving settings are recorded in the manifest.

## Outcomes by arm

| arm | episodes | success | error | timeout | mean return | mean steps | units/episode | unit calls ok | unit top = truth | router STOPs | failed attempts | fallbacks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 1 | 1.00 | 0.00 | 0.00 | +0.850 | 3.00 | 0.00 | 0/0 | — | 0 | 0 | 0 |
| dense | 1 | 1.00 | 0.00 | 0.00 | +0.850 | 3.00 | 9.00 | 9/9 | 0.44 | 0 | 0 | 0 |
| random | 1 | 1.00 | 0.00 | 0.00 | +0.850 | 3.00 | 2.00 | 2/2 | 0.50 | 0 | 0 | 0 |
| router | 1 | 1.00 | 0.00 | 0.00 | +0.900 | 2.00 | 1.00 | 1/1 | 1.00 | 1 | 0 | 0 |
| symbolic | 1 | 1.00 | 0.00 | 0.00 | +0.800 | 4.00 | 0.00 | 0/0 | — | 0 | 0 | 0 |

## Compute per episode (means; API calls include retries)

| arm | call kind | calls | prompt tok | completion tok | reasoning tok | summed call latency (s) |
|---|---|---|---|---|---|---|
| direct | decision | 3.00 | 2050 | 165 | 92 | 0.81 |
| dense | decision | 3.00 | 3238 | 173 | 100 | 0.72 |
| dense | unit | 9.00 | 6141 | 1903 | 1100 | 7.03 |
| random | decision | 3.00 | 2353 | 179 | 106 | 0.70 |
| random | unit | 2.00 | 1359 | 435 | 238 | 1.59 |
| router | decision | 2.00 | 1367 | 157 | 109 | 0.60 |
| router | router | 2.00 | 1648 | 221 | 172 | 0.87 |
| router | unit | 1.00 | 679 | 215 | 128 | 0.79 |
| symbolic | decision | 4.00 | 2674 | 244 | 156 | 0.94 |

| arm | mean episode wall clock (s, monotonic) | median |
|---|---|---|
| direct | 0.82 | 0.82 |
| dense | 7.75 | 7.75 |
| random | 2.29 | 2.29 |
| router | 2.25 | 2.25 |
| symbolic | 0.94 | 0.94 |

Episode wall clock is measured per episode while other episodes ran concurrently (contention included); summed call latency is NOT elapsed time.

## Mean return by family and arm

| family | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|
| false_belief | +0.850 | +0.850 | +0.850 | +0.900 | +0.800 |
