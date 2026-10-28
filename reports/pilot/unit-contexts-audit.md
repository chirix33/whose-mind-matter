# Evidence audit of fixed-context unit outputs (local gpt-oss-20b, low effort, pilot-v1 vs pilot-v2, renderer r3)

**Auditor:** Claude, the implementation agent. Not a human annotation; no inter-rater agreement.

**Sample:** 10 of 24 contexts (uc02, uc07, uc10, uc12, uc13, uc14, uc15, uc16, uc21, uc24). The sample was chosen **after** viewing the per-context results table, to cover unknown truths, nested units, reliability units, abstentions, and disagreements between categories and evidence. It is therefore **not** a random or blind sample.

**Source:** run `unit-contexts-20261028-064729-654f39`; raw outputs in that run's `records.jsonl`. Every judgment below reads the visible history and the unit's actual output, support entries and notes, then compares them against both the public rules and the simulator truth.

| ctx | unit | visible evidence (summary) | sim. truth / evidence posterior | pilot-v1 | pilot-v2 | audit judgment |
|---|---|---|---|---|---|---|
| uc02 | K(judy), recipient | Uma (stated incentive) says `judy_loc = office_b` | office_b / office_b 0.95 | `unknown` 0.90 | ABST, mass split evenly incl. `unknown` | The recipient knows where she is (common sense; the posterior agrees). v1 asserts person-level ignorance without support. v2 avoids that false claim but misses an inferable fact |
| uc07 | K(heidi) | Heidi says desk_3; Wen says desk_9 | desk_3 / desk_3 0.87 | desk_3/desk_9 0.5/0.5, cites Heidi | attributed; desk_3, desk_9, unknown at 0.33 each, **all citing Heidi's statement** | v1 reasonable. v2's support for desk_9 and `unknown` is speculative ("could be lying", "might not hold a belief"): structurally valid but evidentially empty |
| uc10 | R(uma→vik) | Vik states an incentive; Uma later answers the robot | cooperative / cooperative 0.91 | obstructive 0.60 | ABST (uniform) | No visible evidence about Uma's assessment of Vik. v1 projects the ROBOT's own suspicion of Vik onto Uma (a perspective error); the leakage rule misses it because it only checks robot-known values. v2's abstention is appropriate |
| uc12 | R(nadia) | Nadia: "I'd rather keep that package myself." | cooperative / 0.5–0.5 | obstructive 0.70 | obstructive 0.90 (support: the incentive statement) | Direction supported (an incentive is evidence); confidence too high relative to the declared ambiguity. v2 is more overconfident than v1 |
| uc13 | R(grace) | same incentive statement | obstructive / 0.5–0.5 | obstructive 0.80 | obstructive 0.80 | Same pattern; correct here by the hidden draw |
| uc14 | K(wen→leo) | Wen: "I saw Leo head to the office earlier." | unknown / unknown 1.00 | room_7/room_12 0.40/0.40, unknown 0.20 | ABST (uniform) | **Scoring-reference artifact.** The simulator never gives Wen a model of Leo's belief, so the truth is `unknown`. Publicly, though, Wen watched Leo go to his office, so "Wen thinks Leo knows his office" is a natural inference. v1 is scored unsupported for a publicly reasonable answer |
| uc15 | K(vik→ivan) | Ivan: "Vik told me this morning where the meeting is." | office_b / 0.5–0.5 | office_a/office_b 0.5/0.5 | `unknown` 1.00, support says "Vik told him the location" | v1 good. v2 contradicts its own support: telling Ivan implies Vik believes Ivan knows the room. A real failure of v2 |
| uc16 | K(alice→wen) | Alice heard Wen say "Heidi said they are keeping the same office today." | unknown / unknown 1.00 | `unknown` 1.00 | office_a/office_b 0.5/0.5 (support: Wen's statement, heard by Alice) | **Scoring-reference artifact.** Under the r3 public rules Alice learned what Wen claimed, so she has some model of Wen's belief; the simulator's `say` event updates no one. v2's reasoning is publicly defensible but scored unsupported; v1's "unknown" is scored correct only because of the bookkeeping |
| uc21 | K(frank), recipient | Alice: `frank_loc = room_7` | room_7 / room_7 1.00 | spread 0.33 each incl. `unknown` | ABST, spread incl. `unknown` | Both miss that the recipient knows where he is. v2 also puts a third of the mass on `unknown` while abstaining, against its instruction |
| uc24 | K(vik), recipient | nothing about Vik | office_a / 0.5–0.5 | spread incl. `unknown` 0.33 | ABST, spread incl. `unknown` 0.33 | Abstention is right (the robot cannot tell which office), but the mass on `unknown` conflates robot ignorance with Vik's |

## What the audit changes in the interpretation
1. **Part of the measured "unsupported" error is a scoring-reference problem, not a model problem** (uc14, uc16).
   - The evidence posterior uses the simulator's belief bookkeeping. Nested beliefs come only from `tell`/`claim`/`assert` events, and `say` statements update no one. The public r3 rules invite inferences the bookkeeping never makes.
   - Per review item C this needs a decision, not a silent fix: either the public rules state that overheard statements do not create beliefs about the speaker's beliefs, or the scoring reference must allow for it.
   - The frozen worlds were not changed.
2. **Self-knowledge of the recipient is the most common substantive miss** (3/10), in both packages.
3. **pilot-v2's per-hypothesis support is gameable.** In 2/10 the cited utterance does not support the attribution, or contradicts it. This confirms that structural validation is not entailment.
4. **pilot-v2 abstains in situations where pilot-v1 asserted ignorance** (uc02, uc10, uc21, uc24). That is the intended correction, but v2 still spreads mass onto `unknown` inside abstentions.
5. **Reliability units over-read a stated incentive** (both packages).
