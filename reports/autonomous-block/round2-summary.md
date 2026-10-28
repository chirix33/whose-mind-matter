# Round 2 summary: replicated value-of-notes diagnostic (development data; exploratory)

**Full tables:** `round2-results.md`, from `scripts/report_round2.py`, which implements the pre-registered analysis.

**Gates:**
- Sonnet numbers check (`reviews/round2-results-sonnet.md`): CONSISTENT. Everything was reproduced from raw episodes and payload hashes.
- Opus results review (`reviews/round2-results-r3plan-opus.md`, Part A): PASS WITH REQUIRED CHANGES, applied below. **The earlier "integration-limited at s9" claim is withdrawn.**

**Run:** `notes-value-20261028-085354-5b41df`, at clean commit `7c22105`.
- The frozen-note proof `round2-notes-freeze.json` was committed before the policy stage, and every injected payload hash was checked against it.
- 135 episodes: 9 states × 5 conditions × 3 draws. None blocked, 0 failed attempts.
- **API spend:** notes USD 0.0610, policy USD 1.0379. Ledger total USD 2.9559 of 5.00.
- Counts: 9 scenarios, 1 frozen note per state × condition, 3 policy draws.

## Results
1. **No condition meets the pre-registered "reliable" criterion.**

   | Condition | Mean Δ vs. none | Better / worse / tie states | Robustness |
   |---|---|---|---|
   | inferred | +0.039 | 3 / 4 / 2 | reversed by dropping one draw |
   | inferred_bare | +0.130 | 2 / 3 / 4 | +1.30 at s9 alone; −0.017 without s9 |
   | reference | +0.017 | 3 / 2 / 4 | — |
   | privileged | +0.057 | 5 / 1 / 3 | bootstrap 90% over states [+0.007, +0.115]; fails the useful-states test (2 of 4) |

2. **Little headroom by realized outcome.**
   - Without notes the API policy succeeds in 8 of 9 states (24/27 draws). Elsewhere, return differences mostly reflect step counts (−0.05 per step).
   - "Headroom" here means realized success. Before outcomes, risky behaviour is present more widely. At **s1**, the public twin of s9 (the same "I saw X head to the office earlier", an ask and an answer; only the hidden "moved" differs), `none` dropped directly after asking in 2 of 3 draws, at ×4 stakes where a wrong drop costs −2.
   - Dropping is optimal only if P(still there) > 0.966. It succeeded because the recipient had not moved.
3. **Privileged-information dependence: true-belief content leaks the target.**
   - In 8 of 9 states (all but s9) the privileged content is exactly where delivery succeeds.
   - The policy used it fully at s2, s4 and s5 (direct actions, 3/3 first actions changed), partly at s6 (2/3 went direct), and at s1 only by skipping the second ask.
   - It hurt at s8 (−0.083).
   - Privileged episodes take 1.93 steps on average, against 3.07 without notes, and cost USD 0.0049 vs. 0.0072 per episode.
   - This is information about the hidden target conveyed through true-belief content, not mental-state value. s9 is the only false-belief state.
4. **Reference notes ≈ none (+0.017).** The small gains are in stratum B (s2 +0.10, s6 +0.13, s7 0), where the reference carries the generator's undisclosed base rates. Stratum A (s3, n = 1): 0.
5. **Stratum C is not a clean null control (list-order artifact at s4).**
   - At s4, every note condition, including the uninformative 0.5/0.5 reference, went to office_a first.
   - office_a is listed first, and it is also the truth.
   - `none` went to office_b first in 3/3 draws.
   - So s4's +0.10 to +0.12 is a tie-break effect of the note's listing order, not content.
6. **Inferred notes add caution, which costs steps in confident states.**
   - At s3, s5 and s8, inferred or inferred_bare notes add steps where `none` acts directly (s3 −0.07/−0.10, s5 −0.08/−0.05, s8 −0.08/0).
   - Presentation differences (inferred − inferred_bare: −0.091 overall, −0.19 in stratum C) are at noise level with 3 draws.
7. **s9 is a risk-calibration failure, and integration of false-belief content was not tested.**
   - In all 15 s9 episodes the policy asked Dave first and heard "yara_loc = lab_north". The privileged note ("Dave believes lab_north", p = 1) therefore repeated information every episode already had. It does not say the belief is outdated, so privileged ≈ none is expected and **does not test** whether the policy can use false-belief content.
   - After the ask, dropping returns +0.9 or −0.6, and verifying returns about +0.7 or +0.8. Dropping is optimal only if P(Yara still at lab_north) > 0.929.
   - r5 rule 1 says beliefs can be outdated, so dropping is a policy risk-calibration error, present in every condition (none, reference and privileged 0/3).
   - Notes carrying 0.2 `unknown` mass coincided with verification: inferred_bare 3/3 and inferred 1/3 (1/3 vs. 3/3 is within sampling noise).
   - The doubt mass is **not supported by the reference**, which never allows "Dave has no belief". Under public rules 4 and 6, a hedge on the informant is defensible.
   - The doubt mass is not the only trigger: at s1 the reference (0.5/0.5, no unknown mass) produced verification in 3/3 draws.
8. **Why the "useful" labels show near-zero value.** At s1 and s9 the unit belongs to a person who is present and can be asked. The note's content can be had for one 0.05 ask, so it is worth at most about one step. This is a gap between the symbolic labels and an LLM policy that asks.
9. **Compute.**
   - Notes add decision-prompt tokens: inferred +29% (4,046 vs. 3,141 per episode); USD per episode 0.0092 vs. 0.0072.
   - Note generation (USD 0.0610 for 9 notes) is a one-time experimental cost, not free in deployment.

## Pre-registered mapping (brief §8), as corrected
- **Little headroom here** (by realized outcome) **plus privileged-information dependence.** The only consistent gain comes from privileged true-belief content that reveals the target.
- **Integration of false-belief content: inconclusive.** It was not tested by these states.
- **s9:** a risk-calibration failure on possibly stale testimony, present in all conditions. Doubt-carrying notes act as a caution cue in one state (replication and matched control in Round 3).
- **No usable grounded value signal on these states. No evidence for or against an inference limit:** inferred ≈ reference holds by construction outside s2 and s6, and stratum A has n = 1.

## Limitations
- 9 states and 3 draws. The states are a mixed diagnostic set, not certified cases of required mental reasoning.
- Single note draws.
- Presentation and status differ between inferred and computed notes; `inferred_bare` controls only part of that.
- The reference uses undisclosed generator knowledge in stratum B.
- There is a list-order artifact at s4.
- All results are exploratory, on inspected development data.
