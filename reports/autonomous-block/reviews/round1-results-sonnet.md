# Round 1 results gate: Sonnet 5.5 independent numbers check

**Verdict:** CONSISTENT. No numeric discrepancy found. Commit checked: `15dfcc3`.

## Method
- The reviewer wrote its own v3.1 scorer from the documented rules: tie set within 1e-9, 0.2 support threshold, 0.5 commit line, 1e-3 floor.
- It ran over all 360 records in the 6 run directories and agrees with `score_output_v3` on every output: category, unsupported mass, log score, Brier, CE and TV.

## What it reproduced
- **Cells:** every reproduced cell matches `round1-results.md`.
  - Content counts, hallucination-type, unsupported mass, abstentions, proper scores and coverage were checked for API r5 v1/v2/v2.1, local r5 v1/v2/v2.1 and local r4 v2.1.
  - The only differences are display rounding: local r5 v2.1 Brier 0.475 is printed as 0.47, and API r5 v2.1 CE 0.485 as 0.49.
- **Paired rows:** all match.
  - API r5 v2.1 vs. v2: +0.278 / +0.284 / +0.148 / −2 / −0.151 / −19.
  - API r5 v2.1 vs. v1: +0.065 / +0.071 / +0.045 / 0 / −0.058 / 0.
  - Local r5 v2.1 vs. v1: −0.085 / −0.085 / +0.103 / −1 / −0.103 / 0.
  - API pilot-v1 r3 → r5: +0.268 / +0.262 / +0.107 / −1 / −0.112 / 0.
- **Summary claims, all verified:**
  - uc14–uc19 and uc04/05/21/24 for API r5 v1 and v2.1;
  - local v2.1's 3 committed unsupported outputs (uc01, uc09, uc15: `unknown` 1.0 'grounded');
  - API spend USD 0.5446 over 74 attempts (117,073 input and 31,048 output tokens);
  - two runaway attempts at the 6,000-token cap, uc05 and uc24, about $0.0623 each.
- **Ledger:** the 1.8570 snapshot could not be re-read, because Round 2 was already spending. It equals the pre-block 1.3123 plus the verified 0.5446.
- **Tie rule:** 140 tied-top outputs, each scored under every permutation of its hypothesis list. 0 categories depend on order, and the synthetic hand cases all follow the documented rule.

## Wording correction applied
- H1c said 'better than local in every package'. That holds for log score only. For pilot-v2 hallucination-type, API has 2 and local has 1. The summary is corrected.
