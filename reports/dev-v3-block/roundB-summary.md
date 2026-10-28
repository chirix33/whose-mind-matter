# Round B summary: fresh-context value-of-notes check on dev-v3 (local backbone; development data)

**Gated.**
- Opus: `reviews/roundB-results-opus.md`, PASS WITH REQUIRED CHANGES 1–10, all applied here.
- Sonnet: `reviews/roundB-results-sonnet.md`. It reproduced every pre-declared number exactly and found three write-up discrepancies (counts, a float-boundary artifact, token averages), all fixed.

## What ran
- **Run:** `dev-v3-notes-20261028-165208-67f601`. Notes were frozen at commit `d5af211`, before any policy call. The dev-v3 freeze is at `984cb50`, generated at clean `7871e4c`. `verify` passed before every stage.
- **States and backbone:** 16 t0 states, the four variants of hash-selected groups 1c, 2a, 3c and 4b. Backbone: local gpt-oss-20b for both notes (temperature 0, max_tokens 1024, frozen) and policy (temperature 1.0, unseeded).
- **Scale:** 4 conditions × 3 draws = **192 episodes, 0 blocked**.
  - Policy attempts: 3 truncated, all recovered on retry, 0 fallbacks.
  - Pre-declared tables: `roundB-results-local.md`. Post-hoc descriptives: `roundB-descriptive-local.md`. Episode CSV and traces: `evidence/`.
- **No paid calls.** The ledger is unchanged at USD 3.8690.
- **Deviation (B2 API batch not run).** This was decided after the local outcomes, on cost grounds, under the ruling's clause "if the API check cannot fit, finish the free/local diagnostic and report the missing API confirmation".
  - The pre-declared gate (≥ USD 1.00 remaining) held: USD 1.1311 remained.
  - The expected cost exceeded the USD 0.80 stage allowance. Measured local usage was ≈ 1,547 prompt tokens per decision call and ≈ 2.86 decision calls per episode, all conditions. At gpt-6.1-sol's $2/$10 per Mtok, assuming 300–800 output tokens per call including reasoning, 64 episodes plus 24 note calls cost about USD 1.3–2.7 (Sonnet's range; my central estimate was about 1.9).
  - The worst-case reservation per policy call (max 2,000 output tokens) is about USD 0.023; for a note call (6,000) about 0.066.
  - No substitute API variant was run. **The API confirmation is missing.**

## Notes: coverage and content (before any policy outcome)
- **Coverage.** 19 of 24 focal units have a valid inferred note; computed notes cover 24/24.
- **Failures.** All 5 failures are 4b reliability notes. Every failed attempt cites an **invented `PUBLIC_MODEL` evidence ID**, which the frozen pilot-v2.1 validator rejects (`cites_non_visible_evidence`, `rule_citation_mismatch`). Valid 4b notes that cite `RULE6` for the same disclosed rates passed. So the gap is that r6's public-model block **has no citable ID and the model invents one**, not that its content cannot be cited.
  - At temperature 0, attempts 2 and 3 were byte-identical in every failing unit, so the retries could not help.
  - This dev-v3 ↔ pilot-v2.1 interface gap was not caught before the freeze. Per R11, failed cells show no note.
- **Content.** The 1c, 2a and 3c notes are all correct_supported or supported_spread against the aligned public-model posterior. The three valid 4b notes:
  - R(kim) at ×1 perm0 is correct_supported, but it copies the prior (0.98/0.02);
  - R(uma) at ×1 perm1 is correct_supported;
  - R(zane) at ×1 perm1 is unsupported_committed (cooperative 0.70 vs a posterior of 0.045).
