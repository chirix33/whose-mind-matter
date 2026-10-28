# Review request — 2026-10-28 (autonomous research block, final)

**Read first:** `reports/autonomous-block/FINAL_REVIEW.md` (recommendation first, about 3 pages). The bundle index is at the end of that file. Per-round gated conclusions: `reports/autonomous-block/round{1,2,3}-summary.md`. Reviewer reports: `reports/autonomous-block/reviews/`.

The earlier questions are now resolved by the block:
- the old Q1 (overheard remarks vs. scoring) is resolved by public rules r5;
- the old Q2 (pilot-v2 over-abstention) is resolved by pilot-v2.1 on the API, though not on the local model;
- the old Q3 (an oracle-content crossed run) is superseded by the Round 2 and Round 3 four- and five-condition diagnostic.

## Decisions that need research review
1. **Contract and package.** Adopt r5 rules and pilot-v2.1 as the working contract and package, pending an out-of-sample check on fresh dev-v2 contexts? The Round 1 gains are in-sample: the rules and package were written after inspecting these contexts.
2. **State design for the next milestone, within the original outline.** States where:
   - the relevant mental content cannot be had by one cheap ask (absent, unreachable or costly informants);
   - an outdated or false belief matters at realistic stakes;
   - the unit content does not reveal the target (no K(recipient)-of-own-location leakage).

   The baseline keeps the same observations and an equally cautious prompt. Then a fresh four-condition value-of-notes diagnostic. **This needs a budget decision:** USD 1.13 of the USD 5 cap remains.
3. **Ambiguous references.** Disclose the generator's base rates in the public rules, or change the label target so the reference uses only disclosed structure?
4. **The doubt finding.** Is a "caution presentation" a legitimate method component (tested fairly, with the same caution given to the baseline), or a calibration confound to remove from value estimates?
