# Stage 2 results gate: scientific-validity review (Opus 5.5)

**Verdict: PASS WITH REQUIRED CHANGES.** Stage 2 was executed as frozen. The pre-declared reading (§5(3), "reconsider method/environment fit") follows correctly from RC3/RC4. The required changes all concern how the handoff describes what was measured and what the result does and does not show. No new model runs are needed.

Reviewer: Opus 5.5 (scientific validity). This was a read-only review with no model calls. Run `repair-stage2-20261029-132459-743ace` was inspected directly (WSL `episodes.jsonl`, 4032 records). Scratch scripts s1–s6 are in the session scratchpad.

## 1. Execution against the freeze

| Check | Finding |
|---|---|
| Freeze before outputs | `stage1-freeze.json` was created 13:14:19 −0500 at a1263c7 and committed in 27c324e. Its sha256 `e0fc8b94…dad2` matches the manifest's `freeze_sha256`. |
| Notes before policy | Notes ran 13:15:15–13:24:35 −0500 (proof aa75046, 856/864 valid). The policy started 18:24:59 UTC (13:24:59 −0500) from a clean tree at aa75046. `run_repair.py` asserts the notes `states` hash and the per-state rendered-prompt hash before dispatch. (The proof hash is over the canonical `states` object, not the file bytes, so a file-level sha differs by design.) |
| Frozen payloads | Every (state, condition) has exactly 1 distinct note payload across both draws (1440/1440). |
| Decoding / draws | The manifest records temperature 1.0, max_tokens 1024, reasoning low and draws 2, matching Entry 2. Notes used temperature 1.0, max_tokens 2048, reasoning low, as frozen. |
| Complete blocks | All 24 seed blocks (20261100–23) are complete. Every (seed, construction, condition) cell has 4 episodes (1008 cells). 0 blocked, 0 policy fallbacks. 12 inferred-condition episodes carry no note: 6 single-unit states with an invalid note × 2 draws, the declared fallback. |
| Primary numbers | Independently recomputed, ref − none = −0.0240 and inf − none = −0.0429 over 288 base scenarios (equal-n per construction, so the equal-weight estimand is the simple mean). |
| RC3 Holm | p = 0.151 (tested at 0.025) and 0.387 (tested at 0.05). Neither is significant. |
| RC4 reference | CI upper +0.0283 < δ = 0.05 gives **no practical value**. This is correct. |
| RC4 inferred | inf − none CI upper +0.0127 < δ gives **fails**. This is correct. |
| Table cell | (no practical value, fails) maps to §5(3). This is correct. |

No deviation from the frozen protocol was found.

Note on power. `power.md` predicted that the most likely outcome under a true null was "unresolved" (P ≈ 0.72 under variance B). "No practical value" was reached because the point estimate was negative (−0.024), not because the design had resolution to spare. The handoff should say so.

## 2. Mechanism: why correct reference notes do not prevent errors

Error and timeout counts per condition are in `stage2-results.md`. The first actions and action sequences below are descriptive counts over 96 episodes per cell, computed from `actions`.

| Construction | Condition | First action give(F) | ask → give at step 2 | Errors |
|---|---|---|---|---|
| 3a (give(F) correct) | none | 28 | 29/56 | 0 |
| 3a | reference (K(F→R) = 0.5/0.5, "low") | **12** | 43/77 | 0 |
| 3b (give(F) is the error) | none | 10 | 24/84 | 37 |
| 3b | reference (K(F→R) = announced office, 1.00, "high") | **28** | 23/52 | 58 |
| 3b | reference_KR | 12 | 42/79 | 58 |

**3b.** The correct K(F→R) note says, with "high" confidence, that F thinks R believes the *announced* office. The public model states that the meeting was changed away from that office. It also says explicitly that F "forwards them to the office where F thinks R will go, that is, to what F thinks R believes about meeting_room" (`devgen3.py` l.244). So the card is not ambiguous, and the note directly implies that give(F) is wrong. The policy instead gives to F far more often when that note is present (28 vs 10 first-action gives). In 3a it gives less often when the reference note is low-confidence (12 vs 28).

The policy appears to read the confidence line as "F is a good courier" rather than combining the note's value with the forwarding rule. Example trace: `s20261100-dev-v3-3b-stakes4-perm0`, reference. The robot asks sara and is told desk_9, then calls give(sara) with the reasoning "Sara says meeting_room=desk_9 … forward to desk_9", ignoring both the forwarding rule and the note. The result is an error (−2.05).

**2b.** The reference note is K(N) = o_a (correct, high confidence). The policy treats N's belief as the truth. Trace `s20261101-…-2b-stakes4-perm0`: "she believes that value. So Bob likely at suite_3", followed by drop(suite_3), an error. The unit's correct content does not encode that the belief is stale. That inference has to come from the history (R moved and told only H, who then left), and the policy does not make it. Errors: none 56, reference 55.

**1b.** The note is K(x) = unknown. The errors are mostly ask → drop gambles (none 33, reference 24) at a wrong-drop cost of −2.05 under ×4 stakes. The missing behaviour is search under uncertainty, which is the known risk-calibration weakness from the autonomous block. A Knowledge note cannot supply it.

**2c.** After asking the stale holder, the policy gives to that holder (reference ask → give 24). The reference K(N) note is deliberately spread (posterior 0.25/0.5/0.25, "low"). Bayes-optimal play still gives to N, but the policy does not see that N's own belief is what governs forwarding.

**Artifact concerns (contributors, not bugs; all frozen and declared, so the run is not invalidated):**

