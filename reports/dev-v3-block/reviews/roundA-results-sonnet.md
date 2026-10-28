# Round A results gate: independent numerical recomputation (Sonnet 5.5)

Verdict: **CONSISTENT.** Every number checked reproduces. There are no numerical discrepancies. Four presentation or provenance notes are listed at the end; none changes a reported value.

Scope: `reports/dev-v3-block/qualification.md` and `qualification.json` (generator `src/officeminds/devgen3.py`, design in `experiment-plan.md` Entries 1 and 1a). No LLM or model server was called. No repo file was modified except this report.

## Method

1. **Closed-form derivation by hand.** I rendered each of the 12 stakes-×1 unpermuted groups with `devgen3.generate()` and read what the robot sees: task card (rev 6), public model, and t0 ledger. I derived the posterior and Bayes-optimal values from the disclosed model and the reward arithmetic:
   - success at step k = 1 − 0.05k;
   - error = −0.05k − 0.5×stakes.
2. **Independent expectimax** (scratchpad `solver.py`). It does not import `vomi.oracle`.
   - The posterior is the set of prior worlds whose `reset()` observation equals the true t0 observation.
   - Transitions and legal actions come only from `world.py` (`World.clone`, `step`, `legal_actions`).
   - Observations are partitioned exactly (asks, search, give, drop, wait and deliver are all legal).
   - I ran it on all 48 instances and compared every first-action Q-value to `q_first_actions` (not just 6).
3. **Further recomputations with the same solver:**
   - superset pairs and the with-chute counterfactuals;
   - card-only and superset card-only best actions;
   - ex-ante privileged VOI of each focal unit;
   - the ×4 stratum-4 variants.
4. **Round B selection** recomputed from the SHA-256 formula.

## 1. Per-group recomputation (stakes ×1, unpermuted)

Where "hand" is given, the value was derived by hand before running the solver, and the solver agrees. A dash means the family is not available in that group.

| group | what the robot sees, and the hand derivation | V*, hand = solver | reported V* | optimal first action | best ask / search / chute / handoff (recomputed) | reported family values |
|---|---|---|---|---|---|---|
| 1a | R announced desk_3 and left, so R is at desk_3 with certainty. drop = 1−0.05 | 0.950 | 0.950 | drop(desk_3) | 0.90 / 0.85 / 0.95 / – | 0.900 / 0.850 / 0.950 / – |
| 1b | Unannounced, uniform over 3 offices. drop = (0.95−2×0.55)/3 = −0.05. Search = mean(0.85, 0.75, 0.65) = 0.75. Asking is useless. | 0.750 | 0.750 | move(hall) | 0.70 / 0.75 / −0.05 / – | 0.700 / 0.750 / −0.050 / – |
| 1c | Announcement corroborated, so a single world | 0.950 | 0.950 | drop(suite_1) | 0.90 / 0.85 / 0.95 / – | same |
| 2a | Announced office_b, then a quiet talk with yara. R is at one of the other two offices (0.5 each). Yara holds the current location, so give(yara) = 0.95. Ravi holds the stale office_b, so give(ravi) = −0.55. drop(x) = 0.5×0.95 − 0.5×0.55 = 0.20. Ask then give = 0.90. | 0.950 | 0.950 | give(yara) | 0.90 / 0.85 / 0.20 / 0.95 | 0.900 / 0.850 / 0.200 / 0.950 |
| 2b | Yara (the informed courier) left the building. Only stale bob remains, so give(bob) = −0.55. Search: 0.5×0.85 + 0.5×0.75 = 0.80. | 0.800 | 0.800 | move(hall) | 0.75 / 0.80 / 0.20 / −0.55 | 0.750 / 0.800 / 0.200 / −0.550 |
| 2c | Two quiet updates; R's final location is dave's belief (m2). 4 worlds, 0.25 each. K(ivan)=m1 is never correct. K(dave): desk_3 0.5, desk_9 0.25, desk_14 0.25, always correct. | 0.950 | 0.950 | give(dave) | 0.90 / 0.85 / 0.20 / 0.95 | same, and the same K posteriors |
| 3a | Relay A→F→R. F→R is current (b), 2 worlds. give(heidi) = 0.95. No chute. | 0.950 | 0.950 | give(heidi) | 0.90 / 0.85 / – / 0.95 | same |
| 3b | F's belief is current but F→R is stale (a), so give(F) = −0.55. ask(F) then walk (ask, hall, office, deliver = 4 steps) = 1 − 0.20 = 0.80. Search = 0.80. | 0.800 | 0.800 | ask(tomas,meeting_room), move(hall) | 0.80 / 0.80 / – / −0.55 | 0.800 / 0.800 / – / −0.550 |
| 3c | Only F told. R still believes a and is at a. F→R = a = R's true location. | 0.950 | 0.950 | give(nadia) | 0.90 / 0.85 / – / 0.95 | same |
| 4a | q=0.06. P(correct)=0.94. drop = 0.94×0.95 − 0.06×0.55 = 0.860. Walk = 0.94×0.85 + 0.06×0.70 = 0.841. Ask = V−0.05. | 0.860 | 0.860 | drop(suite_1) | 0.810 / 0.841 / 0.860 / – | same |
| 4b | (r_X, r_Y) = (0.02, 0.3). See the posterior below. drop = −0.55 + 1.5π = 0.868006. Walk = 0.843569. Ask = 0.818006. | 0.868006 | 0.868 | drop(desk_14) | 0.818 / 0.844 / 0.868 / – | 0.818 / 0.844 / 0.868 / – |
| 4c | r=0.05. P(correct)=0.95. drop = 0.9025 − 0.0275 = 0.875. Walk = 0.8425. Ask = 0.825. | 0.875 | 0.875 | drop(lab_north) | 0.825 / 0.8425 / 0.875 / – | 0.825 / 0.843 / 0.875 / – |

