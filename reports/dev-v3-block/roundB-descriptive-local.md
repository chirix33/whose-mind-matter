# Round B (local): post-hoc descriptives

**POST-HOC DESCRIPTIVE (after outcomes; not the pre-declared reading).** Run `dev-v3-notes-20261028-165208-67f601`.

## Outcomes per condition | stratum

- inferred|1: {'success': 12}; mean steps 2.25
- inferred|2: {'success': 12}; mean steps 2.667
- inferred|3: {'success': 12}; mean steps 2.917
- inferred|4: {'success': 9, 'error': 3}; mean steps 3.667
- none|1: {'success': 12}; mean steps 2.25
- none|2: {'success': 11, 'error': 1}; mean steps 2.417
- none|3: {'success': 11, 'timeout': 1}; mean steps 4.083
- none|4: {'success': 10, 'error': 2}; mean steps 3.667
- privileged|1: {'success': 12}; mean steps 2.417
- privileged|2: {'success': 12}; mean steps 2.667
- privileged|3: {'success': 12}; mean steps 2.833
- privileged|4: {'success': 12}; mean steps 2.917
- reference|1: {'success': 12}; mean steps 2.5
- reference|2: {'success': 11, 'error': 1}; mean steps 2.583
- reference|3: {'success': 12}; mean steps 2.667
- reference|4: {'success': 12}; mean steps 3

First action in the exact Bayes-optimal set: {'none': '6/48', 'inferred': '9/48', 'reference': '6/48', 'privileged': '3/48'}

Noise floor (identical prompts, reference vs privileged in 1c/3c): {'states': 8, 'ref_minus_priv': [0.0167, 0.0, 0.0167, -0.05, -0.0333, 0.0, 0.0167, 0.05], 'mean_abs': 0.0229, 'max_abs': 0.05}

Median-of-draws sensitivity of the R10 classes: {"inferred": {"classes": {"1": "inconclusive", "2": "null", "3": "positive", "4": "null"}, "reading": "inconclusive"}, "reference": {"classes": {"1": "null", "2": "inconclusive", "3": "null", "4": "null"}, "reading": "no measurable explicit-note headroom"}, "privileged": {"classes": {"1": "null", "2": "inconclusive", "3": "null", "4": "null"}, "reading": "no measurable explicit-note headroom"}}
