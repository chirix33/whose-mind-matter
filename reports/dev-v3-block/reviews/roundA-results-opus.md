# Round A results gate: scientific validity (Opus 5.5)

Reviewed: commit 4c46d8d (`src/officeminds/devgen3.py`, the `world.py`/`pilot.py`/`units.py` diffs, `tests/test_dev_v3.py`, `scripts/qualify_dev_v3.py`, `reports/dev-v3-block/qualification.{json,md}`), measured against `experiment-plan.md` Entry 1a and `POST_BLOCK_RESEARCH_DECISIONS.md`. I also read the uncommitted working-tree changes: an edit to `qualify_dev_v3.py` and the untracked `run_dev_v3_notes.py`, of which I read only the R8 payload code. No model was called.

What I ran myself (WSL venv, symbolic only):
- `pytest tests/test_dev_v3.py`: 17 passed.
- Rendered cards (`task_card(cfg, brief, rev=6)`) and ledgers for 1c, 2a, 2b, 2c, 3a–3c and 4a–4c.
- An independent `_apply` spy over every prior world of all 48 instances, at t0 and after every legal first action, checking r6 rules 1, 3 and 5 and that `enter` events never change a mind. It found **0 violations**.
- A card-consistent superset: holder swap only in stratum 2, the three patterns in stratum 3. In it the card text was byte-identical across worlds (one distinct card each), and card plus final presence did not fix the full-history best-action set in any group.
- A hand recomputation of the stratum-4 and stratum-3 values.

This gate checks LLM reasoning and arithmetic. It is not independent scientific validation.

**Verdict: PASS WITH REQUIRED CHANGES.** The generator, simulator and exact reference are sound. Every R1–R15 item is implemented, apart from one undocumented deviation (RC3a). The numbers I recomputed are right, and nothing undisclosed enters the reference. Three things are not right, and they must be fixed before the freeze:
- Agent-visible text admits readings that differ from the simulator. The differences bear on the very mechanisms being tested: who hears a quiet conversation, the direction of a conversation, and whether people in the scene know the public model.
- Two rule tests are vacuous.
- The committed qualification artifacts came from a dirty tree.

None of the fixes depends on an LLM outcome. Because the simulator itself does not change, the fixes should leave every qualification value unchanged and change only the text hashes.

## R1–R15 status
- **R1a: implemented.**
  - The superset Q-values and focal posteriors match the construction prior in all 24 stratum-2/3 instances. Exactly one pattern stays consistent after the prologue in every case.
  - **Deviation:** stratum 3 uses 3 patterns, not the planned 6 (no A↔F swap). The justification is correct but appears only in a code comment; see RC3a. The card names the organizer and the courier, so swapping them changes the card, and a superset should vary only what the card leaves open.
  - The stratum-2 superset (6 patterns) is broader than what the card allows, since the card text already distinguishes 2a, 2b and 2c. This is harmless. I checked the card-consistent version and got the same result.
- **R1b: implemented, and the interpretation is correct.**
  - Under the construction-specific prior, card-only fixes 2a, 2c, 3a and 3c only because that prior encodes the role labels. It "knows" who H is and which of 3a/3b/3c holds.
  - The rendered text never discloses either fact:
    - the courier list and every name list are alphabetical;
    - the 4b speaking order is alphabetical;
    - the stratum-3 card is identical across 3a, 3b and 3c;
    - in the card-consistent superset, card plus final presence gives {ask, move} or {ask} against the full-history {give(·)}.
  - So the prologue resolves each case, not the template. I found **no remaining text or order cue**.
  - Caveat for the report: the criterion is set equality. Under containment, 2b's move(hall) and 3b's ask(F) are already optimal from card plus presence alone.
- **R2: implemented.** All pairs are built from one superset, with shared names, labels and hidden draw. 3a vs 3c is correctly relabeled as a different physical state. 2a vs 2b is a physical availability contrast. Losses are 1.500 for the holder swap and 1.350 for 3a vs 3b, both correct.
- **R3: implemented.** Π≤1 inputs are equal for 3a/3b: the K and R contents of every person plus people present. The stratum-3 cards are identical. The optimal sets differ ({give(F)} vs {ask(F), move(hall)}).
  - K(F→R) is room_7 vs room_19.
  - K(R→F) is room_7 vs unknown, and K(A→R) is room_19 vs room_7. These are reported as realized contents, so path direction is correctly not certified.
  - The certification depends on r6 rule 5's bystander clause (see RC1b and RC3c).