The solver reproduced the full first-action Q-tables of all 48 instances (including permuted variants and stakes ×4). The maximum |Q_mine − Q_reported| is 4.8e-11. That difference comes from the 10-digit rounding in the JSON, which affects only group 4b. Optimal sets match in all 48. Group-level V* and the permuted-variant isomorphism (same V*, role-renamed action) also match.

Worlds consistent with the t0 history, from the solver and from the table's "worlds" column:

| group | 1a | 1b | 1c | 2a | 2b | 2c | 3a | 3b | 3c | 4a | 4b | 4c |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| worlds | 1 | 3 | 1 | 2 | 2 | 4 | 2 | 2 | 2 | 4 | 5 | 4 |

All match.

### Stratum 4: posteriors and the stakes ×4 variants

**4b posterior, by hand.** The statements are kim = desk_14 and uma = desk_9. Three explanations are consistent with them:

- Kim cooperative and uma lying: (1−0.02)×0.3×½×⅓ = 0.049.
- Kim lying and uma cooperative: 0.02×0.7×½×⅓ = 0.0023333.
- Both lying (a = the third office): 0.02×0.3×¼×⅓ = 0.0005.

| quantity | hand = solver | reported |
|---|---|---|
| π = P(R at desk_14) | 0.9453376206 | 0.9453376206 |
| P(R at uma's office) | 0.0450160772 | uma cooperative 0.0450160772 |
| P(R at the third office) | 0.0096463023 | not reported |
| R(kim) cooperative | 0.9453376206 | 0.9453376206 |
| R(uma) obstructive | 0.9549839228 | 0.9549839228 |
| second parameter set (0.03, 0.4) | π = 0.941748 | plan says 0.942 |

The plan thresholds π* ≈ 0.926 (×1) and 0.965 (×4) are consistent with a hand solution. With the mix of the other two offices fixed, I get 0.928 and 0.965.

**Stakes ×4 (error = 2.0), hand and solver agree.**

| group | ×1 optimal (V*) | ×4: drop | ×4: walk | ×4 optimal (V*) | flip |
|---|---|---|---|---|---|
| 4a | drop(suite_1) 0.860 | 0.770 | 0.841 | move(hall) 0.841 | yes |
| 4b | drop(desk_14) 0.868006 | 0.786013 | 0.843569 | move(hall) 0.843569 | yes |
| 4c | drop(lab_north) 0.875 | 0.800 | 0.8425 | move(hall) 0.8425 | yes |

The 4a threshold is q* = 0.1/1.35 = 0.0741 at ×1 and 0.1/2.85 = 0.0351 at ×4, as the plan states. The flip also holds in all permuted variants.

### Privileged ΔJ column

I recomputed it as the ex-ante value of revealing the unit's true content. This is the posterior-expected gain, J({u}) − J(∅), with Bayes actor and asks legal. It is not the gain in the single realized world.

| unit | recomputed | reported |
|---|---|---|
| R(kim), 4b | +0.075563 | +0.076 |
| R(uma), 4b | +0.067524 | +0.068 |
| R(judy), 4c | +0.067500 | +0.068 |
| every other focal unit (12 units) | +0.000000 | +0.000 |

## 2. Independent solver on the requested instances

The solver was compared on all 48 instances, including 2c (4 worlds), 3b and 4b.

| instance | solver V*, optimal set | max |ΔQ| vs json |
|---|---|---|
| 2c, stakes 1 | 0.95, give(dave) | 1.1e-16 |
| 3b, stakes 1 | 0.80, {ask(tomas,meeting_room), move(hall)} | 2.2e-16 |
| 4b, stakes 1 | 0.868006, drop(desk_14) | 4.4e-11 (rounding) |
| 4b, stakes 4 | 0.843569, move(hall) | 4.8e-11 (rounding) |

## 3. Pairs and with-chute counterfactuals

The superset (stratum-level) pair scenarios were rebuilt from `devgen3.superset_scenario`. They were solved with my own solver on the same truth (pattern + hidden draw).

| pair | recomputed optimal sets and values | reported | match |
|---|---|---|---|
| 2a holder swap (2a:0 vs 2a:1) | give(yara) 0.95 vs give(ravi) 0.95; loss of using yara's action = 0.95 − (−0.55) = 1.50; same physical state: yes (after `reset()`, identical rooms) | same, gap 1.5 | yes |
| 2a vs 2b (H departed) | give(yara) 0.95 vs move(hall) 0.80; physical state differs (yara outside) | same, gap "nan" | yes (see note 2) |
| 3a vs 3b | give(heidi) 0.95 vs {ask(heidi,meeting_room), move(hall)} 0.80; loss 1.35; same physical state: yes; Π≤1 inputs equal | same | yes |
| 3a vs 3c | give(heidi) 0.95 vs give(heidi) 0.95; loss 0.00; uma at room_7 vs room_19, so not the same physical state | same | yes |

The full Q-tables of all 8 pair patterns agree with the report (max difference 2.2e-16).

The depth-2 contents listed in the md were checked against the event semantics. In 3a vs 3b, K(heidi→uma) is room_7 vs room_19, and K(heidi) and K(uma) are equal.

| construction | as built | with a chute (reported) | with a chute (recomputed) | match |
|---|---|---|---|---|
| 3a | give(heidi) 0.95 | give(heidi) 0.95 | give(heidi) 0.95 | yes |
| 3b | {ask(tomas), move(hall)} 0.80 | ask(tomas,meeting_room) 0.90 | ask(tomas,meeting_room) 0.90 | yes |
| 3c | give(nadia) 0.95 | {drop(office_b), give(nadia)} 0.95 | {drop(office_b), give(nadia)} 0.95 | yes |

The ask-then-drop path (2 steps) explains 3b's 0.90. In 3c a chute makes the drop tie with the handoff, so K(F→R) has no task-level relevance there. This matches R14.

Card-only checks (notices stripped), recomputed with my solver:

- Construction prior fixes the best action in 1b, 2a, 2c, 3a, 3c. It does not in 1a, 1c, 2b, 3b, 4a, 4b, 4c. This matches the "card_only_fixes_best_action" list.
- Superset prior: never fixes the best action (the `superset_card_only_fixes_best_action` list is empty). The superset prior and the construction prior give identical first-action Q-values (max difference 0).

## 4. Round B selection

| stratum | `int(sha256(...),16) mod 3` | construction | reported |
|---|---|---|---|
| 1 | 2 | 1c | 1c |
| 2 | 0 | 2a | 2a |
| 3 | 2 | 3c | 3c |
| 4 | 1 | 4b | 4b |

## Discrepancies

None numerical.

## Notes (do not change any value)

1. **"search/walk" is a family, not only an office search.** In groups 2a, 2c, 3a and 3c, the reported "search" value 0.85 is the path move(hall) → move(lobby) → give(...), a retreat to the courier. It is not an office search. Office search is 0.80 in 2a. The Entry-1 text quotes 0.80 for "search". I suggest relabelling the column "move(hall) family" or noting this.
2. **The 2a vs 2b loss is "nan" because the 2a action is illegal in 2b.** give(yara) is illegal after yara leaves, so no loss figure exists. This is a legitimate presentation choice. It is worth a footnote saying the loss is undefined, not zero.
3. **"Privileged ΔJ" wording.** The header says "true content revealed". The values equal the ex-ante expectation over the posterior (verified above). The realized-world gain differs: revealing "kim cooperative" in the drawn world is worth +0.082, not +0.076. I suggest stating "ex-ante" in the header.
4. **Provenance.** The report states commit `0b8346cb9f` (dirty), while HEAD is `4c46d8d`. The current generator reproduces every reported number, so there is no numerical impact. Regenerate the report at the freeze commit so the stamped commit is clean.

Scratch scripts (not part of the repo):
`C:\Users\aashraf\AppData\Local\Temp\claude\C--Users-aashraf-Desktop-Work-2026-whose-mind-matters\fda39f03-9895-4d77-a7ce-8364ec7c76c3\scratchpad\solver.py`, `checks2.py`, `checks3.py`, `render.py`.
