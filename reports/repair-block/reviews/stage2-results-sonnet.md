# Stage 2 results — Sonnet independent recompute

Reviewer: Sonnet 5.5. Raw data: `/home/aashraf/officeminds-runs/repair/repair-stage2-20261029-132459-743ace/episodes.jsonl` (4032 episodes; 24 seeds 20261100–20261123; 12 constructions; each base scenario has 4 episodes per condition, ×1/×4 × 2 draws; KR conditions only for 3a/3b/3c). Own code (scratchpad `recompute.py`, `p2.py`), no import of project scripts, no model calls. Bootstrap: stratified by construction, 20,000 resamples (seed 777123); sign-flip: 100,000 Monte Carlo (equal-construction-weight statistic; repeated at 200k with two other seeds). Rules: Entry 2 + Entry 1a RC3/RC4/RC6.

## Verdict: CONSISTENT

All point estimates, outcome counts, steps, per-construction and per-construction×stakes means, depth contrasts, headroom, and decision-compute totals reproduce exactly. CIs and p-values agree within resampling noise (CI ends within ~0.002; p within ~0.001). The class assignments and the pre-declared outcome (§5(3)) reproduce.

## Primary contrasts (n = 288 base scenarios; equal construction weight)

| Contrast | Reported est [95% CI], p | Recomputed est [95% CI], p |
|---|---|---|
| reference − none | −0.0240 [−0.0739, +0.0283], 0.3868 | −0.0240 [−0.0754, +0.0282], 0.3858 (0.3857, 0.3853 at 200k) |
| inferred − none | −0.0429 [−0.0977, +0.0127], 0.1508 | −0.0429 [−0.0987, +0.0128], 0.1508 (0.1501, 0.1507 at 200k) |
| inferred − reference | −0.0189 [−0.0660, +0.0270] | −0.0189 [−0.0663, +0.0263], p = 0.445 |

Per-construction mean differences (`d_by_construction_mean`) match the reported JSON for all 12 constructions and all three contrasts (e.g. ref−none 3b −0.3812, inferred−none 4c −0.3089, inferred−ref 2c +0.1974).

Classes and Holm:
- Holm: smaller p (inferred, 0.151) is not < 0.025; larger p (reference, 0.386) is not < 0.05. Neither is Holm-significant. Matches.
- Reference "no practical value" (CI upper < 0.05): upper = +0.028, so yes. Matches.
- Inferred "fails" (inferred − none CI upper < 0.05): upper = +0.013, so yes. The alternative clause (inferred − reference CI upper < −0.05) does not hold (upper +0.026). Matches (the first clause alone triggers).
- Anomaly (inferred − reference CI lower > +0.05): no. Matches.
- Outcome row "no practical value × fails" gives §5(3). Matches.

## Per stratum (condition − none)

| Stratum | Reported ref | Recomputed ref | Reported inf | Recomputed inf |
|---|---|---|---|---|
| 1 | +0.0069 [−0.0849, +0.1073] | +0.0069 [−0.0833, +0.1054] | +0.0047 [−0.0637, +0.0792] | +0.0047 [−0.0639, +0.0776] |
| 2 | −0.0441 [−0.1760, +0.0868] | −0.0441 [−0.1760, +0.0898] | +0.0262 [−0.1288, +0.1806] | +0.0262 [−0.1302, +0.1795] |
| 3 | −0.0762 [−0.1793, +0.0292] | −0.0762 [−0.1821, +0.0280] | −0.0599 [−0.1550, +0.0361] | −0.0599 [−0.1571, +0.0361] |
| 4 | +0.0175 [−0.0559, +0.0913] | +0.0175 [−0.0568, +0.0938] | −0.1425 [−0.2493, −0.0345] | −0.1425 [−0.2514, −0.0323] |

The inferred stratum-4 harm (CI excludes 0) reproduces; it is driven by 4c (−0.309) and 4b (−0.138).

## Outcomes and steps (exact match)

| Condition | success / error / timeout | mean steps |
|---|---|---|
| none | 880 / 205 / 67 | 3.1241 |
| inferred | 866 / 240 / 46 | 3.0443 |
| reference | 871 / 230 / 51 | 3.1259 |
| inferred_KR | 193 / 50 / 45 | 3.8194 |
| reference_KR | 226 / 58 / 4 | 3.0035 |

