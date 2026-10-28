# Review request — 2026-10-28 (pilot model diagnostic, local and API cells complete)

Write-up: `reports/pilot/model-diagnostic.md`. Supporting files:
- `reports/pilot/unit-contexts-results.md` (generated table and per-context outputs, local and API);
- `reports/pilot/unit-contexts-audit.md` (10-context evidence audit of the local runs, readable extracts);
- `reports/pilot/unit-contexts-v1.jsonl` (the exact frozen request payloads);
- D-013.

All planned cells ran. API spend was USD 1.31 of the USD 5 cap.

## Headline (exploratory; dev-v2; 24 fixed contexts and 12 crossed instances; one draw per API episode)
- **Notes model:** gpt-6.1-sol (low effort) writes better-calibrated notes than local gpt-oss-20b, +0.40 log score on pilot-v1. Its categorical accuracy is only slightly better.
- **Policy model:** the policy is what matters.
  - Swapping in the API policy helps on 9 of 12 instances (+0.163).
  - Swapping in API notes under the local policy does not help (−0.033).
- **Do notes help?** No reliable gain from notes under either policy:
  - the local policy is worse with notes of either quality than without (−0.108 / −0.142);
  - the API policy ties direct with local notes (11 of 12 ties);
  - its +0.092 with API notes comes from one instance where the note content was wrong and the policy happened to check both rooms.

## Q1. The scoring reference conflicts with the r3 public rules (audit uc14, uc16)
The simulator creates nested beliefs only through tell/claim/assert events. Statements people overhear (`say` events) update no one, yet the r3 rules say listeners "learn what was said". The evidence posterior therefore scores some publicly reasonable nested attributions as unsupported. The API model makes the same attribution at uc14.

**Options:**
- **(a)** Clarify the public rules: "hearing a statement tells you what the speaker claimed, but people do not form beliefs about others' beliefs from casual remarks." This is a shared interface revision r4, rerun for all cells.
- **(b)** Keep the rules, and score nested units against a public-rules-consistent reference (a scoring change).
- **(c)** In a new dev version, give the simulator nested updates from `say` events (a world change; frozen sets untouched).

**Recommendation: (a).** It is the smallest change, it keeps the frozen worlds, and it makes the contract explicit. It would also add "everyone knows where they themselves are", the most common substantive miss (3/10).

## Q2. Over-abstention in pilot-v2: now attributable to the package
pilot-v2 abstains on 12/24 contexts (local, low effort), 14/24 (local, medium) and **20/24 (API)**, including contexts whose evidence posterior is 1.00. On the API model, v2 scores worse than v1 (−0.13 log score).

The stronger model abstains more, so this is a package problem (the instructions and `insufficient_evidence` status design), not a capacity limit.

**Options:**
- **(a)** One documented revision, pilot-v2.1. Abstain only when no hypothesis reaches a stated support threshold, and require that self-location and directly witnessed facts be attributed. Rerun the 24 contexts on both models (API cost about $0.15).
- **(b)** Drop the abstention status. Keep per-hypothesis support, but require a distribution over values (incl. person-level `unknown`).
- **(c)** Keep v2 as is and treat abstention as a cost the router should learn to avoid.

**Recommendation: (a).** It keeps the distinction the review asked for, between "the person does not know" and "the robot cannot tell", while fixing the trigger.

## Q3. What the crossed result means for the next pilot step
On this subset, better notes do not improve decisions under either policy. The direct agent already succeeds on 11/12 instances, so there is little room for notes to help. The subset was prespecified for the comparison, not chosen for mental-state dependence.

**Options:**
- **(a)** Replicated crossed run on instances where mental content should matter:
  - the 9 prespecified intervention states, plus dev-v2 instances where direct fails under either policy;
  - 3 draws per API episode;
  - cells API/direct, API/API, API/oracle-content (true unit content shown to the policy, an oracle-content bound, labelled as such);
  - estimated cost about USD 1.5–2.5, still within the existing USD 5 cap (USD 3.69 remains).

  This asks directly whether correct notes would change decisions, separating "notes are wrong" from "decisions do not depend on notes here".
- **(b)** Proceed to Q1/Q2 revisions and rerun the full five-arm pilot on the API policy.
- **(c)** Stay local only: revise the local policy's note-use instructions.

**Recommendation: (a) before (b).** Without an oracle-content bound we cannot tell whether the method lacks headroom on these tasks or the notes are simply not good enough. This bears on C1/C3 and the label–policy mismatch the pilot is meant to measure.

**Resource note:** (a) and the v2.1 rerun together fit the existing cap. A larger API backbone run would need a budget decision. For example, the full five-arm pilot of 400 episodes, at the measured USD 0.005 (direct) to 0.038 (all-notes API/API) per episode, would cost roughly USD 10 (illustrative).
