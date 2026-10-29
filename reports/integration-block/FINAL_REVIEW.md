# Integration diagnostic (D-016): consolidated report for the research conversation

All results are development data from single-decision probes. They are not return estimates. Gates:
- Opus (validity): `reviews/plan-opus.md` (RC1–RC9) and `reviews/results-opus.md` (required changes 1–8, applied here).
- Sonnet (recompute): `reviews/results-sonnet.md`, CONSISTENT. Its own code reproduced every contrast, all 74 raw-rate rows, all three readings, all 1,536 value gaps (0 mismatches) and the API cost.

## Recommendation (D-016 §5, bullet 4)
**Neither factor helped. Stop content and display tuning, and return to a method/environment review.**
- Do not propose dependency-aware invalidation (bullet 2 does not apply; see below).
- Do not add more seeds, backbones or render variants to chase a positive result.
- Allocation training stays on hold.
- One open question remains, *unresolved* (bullet 5): the post-ask implication effect, +0.083 [−0.036, +0.208] wrong rate.

## What ran
- **Probe:** 4 constructions (3b and 2b; positive controls 3a and 2a) × 8 fresh seeds (20261200–07) × ×1/×4 × (3 t0 + 5 post-ask conditions) × 3 draws = **1,536 local decisions**.
  - Exact reference notes, frozen once and reused; local gpt-oss-20b, unchanged.
  - Frozen at `7877fa0` before any output. Every prompt hash, source hash and Bayes-optimal set matches the freeze; the t0 duplicates are byte-identical; dispatch was counterbalanced.
  - 11 truncated attempts, all recovered on retry; 0 fallbacks; no fallback-rate imbalance. Wall clock 6.7 min.
- **Implication line** (the action-consequence mapping): "Given this estimate and the stated forwarding rule, give(X) sends the package to <office> with probability <p>". It is built only from the frozen note and the public handoff route (80 lines qualified, no unknown mass).
- **Stale omission:** the post-ask stale label is triggered by people being seen or mentioned, not by the ask itself, so the factor omits every `stale` status line.
- **API check:** 16 decisions, gpt-6.1-sol at low effort, one attempt each. Worst case USD 0.42; actual **USD 0.055**; the ledger is now **USD 3.924 of 5**.

## Results (16 base units per pair; 95% CI resampling seeds within construction; exact sign-flip p)

| Pre-declared reading | Key number | Note |
|---|---|---|
| **t0: implication = harm** | negative-pair wrong, impl − content: +0.115 [+0.031, +0.198], p = 0.045 | carried by 3b |
| **post-ask: implication = "neither"** | impl_main wrong: +0.083 [−0.036, +0.208]; gap +0.117 [−0.119, +0.367] | through the rule's non-negative-point clause: **no help, harm not excluded, size unresolved** |
| **post-ask: omission = harm** | omit_main wrong: +0.083 [+0.016, +0.141], p = 0.043 | a non-specific caution signal; see below |

Both harm readings are **descriptive**. There is no multiplicity correction across the 3 readings, and Holm over 3 would not reach 0.05. Neither effect is established. The interaction (negative-pair wrong +0.062 [−0.125, +0.250]) is unresolved. A resolving test of the post-ask implication effect, with a half-width of about 0.05, would need roughly 45–50 seeds per construction (extrapolated from the observed CI width).

**Comparisons with no notes:**
- **Negative pair:** no note condition beats no notes at either context. At t0, content − none is +0.031 and impl − none +0.146 in wrong rate. Post-ask, content|shown − none is −0.052 [−0.219, +0.104].
- **Positive pair at t0:** notes *reduce* correct handoffs relative to no notes (content −0.104; impl −0.125 [−0.229, −0.031]), because the policy asks first more often.

