# Round 3 results: replication and matched doubt control (development data; exploratory)

Run `notes-value-20261028-090725-c312fa` (commit `578fb6f`, dirty paths 0); policy gpt-6.1-sol effort low, cap 6000, rules r5, concurrency 4, stage cap env 4.156. Episodes 112, blocked 0. Wall clock 238 s.
Every injected payload hash was checked against `round3-notes-freeze.json` / `round2-notes-freeze.json`. At s1 and s9 reference_doubt is byte-identical to inferred_bare (rendered-note hashes equal), so the s9 doubt arm pools both cells (8 draws).

## s9 (H3a replication, H3b doubt): successes / draws

| condition | Round 3 | Round 2 (not pooled) | combined (descriptive) | Round 3 actions |
|---|---|---|---|---|
| none | 0/4 | 0/3 | 0/7 | ask(dave,yara_loc) drop(lab_north) ×4 |
| reference | 0/4 | 0/3 | 0/7 | ask(dave,yara_loc) drop(lab_north) ×4 |
| reference_doubt | 3/4 | 0/— | 3/4 | ask(dave,yara_loc) move(hall) move(lab_north) move(hall) move(lab_south) deliver() ×3; ask(dave,yara_loc) drop(lab_north) ×1 |
| inferred_bare | 4/4 | 3/3 | 7/7 | ask(dave,yara_loc) move(hall) move(lab_north) move(hall) move(lab_south) deliver() ×4 |
| **pooled doubt arm** (reference_doubt + inferred_bare, identical prompts) | **7/8** | 3/3 (inferred_bare) | 10/11 | |

**H3a (replication: none ≤1/4, reference ≤1/4, pooled doubt ≥6/8): holds.** **H3b (pooled ≥6/8 with reference ≤1/4 → holds; pooled ≤2/8 → fails; else inconclusive): holds.**

## H3c: reference_doubt − reference (and − none) in the other states (mean return over 4 draws; mean steps)

| state | stratum | none | reference | reference_doubt | doubt − reference | doubt − none | steps none / ref / doubt | first action differs from modal reference |
|---|---|---|---|---|---|---|---|---|
| s1 | s9 twin | +0.800 | +0.750 | +0.762 | +0.012 | -0.037 | 4.00 / 5.00 / 4.75 | 0/4 |
| s2 | K(recipient) | +0.750 | +0.850 | +0.850 | +0.000 | +0.100 | 5.00 / 3.00 / 3.00 | 0/4 |
| s3 | other | +0.950 | +0.950 | +0.850 | -0.100 | -0.100 | 1.00 / 1.00 / 3.00 | 4/4 |
| s4 | K(recipient) | +0.712 | +0.837 | +0.775 | -0.062 | +0.062 | 5.75 / 3.25 / 4.50 | 2/4 |
| s5 | K(recipient) | +0.900 | +0.825 | +0.825 | +0.000 | -0.075 | 2.00 / 3.50 / 3.50 | 0/4 |
| s6 | other | +0.750 | +0.900 | +0.800 | -0.100 | +0.050 | 5.00 / 2.00 / 4.00 | 4/4 |
| s7 | other | +0.850 | +0.850 | +0.850 | +0.000 | +0.000 | 3.00 / 3.00 / 3.00 | 0/4 |
| s8 | other | +0.950 | +0.950 | +0.950 | +0.000 | +0.000 | 1.00 / 1.00 / 1.00 | 0/4 |
| s9 | s9 | -0.600 | -0.600 | +0.375 | +0.975 | +0.975 | 2.00 / 2.00 / 5.00 | 0/4 |

| group | states | mean doubt − reference | mean doubt − none | negative / positive states (vs reference) |
|---|---|---|---|---|
| all 8 (excl. s9) | s1, s2, s3, s4, s5, s6, s7, s8 | -0.031 | +0.000 | 3 / 1 |
| K(recipient): doubt contradicts rule 2 | s2, s4, s5 | -0.021 | +0.029 | 1 / 0 |
| other | s3, s6, s7, s8 | -0.050 | -0.012 | 2 / 0 |
| s1 (s9 twin) | s1 | +0.012 | -0.037 | 0 / 1 |

**H3c (8-state mean ≤ −0.025 and negative > positive states): holds** (mean -0.031; 3 negative, 1 positive).

## Replication check: none − reference per state (Round 3 vs Round 2)

| state | R3 none | R3 reference | R3 none − ref | R2 none − ref | R3 none successes | R3 reference successes |
|---|---|---|---|---|---|---|
| s1 | +0.800 | +0.750 | +0.050 | +0.100 | 4/4 | 4/4 |
| s2 | +0.750 | +0.850 | -0.100 | -0.100 | 4/4 | 4/4 |
| s3 | +0.950 | +0.950 | +0.000 | +0.000 | 4/4 | 4/4 |
| s4 | +0.712 | +0.837 | -0.125 | -0.100 | 4/4 | 4/4 |
| s5 | +0.900 | +0.825 | +0.075 | +0.083 | 4/4 | 4/4 |
| s6 | +0.750 | +0.900 | -0.150 | -0.133 | 4/4 | 4/4 |
| s7 | +0.850 | +0.850 | +0.000 | +0.000 | 4/4 | 4/4 |
| s8 | +0.950 | +0.950 | +0.000 | +0.000 | 4/4 | 4/4 |
| s9 | -0.600 | -0.600 | +0.000 | +0.000 | 0/4 | 0/4 |

## Compute and cost

| condition | episodes | mean steps | mean prompt tokens | mean completion tokens | mean USD / episode |
|---|---|---|---|---|---|
| none | 36 | 3.19 | 3279 | 92 | 0.0075 |
| reference | 36 | 2.64 | 2884 | 125 | 0.0070 |
| reference_doubt | 36 | 3.53 | 3877 | 140 | 0.0092 |
| inferred_bare | 4 | 6.00 | 6778 | 180 | 0.0154 |

Round 3 policy spend from tokens: USD 0.9130. Failed attempts: 0.
