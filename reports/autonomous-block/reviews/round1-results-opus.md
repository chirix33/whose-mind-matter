# Round 1 results gate: Opus 5.5 scientific-validity review

- **Reviewer:** sub-agent, model opus (Opus 5.5). Read-only; it made no API calls.
- **Commit reviewed:** `15dfcc3`.
- **Verdict:** PASS WITH REQUIRED CHANGES. All were applied to `round1-summary.md`.

## Required changes
1. **H1b:** supported on the API, NOT locally. Local v2.1 vs. v2 has hallucination-type 1 → 3 and CE −0.30, which fails the pre-registered condition.
2. **H1c** asked whether package differences hold on both models. The answer is no.
3. **H1a caveats:**
   - it was declared for r4, which the API never ran;
   - under API pilot-v2 at r5, uc16/18/19 still put their top on content (2 leakage);
   - at r3, the API already had 8/10 targeted contexts right or spread;
   - the local r3 → r5 result is mixed (uc19 regressed to leakage; uc04 still unknown 1.0).
4. **"Rules matter a lot" is not established.**
   - The API r3 → r5 gain is entirely in the targeted contexts (+0.50 vs. +0.01).
   - uc14 (+2.20) and uc21 (+1.61) carry about 75% of it.
   - It is confounded with the cap and a fresh draw.
   - Only local r4 → r5 (+0.54) is clean evidence.
5. **Teaching-to-the-test limitation.**
   - Clauses and v2.1 examples were chosen after inspecting failures on these contexts, so the gains are in-sample.
   - Report the targeted vs. non-targeted slice. → Done; all gains are in the targeted slice.
6. **"Gets every context right" overstates.**
   - 9 contexts have flat 0.5/0.5 references, where correct vs. incorrect depends on the realized world (uc12 vs. uc13).
   - uc21's spread ignores Alice's sincere testimony.
7. **Local log-score means rest on 1e-3 floor hits.** → A floor-1e-2 sensitivity was added; signs are unchanged. The abstention-spread explanation is labelled a hypothesis.
8. **Timing:** the Round 2 notes stage ran after `15dfcc3`, before this gate. Acceptable (pre-committed package, 0/24 invalid). The freeze was committed before the policy stage.

## Grounding audit of the API v2.1 raw outputs
- 0 invalid IDs.
- 26/60 supported hypotheses rest on rules only.
- Three rationalization patterns:
  - "could have…" rule support for every value;
  - support fitted to an assumed spread, ignoring testimony (uc21, uc23);
  - RULE6-driven reliability leans (uc12/uc13 hits are luck).

## Round 2 implications
- Proceeding is legitimate.
- Inferred ≈ reference is expected almost by construction except at s2 and s6 (not s7).
- Report per-state TV(inferred, reference) of the frozen notes. → Done: s2 0.45, s6 0.47; others ≤ 0.20.
- Any stratum C gain is about note presence and presentation; interpret it through `inferred_bare`.
