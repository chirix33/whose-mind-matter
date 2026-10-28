# Pilot integration results: run `pilot-integration-20261028-060221-70b781`

Frozen set `dev-v2` (set hash `3e8afe544f7e2900…`), commit `0747536`, model `gpt-oss-20b`, prompts `pilot-v1`, decoding {'temperature': 0.0, 'max_tokens': 1024, 'reasoning_effort': 'low'}, concurrency 1. Development data: exploratory pilot, not a confirmatory result. Temperature 0 does not guarantee reproducibility under vLLM batching; serving settings are recorded in the manifest.

## Outcomes by arm

| arm | episodes | success | error | timeout | mean return | mean steps | units/episode | unit calls ok | unit top = truth | router STOPs | failed attempts | fallbacks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direct | 1 | 1.00 | 0.00 | 0.00 | +0.800 | 4.00 | 0.00 | 0/0 | — | 0 | 0 | 0 |
| dense | 1 | 1.00 | 0.00 | 0.00 | +0.750 | 5.00 | 10.00 | 9/10 | 0.40 | 0 | 4 | 1 |
| random | 1 | 1.00 | 0.00 | 0.00 | +0.900 | 2.00 | 2.00 | 2/2 | 0.50 | 0 | 0 | 0 |
| router | 1 | 1.00 | 0.00 | 0.00 | +0.800 | 4.00 | 0.00 | 0/0 | — | 4 | 0 | 0 |
| symbolic | 1 | 1.00 | 0.00 | 0.00 | +0.800 | 4.00 | 0.00 | 0/0 | — | 0 | 0 | 0 |

## Compute per episode (means; API calls include retries)

| arm | call kind | calls | prompt tok | completion tok | reasoning tok | summed call latency (s) |
|---|---|---|---|---|---|---|
| direct | decision | 4.00 | 2736 | 221 | 133 | 1.76 |
| dense | decision | 5.00 | 5859 | 269 | 156 | 1.15 |
| dense | unit | 13.00 | 8999 | 2818 | 1542 | 10.42 |
| random | decision | 2.00 | 1455 | 203 | 155 | 0.77 |
| random | unit | 2.00 | 1367 | 408 | 234 | 1.50 |
| router | decision | 4.00 | 2696 | 261 | 173 | 1.00 |
| router | router | 4.00 | 3418 | 540 | 452 | 2.09 |
| symbolic | decision | 4.00 | 2696 | 277 | 189 | 1.04 |

| arm | mean episode wall clock (s, monotonic) | median |
|---|---|---|
| direct | 1.76 | 1.76 |
| dense | 11.57 | 11.57 |
| random | 2.26 | 2.26 |
| router | 3.09 | 3.09 |
| symbolic | 1.04 | 1.04 |

Episode wall clock is measured per episode while other episodes ran concurrently (contention included); summed call latency is NOT elapsed time.

## Mean return by family and arm

| family | direct | dense | random | router | symbolic |
|---|---|---|---|---|---|
| false_belief | +0.800 | +0.750 | +0.900 | +0.800 | +0.800 |
