# Stage 2 results — run `repair-stage2-20261029-132459-743ace`

`scripts/report_repair_stage2.py` (frozen before outcomes). 288 base scenarios from 24 complete seed blocks; 4032 episodes, 0 blocked. Development data, local backbone.

## Primary (paired by base scenario; equal construction weight; 95% stratified bootstrap CI)

- reference − none: -0.0240 [-0.0739, +0.0283] (n=288); sign-flip p = 0.38678; Holm-significant: False
- inferred − none: -0.0429 [-0.0977, +0.0127] (n=288); sign-flip p = 0.15085; Holm-significant: False
- inferred − reference (secondary): -0.0189 [-0.0660, +0.0270] (n=288)

**Reference class: no practical value. Inferred class: fails. Pre-declared outcome: §5(3) reconsider method/environment fit.**

## Per stratum (condition − none)

- stratum 1: reference +0.0069 [-0.0849, +0.1073] (n=72); inferred +0.0047 [-0.0637, +0.0792] (n=72)
- stratum 2: reference -0.0441 [-0.1760, +0.0868] (n=72); inferred +0.0262 [-0.1288, +0.1806] (n=72)
- stratum 3: reference -0.0762 [-0.1793, +0.0292] (n=72); inferred -0.0599 [-0.1550, +0.0361] (n=72)
- stratum 4: reference +0.0175 [-0.0559, +0.0913] (n=72); inferred -0.1425 [-0.2493, -0.0345] (n=72)

## Outcomes and steps

- none: {'success': 880, 'error': 205, 'timeout': 67}; mean steps 3.12
- inferred: {'success': 866, 'timeout': 46, 'error': 240}; mean steps 3.04
- reference: {'success': 871, 'error': 230, 'timeout': 51}; mean steps 3.13
- inferred_KR: {'success': 193, 'timeout': 45, 'error': 50}; mean steps 3.82
- reference_KR: {'success': 226, 'error': 58, 'timeout': 4}; mean steps 3.00

Headroom (Bayes V* − condition mean): {'none': 0.5038, 'inferred': 0.5467, 'reference': 0.5277}

## Depth (RC13; descriptive; 3a/3c are label-only controls)

- reference|3a|K(F->R)-K(R): -0.0328 [-0.1187, +0.0536] (n=24)
- reference|3b|K(F->R)-K(R): -0.1182 [-0.4224, +0.2010] (n=24)
- reference|3c|K(F->R)-K(R): -0.0667 [-0.1443, +0.0005] (n=24)
- reference|DiD (cond-none)[3b]-(cond-none)[3a]: -0.4171875 [-0.7364583333333333, -0.09270833333333334] (n=24)
- inferred|3a|K(F->R)-K(R): +0.3365 [+0.1750, +0.5120] (n=24)
- inferred|3b|K(F->R)-K(R): +0.0359 [-0.2208, +0.2771] (n=24)
- inferred|3c|K(F->R)-K(R): -0.1010 [-0.1766, -0.0323] (n=24)
- inferred|DiD (cond-none)[3b]-(cond-none)[3a]: -0.3786458333333333 [-0.6635416666666667, -0.10520833333333332] (n=24)

## Inferred-note fidelity by construction