1. **Stale label on the person's own answer.** Once the robot asks the note's subject, the graph marks the t0 note `stale` and renders "new evidence about this person has appeared since the note was written". This happened in 62/96 3b-reference episodes. In 3b, F's answer about her own belief does not change K(F→R), yet the label invites the policy to override a still-correct note with the fresh answer, which is exactly the 3b error. So the reference condition is "correct-at-t0 content that is later flagged stale after an ask", not simply "correct content".
2. **Content-only rendering.** By design, r7 shows the distribution plus a confidence line, with no decision implication and no correctness line. "High confidence" on a stale or second-order belief is semantically correct but evidently misread. The result therefore measures *this policy's integration of content-only notes*, not the decision value of the mental-state content itself.
3. **Round B is not a comparison.** Round B used constructions 1c, 2a, 3c and 4b, none of the four failure constructions. There is no evidence that the older format with a correctness line would have repaired 1b/2b/2c/3b. The handoff must not attribute the null result to the r7 format change; that would be untested speculation.

Taken together, "no practical value" is a valid finding for the measured object: fixed t0 allocation, no refresh, stale labelling, r7 content-only rendering, gpt-oss-20b at low reasoning and temperature 1.0. It is not evidence that ToM content has no decision value in OfficeMinds. The Bayes headroom is about 0.50, and the qualification's exact bounded actor gains from these units. The gap between the symbolic actor and the LLM is the finding.

## 3. Depth descriptives and fidelity: limits on interpretation

- **Reference DiD.** (ref − none)[3b] − [3a] = −0.417 [−0.736, −0.093], n = 24. The correct depth-2 note *harms* the construction that certifies depth 2. This is descriptive and argues against C4-style support, not for it. Do not report it as depth evidence.
- **Label-only controls.** The 3a/3c renderings differ only in labels (`differ_beyond_labels` = 0/96). Their contrasts, −0.03 and −0.07 (3c reference CI upper +0.0005), show that a unit label alone can shift return by roughly 0.07 at this n. Any depth contrast of that size is within label and noise effects.
- **Inferred 3a +0.34.** This is driven by inferred_KR behaviour: 28/96 timeouts and frequent move(hall) first actions. It reflects a note-content effect, not depth.
- **Inferred DiD −0.38.** This mirrors the reference DiD and has the same caveat.
- **Fidelity.** It is low where the posterior is spread or nested.
  - 3a: 55/95 unsupported_committed. The note commits to one office when the posterior is 0.5/0.5.
  - 3b: 41/95.
  - 2c: TV 0.47, with 18 incorrect_supported.
  - 4b: 14/96 discriminating prior copies (35 raw). The v2.2 prior-vs-posterior instruction reduced but did not remove prior copying.
  - Strata-1 constructions are trivially correct (TV 0).
  - Because the *reference* also has no practical value, the inferred "fails" class cannot be attributed to inference fidelity alone. Both bottlenecks exist, and the policy-integration bottleneck dominates.

## 4. Recommendation and handoff content

**Justified under §5(3).** Stop the block. Run no allocation or controller training and no further package iteration on these outputs. Hand off to research review with the recommendation to reconsider method/environment fit. Specifically, put the policy-integration gap (correct notes are not used and can mislead) at the centre of that discussion, ahead of inference fidelity.

**Required changes to the eventual summary or handoff:**

1. Report the classification with the exact CI upper bounds against δ and the Holm p-values. State that "no practical value" holds for the equal-weight 12-construction estimand only. The per-stratum CIs still include +0.05 (stratum 1 reference upper +0.107, stratum 2 +0.087). Note that the outcome arose from a negative point estimate rather than from planned resolution.
2. Define the measured object precisely: t0 fixed notes, no refresh, stale relabelling after asks, r7 content-only rendering, single backbone at reasoning low and temperature 1.0, development seeds.
3. Include the §2 action-pattern table (labelled descriptive), with the 3b and 2b traces cited by state ID.
4. State explicitly that Round B did not cover 1b, 2b, 2c or 3b.
5. Present the depth results as descriptive only: the reference DiD is negative, the label-only control magnitude is about 0.07, and the inferred 3a value is a timeout artifact. Make no C4 statement.
6. Report the fidelity limits, including the 4b discriminating prior copies (14/96) and the 12 inferred episodes without a note under the declared fallback.
7. Report compute separately. The reference oracle (1.53 s CPU) is not deployable. Inferred notes cost 883 attempts and about 2.9M tokens.
8. Mark seeds 20261100–20261123 as inspected development data that must never be reused as held-out.

**The handoff must NOT claim:**
- that mental-state notes or ToM have no decision value in OfficeMinds, or that C1 or C2 is refuted;
- that reference notes significantly harm overall (the CI includes 0). Only the 3b-specific DiD is a descriptive harm signal;
- any depth (C4) evidence;
- that the inferred failure is caused by note fidelity;
- that the r7 renderer or the stale label *caused* the null. These are hypotheses, untested;
- confirmatory status, or anything about Tier 2 or Menti-Bench.

**Recommended diagnostic for the research review** (a proposal, not authorised here):
- *Zero-cost, now:* tabulate from existing traces how often the step reasoning references the note value, and the action given a stale vs fresh note.
- *Candidate next design, needing review because it changes the method:* a small 2×2 on fresh seeds restricted to 3b and 2b:
  - factor 1: content-only rendering vs content plus decision implication (for example, "if handed to F, F forwards to desk_14");
  - factor 2: stale-on-own-answer relabelling on vs off.

  This would test whether the null result is about policy integration or about the value of the content. Compare each cell against the exact bounded actor's value, so that the gap between the symbolic actor and the LLM is quantified per construction.