- **4b content finding** (from the gate's inspection of all 8 final 4b outputs, valid or not):
  - 6 of 8 copy the disclosed prior instead of updating on the conflicting reports;
  - every reliability note for the high-rate reporter says cooperative 0.70, where the reference says 0.045;
  - the one inferred-arm error with a note shown (4b ×1 perm1, replicate 2, −0.70) followed that 0.70 note, according to the policy's reasoning.

  So inferred notes have **two** problems in 4b: an interface gap (no citable ID), and content that does not integrate the evidence.
- **Content-free inferred cells.** In 4b ×4 perm0 and perm1 every note failed, so the inferred prompt reads "(none instantiated)". It is effectively a second no-note arm. Its difference from `none` (0.00 and −0.98) shows that one draw can move a cell mean by about 1.0 in error-prone ×4 states.

## Pre-declared reading (Entry 1a R10; reproduced by Sonnet)

| condition | stratum 1 (control) | 2 | 3 | 4 | reading |
|---|---|---|---|---|---|
| inferred | inconclusive | inconclusive | positive | inconclusive | **inconclusive** |
| reference | null | inconclusive | positive | positive | **headroom present** |
| privileged | null | inconclusive | positive | positive | headroom present (never counted as deployable) |

The analysis script's classifier was given an exact-decimal tolerance after the run, because 0.04999999999999999 had read as below +0.05. No pre-declared class or reading changed.

**Pre-registered measures:**
- **Headroom.** Bayes V* minus none, per stratum: 0.06 / 0.32 / 0.24 / 0.41.
- **Privileged mechanism (R8):**
  - 2a: target leakage; the true K(H) content is R's office;
  - 4b: true intent identifies which report is true, which is effectively target leakage;
  - 1c and 3c: byte-identical to reference, so no privileged-specific benefit.

## Why the reference reading is fragile (post-hoc, descriptive)
- **Leave-out.** Without the 3 tail `none` episodes (2 errors and 1 timeout of 48) the reference reading becomes **inconclusive**, and stratum 3's "positive" depends on the one timeout alone.
  - The median-of-3 sensitivity tells the same story but discards tails by construction: reference and privileged read "no measurable headroom" and inferred reads "inconclusive".
- **4b (one group, one hidden draw).** Episodes without a correct reliability posterior had 5 errors in 24 (none 2/12; inferred 3/12, where notes were mostly missing or prior copies). Episodes with one had 0/24 (reference, privileged).
  - This is the clearest pattern in the round, and it is a single-group observation.
- **Counterexample (2a).** One reference episode erred (−0.60); `none` also had one error (−2.05).
- **Noise floor.** In the 8 states where reference and privileged prompts are byte-identical (1c, 3c), their per-state mean difference averages |0.023| (max 0.05). That floor does not cover error-prone ×4 states (see the content-free inferred cells above).
- **Policy behavior.** The first action is an ask in 32–37 of 48 episodes per condition. It is in the exact Bayes-optimal set in only 6/48 (none), 9/48 (inferred), 6/48 (reference) and 3/48 (privileged), because the Bayes actor gives or drops at once. Success is 44–48/48 in every condition.
- **3c (descriptive).**
  - Under `none`, 3 of 12 episodes visited F's own (new) meeting office, where R is not because R was never told: returns 0.65, 0.65, and −0.40 (timeout). The note arms visited it in 0/12 each.
  - give(F) rose from 2/12 to 5/12.
  - This is consistent with the note correcting a perspective confusion. But the usable content equals R's own belief, which a depth-1 K(R) note would also supply. There is no K(R) control, and 3c is not the certification pair, so this is **not** evidence specific to depth 2.

## Conclusion
- **Pre-declared reading.** On dev-v3 with the local backbone, the rule reads "headroom present" for **reference** notes and "inconclusive" for **inferred** notes.
- **The reference reading is weak and fragile.** It rests on 3 rare catastrophic `none` episodes and becomes inconclusive without them. The clearest pattern is single-group: in 4b, a correct reliability posterior was followed by 0 errors in 24 episodes, against 5 in 24 without one.
- **Inferred notes**, the deployable candidate, show no reliable value. They have two measured problems: the public-model block is uncitable in practice (5/24 notes failed), and 4b content copies the prior instead of integrating the evidence.
- **Scope.** Development data only; local backbone only; the API confirmation is missing.

## Recommendation
- **Not allocation learning.**
- **First, inference/integration work.** Give the public model citable IDs, and make reliability notes integrate conflicting testimony with disclosed rates. Test this on fresh dev-v3 seeds, not on these outcomes.
- **Send a re-measurement design to research review.** The remaining headroom is mostly a tail of rare costly errors and a few extra steps, so it needs a design powered for error rates: more draws on error-prone ×4 states and paired designs. Whether that headroom is worth pursuing within the original goal is a research decision.