**Mechanism, descriptive:**
- **The implication line at t0 (3b).** In 3b every handoff is wrong.
  - The handoff rate rises from 0.062 (none) to 0.167 (content) to 0.354 (impl); gives under impl went from 8 to 17 of 48, all wrong.
  - The line is a **correct** application of the public rule to a **correct** note. What the policy lacks is R's changed belief, which is visible in the history but sits in an unallocated unit, K(R).
  - The reasoning shows the destination treated as success ("he forwards to desk_9. Zane is in desk_9").
  - This is consistent with the pre-registered certainty confound but not separated from it: the probe has no case with a certain *and* correct destination. In 2a the stale courier also gets a certain-but-wrong line, yet 2a handoffs did not rise (0.062 → 0.042), so the effect is construction-specific.
- **Omission.** Hiding the stale line raises handoffs in both pairs. Positive-control correct handoffs rise by +0.078 [+0.010, +0.151], and negative-pair wrong handoffs rise by +0.083.
  - Symbolically, the ask leaves the note's content **and** its public posterior unchanged in all 16 negative-pair units. The stale line therefore carries no validity information there; it works as a generic caution signal.
  - That is why bullet 2 (dependency-aware invalidation) does not apply: a dependency-aware label would remove the line exactly in those cases.
- **2a post-ask, split by who was asked:**
  - asking the informed courier (30 decisions per condition): correct handoffs 0.50 with no notes, 0.47–0.63 with notes;
  - asking the stale one (18 per condition): almost no handoffs in any condition.
- **API (bullet 3, with caveats):**
  - 16/16 API decisions were Bayes-optimal (gap 0), with and without notes. At the same 8 contexts the local policy made 5 wrong handoffs in 48 decisions.
  - This is **consistent with a local-policy capability limitation**. It is a ceiling result over 8 contexts with 1 draw each, under different settings: 1 attempt vs 3; 2,000 vs 1,024 output tokens; no temperature sent; different effort semantics.
  - It is not a backbone benchmark and not evidence about note value.

**Audit of the existing repair traces** (`audit.md`, rubric v2; v1 applied once before the gate, kept as `audit-v1-pregate.*`):
- **Asks:** every 2b and 3b ask left the person's belief and the robot's posterior unchanged. In 3a the posterior almost always changed; 2a was mixed by who was asked. True content was never changed by an ask, so every posterior change is a robot-estimate update.
- **Stale exposure:** about 100% of the decisions after an ask, lower after sightings only.
- **Reasoning codes:** heuristic and non-causal.
  - In 2b the rubric codes 82 of 86 decisions as "other", which makes it uninformative there.
  - In 3b, 28 of 58 give/drop decisions are coded "applies the forwarding rule", all of them errors, with 8 uncertain.
- No causal comparison is made between episodes that asked and episodes that did not.

## What this does NOT show
- That the mapping was false or misleading: it is a correct rule application.
- That either harm effect is established.
- Anything about return, allocation or depth (C4).
- That the API model is superior, or that notes have value under it.
- That dependency-aware invalidation would help.

## Decisions for the research review
1. The method/environment review under bullet 4. The recurring pattern is that the local policy uses correct mental content poorly, or acts on a correct partial view, as in 3b, where the needed unit K(R) is unallocated. Is the next step about **which units are allocated together** (complements such as K(F→R) with K(R)), about the policy backbone, or about environment fit?
2. Whether the post-ask implication question (unresolved) is worth a resolving test of about 45–50 seeds per construction, or should be dropped.
3. Whether the API capability observation warrants a properly designed backbone comparison under a separate budget. About USD 1.08 of the original cap remains.

**Corrections from D-016 §6:**
- The repair-block 3b example's **cumulative** return is −2.10; −2.05 was its final action's reward.
- Hashes in `evidence/hashes.json` are computed over the exact exported bytes, and the CSVs are written with LF.
- Deployment cost: in this probe each frozen note was reused across 8 conditions × 3 draws, an experimental reuse that does not apply per independent episode at deployment.
