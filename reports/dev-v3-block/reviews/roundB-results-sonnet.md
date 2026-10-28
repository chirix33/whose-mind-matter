# Round B results: independent numerical check (Sonnet 5.5)

Run `dev-v3-notes-20261028-165208-67f601` (192 episodes). My own code (scratch scripts `chk.py`, `chk2.py`; no repo scripts imported; no LLM or server calls). Classifications were recomputed twice: in floats, and in exact rational arithmetic (all returns are multiples of 0.05).

## Verdict: DISCREPANCIES (minor; none touches the main pre-declared reading)

The pre-declared readings (inferred: inconclusive; reference and privileged: headroom present), all per-state returns, d_s, stratum means, outcome counts, first-action rates and the noise floor reproduce exactly. Three items need correction in `roundB-summary.md` / the descriptive report:

1. **Failed inferred notes are 5 of 24, not 6 of 24.** The summary says "6 of 24 ... failed" and "In the 18 valid notes".
   - Recomputed from `roundB-notes-local.json`: failed (`ok` false, 3 attempts each, validation errors `cites_non_visible_evidence` + `rule_citation_mismatch` on every attempt): R(uma) 4b-x1-perm0; R(kim) and R(uma) 4b-x4-perm0; R(uma) and R(zane) 4b-x4-perm1. That is 5 units, all R-type in 4b.
   - The results table in `roundB-results-local.md` itself lists exactly these 5 `invalid` rows, so the summary text disagrees with its own table. Valid notes: 19.
   - The summary also says "the two valid 4b notes split". There are three valid 4b notes: R(kim) 4b-x1-perm0 correct_supported, R(uma) 4b-x1-perm1 correct_supported, R(zane) 4b-x1-perm1 unsupported_committed (top cooperative 0.7 against a reference of 0.045). So 2 correct, 1 unsupported_committed.
   - Likely cause: a miscount or a leftover figure from an earlier draft. The note-call count (37 attempts for 24 units: 5 x 3 failed + 22 attempts across the other 19 valid) is consistent with 5.
2. **Median-of-draws sensitivity for the inferred condition is a floating-point boundary artifact.** `roundB-descriptive-local.md` gives inferred median classes {1: inconclusive, 2: null, 3: null, 4: null} and reading "no measurable explicit-note headroom". The summary then says this holds "for every condition".
   - Stratum 3 inferred, median d_s = [-0.05, +0.05, +0.10, +0.10], whose mean is exactly +0.05, with 3 of 4 d_s > 0. Under R10 ("mean >= +0.05 and >= 3 of 4 d_s > 0") that is **positive**, not null.
   - In floats the d_s come out as [-0.050000000000000044, 0.050000000000000044, 0.09999999999999998, 0.09999999999999998], mean 0.04999999999999999, so the `>= 0.05` test fails. I reproduced this in floats.
   - Corrected inferred median reading: strata 2-4 = null / positive / null. That is one positive and two null, so it is neither "headroom present" (needs >= 2 positive) nor "no measurable headroom" (needs 0 positive): **inconclusive**.
   - Reference and privileged median readings ("no measurable headroom") are robust to exact arithmetic.
   - Effect on the summary: "reverses to no measurable headroom for every condition" should read "for reference and privileged; inferred is borderline-inconclusive". The reference fragility conclusion stands. Suggest comparing with exact (Fraction) arithmetic or a 1e-9 tolerance.
3. **The B2 cost inputs are the `none` condition only** (see the table below). This does not change the conclusion: my range is about USD 1.3 to 2.6, above the USD 0.80 allowance.

Minor wording issue (not a numeric error): the summary says every 1c/2a/3c note is "correct_supported or supported_spread against the posterior". True by the scoring rule, but the two K(yara) notes in 2a x1-perm0 and x4-perm0 put 0.333 mass on office_b, which has zero reference posterior (`unsupported_mass` 0.3333, `tv_posterior` 0.333 in the JSON). In x1-perm0 this note is still labelled correct_supported with status "grounded" at top p = 0.5.

## Recomputed vs reported

