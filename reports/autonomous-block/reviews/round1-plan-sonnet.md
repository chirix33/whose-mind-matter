# Round 1 plan gate: Sonnet 5.5 facts/numbers check

- **Reviewer:** sub-agent, model sonnet (Sonnet 5.5). Read-only; it made no API calls.
- **Commit reviewed:** `03a52c1`.
- **Verdict:** DISCREPANCIES FOUND, all minor. All numbers verified.

## Findings
1. **Tests:** full suite, 275 passed.
2. **Reference audit:**
   - Replaying agent_view actions reproduces every history exactly.
   - `evidence_posterior` was recomputed for **all 24 contexts**, and each matches the stored posterior to 1e-9.
   - Every quoted number was verified: uc02 0.95/0.05; uc06 0.975/0.025; uc07 0.8667/0.1333; the 0.5/0.5 contexts; `unknown` = 1.0 in uc14, 16, 17, 18, 19 and 23; uc11 0.65/0.35 with `unknown` = 0.
   - Hidden template events were confirmed: uc10 `bs-vouch`; uc11 `bs-warn`; in uc07 the desk_9 claim is the lie.
   - Wording issues, none of which changes a flag:
     - uc11 said "no visible link at all", but the two people are co-present and ravi makes an incentive remark;
     - uc01's basis was garbled;
     - uc10 omitted the visible ask answer;
     - uc11 applies rule 1 to R(j→k) only by a loose reading.
3. **r4 re-render:**
   - 24 identical contexts, agent views and visible IDs; the sha256 matches.
   - For pilot-v1/v2 the only request difference is the people-rules paragraph (one diff hunk). System messages, schemas and domains are identical.
4. **The "23 of 24" row:**
   - The raw records for local medium pilot-v2 give 14 abstained, 8 correct-supported, 1 incorrect-supported, 1 unsupported, 0 correct-unsupported and 0 leakage, which sums to 24.
   - The generated `unit-contexts-results.md` was correct.
   - The hand table in `model-diagnostic.md` §2 was wrong: Incorrect (supported) showed 0 instead of 1. That was the only wrong row.

## Actions taken by the main session
- Corrected the audit wording for uc01, uc10 and uc11 (no flag changed). The change is disclosed in `reference-audit.json` → `wording_revisions`, including that it was made after Round 1 local outputs existed.
- Corrected the hand table in `reports/pilot/model-diagnostic.md`, with an erratum at the top.