- 1a: {'n': 48, 'valid': 48, 'mean_tv': 0.0, 'mean_unsupported_mass': 0.0, 'abstained': 0, 'categories': {'correct_supported': 48}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 1b: {'n': 48, 'valid': 48, 'mean_tv': 0.0, 'mean_unsupported_mass': 0, 'abstained': 0, 'categories': {'correct_supported': 48}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 1c: {'n': 48, 'valid': 48, 'mean_tv': 0.0, 'mean_unsupported_mass': 0.0, 'abstained': 0, 'categories': {'correct_supported': 48}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 2a: {'n': 96, 'valid': 95, 'mean_tv': 0.1824563157894737, 'mean_unsupported_mass': 0.1824557894736842, 'abstained': 0, 'categories': {'correct_supported': 47, 'invalid': 1, 'supported_spread': 31, 'unsupported_committed': 17}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 2b: {'n': 48, 'valid': 48, 'mean_tv': 0.0, 'mean_unsupported_mass': 0.0, 'abstained': 0, 'categories': {'correct_supported': 48}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 2c: {'n': 96, 'valid': 95, 'mean_tv': 0.47017456315789474, 'mean_unsupported_mass': 0.2561392947368421, 'abstained': 0, 'categories': {'correct_supported': 9, 'incorrect_supported': 18, 'invalid': 1, 'supported_spread': 45, 'unsupported_committed': 23}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 3a: {'n': 96, 'valid': 95, 'mean_tv': 0.5824563157894737, 'mean_unsupported_mass': 0.5824557894736843, 'abstained': 0, 'categories': {'invalid': 1, 'supported_spread': 40, 'unsupported_committed': 55}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 3b: {'n': 96, 'valid': 95, 'mean_tv': 0.4350878947368421, 'mean_unsupported_mass': 0.4350873684210526, 'abstained': 0, 'categories': {'correct_supported': 23, 'invalid': 1, 'supported_spread': 31, 'unsupported_committed': 41}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 3c: {'n': 96, 'valid': 92, 'mean_tv': 0.06532608695652174, 'mean_unsupported_mass': 0.06532608695652174, 'abstained': 0, 'categories': {'correct_supported': 86, 'invalid': 4, 'unsupported_committed': 6}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 4a: {'n': 48, 'valid': 48, 'mean_tv': 0.0, 'mean_unsupported_mass': 0.0, 'abstained': 0, 'categories': {'correct_supported': 48}, 'prior_copies_raw': 0, 'prior_copies_discriminating': 0}
- 4b: {'n': 96, 'valid': 96, 'mean_tv': 0.2665186951379567, 'mean_unsupported_mass': 0.2998164583333333, 'abstained': 0, 'categories': {'correct_supported': 60, 'correct_unsupported': 1, 'incorrect_supported': 3, 'supported_spread': 4, 'unsupported_committed': 28}, 'prior_copies_raw': 35, 'prior_copies_discriminating': 14}
- 4c: {'n': 48, 'valid': 48, 'mean_tv': 0.24351979166666665, 'mean_unsupported_mass': 0.2788541666666667, 'abstained': 0, 'categories': {'correct_supported': 31, 'correct_unsupported': 1, 'incorrect_supported': 5, 'unsupported_committed': 11}, 'matches_prior_correct_in_4c': 19, 'over_updates_4c': 29}

Depth render diffs 3a/3c (reference K(F->R) vs K(R)): {'states': 96, 'differ_beyond_labels': 0}

Blocked episodes: 0; excluded base scenarios (reference−none / inferred−none): [] / []

Wall clock: {'notes_stage_s': 559.2, 'policy_stage_s': 2362.512934311, 'concurrency': None, 'reference_oracle_cpu_s_not_deployable': 1.53}

## Compute (all attempts charged)

- inferred: {'note_attempts': 883.0, 'note_attempts_missing_usage': 0.0, 'note_reasoning_tokens': 309946.0, 'note_prompt_tokens': 2421944.0, 'note_completion_tokens': 477445.0, 'note_latency_s': 3795.0644875099974, 'decision_attempts': 3525.0, 'decision_attempts_missing_usage': 0.0, 'episodes': 1152.0, 'decision_calls': 3525.0, 'decision_prompt_tokens': 5488195.0, 'decision_completion_tokens': 693147.0, 'decision_latency_s': 5073.177832706004, 'failed_attempts': 18.0, 'decision_reasoning_tokens': 614372.0, 'fallbacks': 0.0}
- inferred_KR: {'note_attempts': 171.0, 'note_attempts_missing_usage': 0.0, 'note_reasoning_tokens': 40522.0, 'note_prompt_tokens': 483843.0, 'note_completion_tokens': 70364.0, 'note_latency_s': 560.0427612450003, 'decision_attempts': 1103.0, 'decision_attempts_missing_usage': 0.0, 'episodes': 288.0, 'decision_calls': 1103.0, 'decision_prompt_tokens': 1775176.0, 'decision_completion_tokens': 204678.0, 'decision_latency_s': 1483.0350237830057, 'failed_attempts': 3.0, 'decision_reasoning_tokens': 181106.0, 'fallbacks': 0.0}
- none: {'decision_attempts': 3628.0, 'decision_attempts_missing_usage': 0.0, 'episodes': 1152.0, 'decision_calls': 3628.0, 'decision_prompt_tokens': 5316406.0, 'decision_completion_tokens': 709055.0, 'decision_latency_s': 5213.4085344990035, 'failed_attempts': 29.0, 'decision_reasoning_tokens': 628608.0, 'fallbacks': 0.0}
- reference: {'decision_attempts': 3620.0, 'decision_attempts_missing_usage': 0.0, 'episodes': 1152.0, 'decision_calls': 3620.0, 'decision_prompt_tokens': 5648500.0, 'decision_completion_tokens': 701305.0, 'decision_latency_s': 5156.854964796998, 'failed_attempts': 19.0, 'decision_reasoning_tokens': 620606.0, 'fallbacks': 0.0}
- reference_KR: {'decision_attempts': 870.0, 'decision_attempts_missing_usage': 0.0, 'episodes': 288.0, 'decision_calls': 870.0, 'decision_prompt_tokens': 1401868.0, 'decision_completion_tokens': 177015.0, 'decision_latency_s': 1278.2173904030014, 'failed_attempts': 5.0, 'decision_reasoning_tokens': 158275.0, 'fallbacks': 0.0}

## By construction × stakes (mean return)

- inferred|1a|1: 0.871
- inferred|1a|4: 0.857
- inferred|1b|1: 0.150
- inferred|1b|4: -0.495
- inferred|1c|1: 0.882
- inferred|1c|4: 0.879
- inferred|2a|1: 0.741
- inferred|2a|4: 0.689
- inferred|2b|1: -0.029
- inferred|2b|4: -0.712
- inferred|2c|1: 0.170
- inferred|2c|4: -0.687
- inferred|3a|1: 0.831
- inferred|3a|4: 0.824
- inferred|3b|1: -0.166
- inferred|3b|4: -0.877
- inferred|3c|1: 0.818
- inferred|3c|4: 0.654
- inferred|4a|1: 0.772
- inferred|4a|4: 0.710
- inferred|4b|1: 0.584
- inferred|4b|4: 0.150
- inferred|4c|1: 0.580
- inferred|4c|4: -0.089
- inferred_KR|3a|1: 0.558
- inferred_KR|3a|4: 0.424
- inferred_KR|3b|1: -0.135
- inferred_KR|3b|4: -0.979
- inferred_KR|3c|1: 0.840
- inferred_KR|3c|4: 0.834
- none|1a|1: 0.872
- none|1a|4: 0.877
- none|1b|1: 0.199
- none|1b|4: -0.598
- none|1c|1: 0.880
- none|1c|4: 0.886
- none|2a|1: 0.881
- none|2a|4: 0.685
- none|2b|1: -0.050
- none|2b|4: -0.825
- none|2c|1: -0.025
- none|2c|4: -0.654
- none|3a|1: 0.725
- none|3a|4: 0.804
- none|3b|1: 0.235
- none|3b|4: -0.647
- none|3c|1: 0.748
- none|3c|4: 0.578
- none|4a|1: 0.787
- none|4a|4: 0.656
- none|4b|1: 0.595
- none|4b|4: 0.416
- none|4c|1: 0.559
- none|4c|4: 0.550
- reference|1a|1: 0.898
- reference|1a|4: 0.880
- reference|1b|1: 0.206
- reference|1b|4: -0.550
- reference|1c|1: 0.855
- reference|1c|4: 0.869
- reference|2a|1: 0.685
- reference|2a|4: 0.751
- reference|2b|1: -0.131
- reference|2b|4: -0.645
- reference|2c|1: 0.002
- reference|2c|4: -0.915
- reference|3a|1: 0.809
- reference|3a|4: 0.792
- reference|3b|1: -0.167
- reference|3b|4: -1.007
- reference|3c|1: 0.772
- reference|3c|4: 0.787
- reference|4a|1: 0.809
- reference|4a|4: 0.789
- reference|4b|1: 0.589
- reference|4b|4: 0.403
- reference|4c|1: 0.601
- reference|4c|4: 0.478
- reference_KR|3a|1: 0.833
- reference_KR|3a|4: 0.833
- reference_KR|3b|1: -0.194
- reference_KR|3b|4: -0.744
- reference_KR|3c|1: 0.850
- reference_KR|3c|4: 0.843