- **R4: implemented.** I recomputed the values below; the "flip" column means the Bayes action differs between ×1 and ×4. The flip holds in all 12 stratum-4 instances.

  | group | ×1: drop | ×1: walk | ×4: drop | ×4: walk | flip |
  |---|---|---|---|---|---|
  | 4a (q = 0.06) | 0.860 | 0.841 | 0.770 | 0.841 | yes |
  | 4b (π = 0.9453) | 0.868 | 0.8436 | 0.786 | 0.8436 | yes |
  | 4c (r = 0.05) | 0.875 | 0.8425 | 0.800 | 0.8425 | yes |

  The other declared 4b pair, (0.03, 0.4), has π = 0.9417 and would also flip.
- **R5: implemented.**
  - The card lists the couriers and says "Nobody accepts handed-over packages" in strata 1 and 4.
  - Persistence ("nobody but the robot moves") is stated.
  - A departure renders as "leaves the lobby and the building".
  - With no chute, the card drops the `drop(...)` action from the action list.
- **R6: implemented in the simulator. The text is defective; see RC1a.**
- **R7: implemented.** `ExactOracle.belief` is the plain posterior; eps enters only `_grounded_weights`. The "given declared rules" statement is missing from the report; see RC3c.
- **R8, R9, R11 and R12:** I checked only the R8 payload code in the untracked `run_dev_v3_notes.py`. It matches the plan amendment (status from max p, plus one `unresolved` line). Round B code is not certified by this gate.
- **R13:** I found no evidence of any LLM call on dev-v3.
- **R14: implemented.** With a chute, 3a stays {give} at 0.95, 3b becomes {ask} at 0.90, and 3c becomes {drop(o_a), give} at 0.95. All three are correct.
- **R15: implemented.** The banned-label test passes. The hidden stream is keyed by construction only. The prior is the product of the disclosed distributions (with the disclosed 4b conflict filter).

## Numbers checked
- **Strata 1–3** (V*, family bests, chute values such as 0.200 and −0.050, ask values): all correct.
- **Privileged ΔJ = 0 for every stratum 1–3 focal unit (36 instances).** This is correct and expected. Every focal content is evidence-resolved, or its value spread is irrelevant to an ideal Bayes actor whose best handoff already reaches 0.95, 0.80 or 0.75.
- **Stratum 4:** privileged ΔJ is 0.068 and 0.076 at ×1 for 4b, and 0.0675 at ×1 for 4c (0.077–0.100 at ×4). 4a's privileged ΔJ is 0, because only the content, not the truth status, is revealed (see optional item O2).
- **Round B selection:** 1c, 2a, 3c, 4b. This is correct.

## REQUIRED changes (before the freeze; no LLM outcome needed)
1. **Make agent-visible text match the simulator semantics.** This affects render r6, the public-model header and the ledger. Re-run the tests and the qualification afterwards; the values should be unchanged.
   - (a) **Quiet-conversation notices.**
     - "others present" currently includes the addressed listener, for example `leo talks quietly with yara … (others present: ravi, yara)`. Rule 1 says the "others present see it but do not hear it". Exclude the listener from that list for quiet notices, or reword it.
     - "X talks quietly with Y" is symmetric. The stratum-2 card says "started by R", but the stratum-3 card says only "the listener" without defining it, and the depth-2 path F→R depends on the direction. Render the notice as "X talks quietly to Y", or have rule 1 say that the first-named person speaks and the second is addressed.
   - (b) **The public model is "shared by everyone".** This can be read as known to the characters too. Then F, who knows that "a quiet conversation always tells the listener the current meeting office", infers from watching A talk to R in 3b that R is now current. That contradicts rule 5's bystander clause and the 3b label. Similarly, in 2a, N could infer that R has moved. Reword the header, for example: "given identically to the robot in every condition; people in the scene form beliefs only by rules 1–5".
   - (c) **Lobby sightings.** Couriers and the plausible distractor see R return through the lobby and leave again. The simulator keeps their belief at the announced office. But rule 1 ("until they see … otherwise") and rule 2 ("unless they saw it") also admit "N saw R had moved". Add a clause: seeing someone in, arriving at or leaving the lobby does not change anyone's belief about which office that person is in. This changes the K(N) reference in 2a, a Round B group, and its fidelity scoring.