| Quantity | Reported | Recomputed | Match |
|---|---|---|---|
| Per state x condition draws (64 cells x 3) | `roundB-results-local.md` table | identical in all cells (also checked outcomes/means for sample cells in table order) | yes |
| Bayes V* and optimal first actions | e.g. 0.950 / 0.868 / 0.844 | same from `qualification.json` | yes |
| inferred d_s means by stratum 1-4 | 0.0 / 0.2375 / 0.1417 / -0.25 | same | yes |
| reference d_s means | -0.0125 / 0.1167 / 0.1542 / 0.4083 | same | yes |
| privileged d_s means | -0.0083 / 0.2375 / 0.1458 / 0.4125 | same | yes |
| Classes, inferred | inc / inc / pos / inc | same | yes |
| Classes, reference | null / inc / pos / pos | same | yes |
| Classes, privileged | null / inc / pos / pos | same | yes |
| Overall readings | inferred inconclusive; reference, privileged headroom present | same | yes |
| Outcome counts (none) | 3 err + 1 timeout (2a:1 err; 3c:1 timeout; 4b:2 err) | same | yes |
| Outcome counts (inferred / reference / privileged) | 3 err (all 4b) / 1 err (2a) / 0 | same | yes |
| Mean steps by condition x stratum | e.g. none\|3 = 4.083, inferred\|4 = 3.667 | same (all 16 cells) | yes |
| First action in Bayes-optimal set | none 6/48, inferred 9/48, reference 6/48, privileged 3/48 | same | yes |
| Noise floor (ref - priv, 8 identical-prompt states) | mean abs 0.0229, max 0.05, 8 diffs | same values (0.0167, 0, 0.0167, -0.05, -0.0333, 0, 0.0167, 0.05) | yes |
| Median classes, reference | null-ish: 1 null, 2 inc, 3 null, 4 null | same (no measurable headroom) | yes |
| Median classes, privileged | same | same | yes |
| Median classes, inferred | 1 inc, 2 null, 3 null, 4 null -> no measurable headroom | 1 inc, 2 null, 3 **positive** (exact mean 0.05), 4 null -> inconclusive | **no (float boundary)** |
| Failed inferred notes | 6 of 24 (summary text); 5 `invalid` rows (table) | 5 of 24 | **summary wrong** |
| Valid 4b notes | "two valid 4b notes" | three (2 correct_supported, 1 unsupported_committed) | **summary wrong** |
| Failure validation errors | `cites_non_visible_evidence`, `rule_citation_mismatch` | every failed attempt carries exactly these two | yes |
| Note-generation usage | 37 calls, 79,143 prompt, 14,911 completion tokens | 37 attempts, 79,143, 14,911 | yes |
| Policy usage per condition (decision "calls") | none 149, inferred 138, reference 131, privileged 131 | these are attempts (549 total, 3 retries); decision calls = steps = 546 (129 / 130 for reference / privileged) | yes (label: attempts) |
| Fidelity categories (19 valid rows) | per table | status/top/posterior re-derived from the frozen notes and `qualification.json`; categories consistent with `src/vomi/fidelity.py` rules (read-only) | yes |

## Note-fidelity spot-check (against frozen notes and qualification posteriors)

- All four 1c notes and all four 3c notes: top = truth = posterior top with p = 1.0, grounded. Correct.
- 2a: K(ravi)/K(judy) with office_b p = 1 match a posterior of {office_b: 1}; the two K(ravi) uncertain notes {a .5, c .5} match the posterior exactly, giving supported_spread. The two K(yara) notes carry unsupported mass 0.333 (see wording note above).
- 4b: R(kim) .98 vs .945 (TV 0.035) and R(uma) .969 vs .945 (TV 0.024) are correct_supported; R(zane) cooperative 0.7 vs posterior 0.045 gives TV 0.655, unsupported_committed. In both the 4b x4-perm0 and x4-perm1 states, both notes are missing, so the inferred condition there shows no note (equal to `none` in content, though not listed under "identical rendered conditions", which covers only reference/privileged).

## B2 cost estimate (summary: about USD 1.9)

Inputs from the run's usage:

| Measure | Reported | Measured |
|---|---|---|
| Prompt tokens per decision call | about 1,490 | none 1,491; inferred 1,598; reference 1,560; privileged 1,546; **all 4 conditions 1,547** |
| Decision calls per episode | about 3.1 | none 3.10; inferred 2.88; reference 2.73; privileged 2.73; **all 4 conditions 2.86** (attempts) |
| Local completion tokens per call | not stated | about 162 (reasoning included, low effort local model) |
| Note calls | 24 | 24 units, 37 attempts locally (1.54 attempts per unit), about 2,139 prompt and 403 completion tokens per attempt |

The summary's 1,490 and 3.1 are the `none` condition's values, not the average over the four conditions. With all-condition averages the input bill is almost the same (see below), so this is a labeling issue only.

My estimate (64 episodes = 16 states x 4 conditions x 1 draw, USD 2 / 10 per Mtok, output including reasoning):

| Component | Low | High |
|---|---|---|
| Policy input: 64 x 2.84 to 3.1 calls x 1,490 to 1,547 tokens | 0.54 | 0.61 |
| Policy output: same calls x 300 to 800 tokens | 0.55 | 1.59 |
| Note input: 24 to 37 attempts x about 2,139 tokens | 0.10 | 0.16 |
| Note output: 24 to 37 attempts x 400 to 1,000 tokens | 0.10 | 0.37 |
| **Total** | **about 1.3** | **about 2.7** |

The summary's USD 1.9 lies inside this range (it implies roughly 550 output tokens per call). The conclusion "exceeds the USD 0.80 stage allowance" holds across the whole range, even at the lowest end: input alone is about USD 0.64 to 0.77, and 300 output tokens per call already pushes the total past 1.2. The USD 1.13 remaining would also not cover the high end. Caveat: API-model episode length, effort and retry rates are not measured, and the model could take fewer steps than the local policy, which asks first in most episodes.

## Files

- Report: `C:\Users\aashraf\Desktop\Work\2026\whose mind matters\reports\dev-v3-block\reviews\roundB-results-sonnet.md`
- Scratch scripts: `C:\Users\aashraf\AppData\Local\Temp\claude\C--Users-aashraf-Desktop-Work-2026-whose-mind-matters\fda39f03-9895-4d77-a7ce-8364ec7c76c3\scratchpad\chk.py`, `...\chk2.py`