## By construction × stakes

All 120 cell means (condition × construction × stakes ∈ {1, 4}, n = 48 each; KR cells n = 48) match the reported table to the 3 printed decimals (spot values: none|1b|4 −0.598; reference|3b|4 −1.007; inferred|4c|4 −0.089; inferred_KR|3a|4 0.424).

## Depth (stratum 3)

| Contrast | Reported | Recomputed |
|---|---|---|
| reference 3a K(F→R)−K(R) | −0.0328 [−0.1187, +0.0536] | −0.0328 [−0.1203, +0.0531] |
| reference 3b | −0.1182 [−0.4224, +0.2010] | −0.1182 [−0.4271, +0.2031] |
| reference 3c | −0.0667 [−0.1443, +0.0005] | −0.0667 [−0.1458, +0.0005] |
| reference DiD (cond−none)[3b]−[3a] | −0.4172 [−0.7365, −0.0927] | −0.4172 [−0.7380, −0.0953] |
| inferred 3a | +0.3365 [+0.1750, +0.5120] | +0.3365 [+0.1719, +0.5083] |
| inferred 3b | +0.0359 [−0.2208, +0.2771] | +0.0359 [−0.2308, +0.2807] |
| inferred 3c | −0.1010 [−0.1766, −0.0323] | −0.1010 [−0.1750, −0.0323] |
| inferred DiD | −0.3786 [−0.6635, −0.1052] | −0.3786 [−0.6557, −0.1073] |

Both DiD CIs exclude 0 (negative): the note effect (cond − none) is lower in 3b than in 3a, driven by 3b (ref−none −0.381, inferred−none −0.316; `none` scores 0.235 in 3b stakes 1 and the notes lower it). Whether that is the intended direction for the depth hypothesis is for the reviewer; this is descriptive and not a discrepancy.

## Headroom (Bayes V* − condition mean, using `bayes_value_t0` from stage2-qualification.json)

| Condition | Reported | Recomputed (episode-mean = construction-mean) |
|---|---|---|
| none | 0.5038 | 0.5038 |
| inferred | 0.5467 | 0.5467 |
| reference | 0.5277 | 0.5277 |

## Decision compute (from episodes' `usage.decision`; all attempts charged)

| Condition | calls (reported = recomputed) | failed attempts | prompt tok | completion tok | reasoning tok |
|---|---|---|---|---|---|
| none | 3628 | 29 | 5,316,406 | 709,055 | 628,608 |
| inferred | 3525 | 18 | 5,488,195 | 693,147 | 614,372 |
| reference | 3620 | 19 | 5,648,500 | 701,305 | 620,606 |
| inferred_KR | 1103 | 3 | 1,775,176 | 204,678 | 181,106 |
| reference_KR | 870 | 5 | 1,401,868 | 177,015 | 158,275 |

All match the reported `decision_*` fields (latency sums also match, e.g. none 5213.41 s, inferred 5073.18 s). Fallbacks = 0 in every condition; reasoning tokens are known in every episode.

Not recomputable here: the `note_*` totals (note attempts, tokens, latency) for inferred/inferred_KR. They are not in `episodes.jsonl` (only `usage.decision` exists) and were not checked. The per-construction fidelity table is likewise not checked (it comes from the notes freeze, not from the episodes).

## Discrepancies

None material. Observations (not errors):
1. `usage.decision.calls` counts attempts (sum of `len(attempts)` across decision calls), including retries. The number of distinct decision calls is smaller (e.g. none 3599 vs 3628 attempts). The report's "decision_attempts" and "decision_calls" fields show the same number (the attempt count), so "decision_calls" is a slight misnomer. This does not change any conclusion.
2. The sign-flip p-values and CI endpoints differ from the report only by Monte Carlo/bootstrap noise (max |ΔCI| ≈ 0.005 in the stratum/depth cases, ≈ 0.002 in the primaries; max |Δp| ≈ 0.001).
3. The inferred − none CI is wide enough (upper +0.013) that "fails" rests on the CI-upper < δ rule, not on evidence of harm; the primary inferred − none estimate is −0.043 and not significant. The inferred stratum-4 harm is the only primary-family-level CI excluding 0, and it is a secondary contrast without multiplicity adjustment.