2. **Fix the vacuous tests.**
   - `test_rule3_statements_are_not_adopted_and_give_speaker_nothing` has three problems:
     - Statements have `present=None`, so the listener loop is empty.
     - It contains dead code (the `w0` copy and a `pass` loop).
     - The spy covers only the first prior world at t0. `clone()` bypasses the spy, so robot-ask answers are never checked.
   - `test_rule1_and_rule5_quiet_content_reaches_only_listener` is tautological: it checks `perceived` for people outside `ev.present`. It should check that lobby bystanders' `beliefs` and `nested` are unchanged, and that the listener and speaker are updated as rules 1 and 5 state.
   - Add a test for the lobby-sighting clause from RC1c.
   - My own spy found no violations, so this is a test-quality fix, not a data defect.
3. **Documentation in the qualification report and plan.**
   - (a) Record the deviation of the stratum-3 superset (3 patterns, no A↔F swap) from Entry 1a R1a, with its rationale.
   - (b) Explain the "card-only fixes" column: the construction prior encodes role labels, the text does not disclose them, and the card-consistent superset fixes nothing. State the set-equality criterion and the containment caveat (2b, 3b).
   - (c) State (R7) that the strata 1–3 labels and the 3a/3b Π≤1 certification are evidence-resolved given the declared rules: everyone is cooperative, the content of quiet conversations, rule 5's bystander clause, and the lobby-sighting clause. They are not rationally entailed without those stipulations.
4. **Clean provenance for the freeze.**
   - `qualification.{json,md}` were generated at 0b8346c from a dirty tree. The working tree now also has an uncommitted edit to `qualify_dev_v3.py` and the untracked `run_dev_v3_notes.py` and `report_dev_v3.py`, which `--freeze` hashes.
   - Commit all of it. Regenerate the qualification at a clean commit (`dirty_paths` empty). Then write `dev-v3-freeze.json`, run `run_dev_v3_notes.py verify`, and commit the freeze before any LLM call.

## Optional
- **O1. Unknown-belief notes.** `default_holds` treats an unknown belief as holding, so a reference note for a no-belief unit would say "probability that this belief is correct now is 1.00". This affects only 1b K(D), which is not in Round B. Add a guard, or render "no belief".
- **O2. Content-only privileged ΔJ.** Label the qualification's privileged ΔJ as content-only. The Round B privileged payload also carries the truth status: for 4a, revealing whether R moved would be worth about +0.081 at ×1 and +0.100 at ×4. 4a is not selected.
- **O3. Rule wording.** In rule 5, write "stated, announced or told quietly"; the simulator sets the listener's nested belief on quiet conversations. In the public model, "people's beliefs change only through answers" really concerns beliefs about beliefs.
- **O4. Freeze the computed notes earlier.** Put the reference and privileged payload hashes in `dev-v3-freeze.json`. They are symbolic, so they can be frozen before the inferred-note LLM stage.
- **O5. Expected identical conditions.** Predeclare that reference and privileged will be byte-identical for 1c, 3c and K(N) in 2a, so that this is not read post hoc.

## Short reasoning
The simulator, the exact reference and the pairing are correct over the full support. Every reference input is either disclosed in the card or recoverable from the visible prologue, and that is shown non-vacuously by the superset checks.

The remaining risks are in the text. Under D-014 §4, the reference may use only the semantics the shared public text determines. Where the text admits a second reasonable reading — quiet-conversation listeners, conversation direction, characters knowing the model, lobby sightings — the reference silently picks the simulator's reading. These are cheap text fixes, and they must happen before the hashes are frozen.
