# Problem-design argument: when could selective mental computation pay?

Date: 2026-10-30. Status: **proposal only** (D-021 item 6). Nothing is built, run or authorized. Exact numbers come from `scripts/design_argument_examples.py` and are stored in `examples.json`. That script is CPU-only, with no model calls.

## 0. Position in one paragraph

- **Why this block failed.** In OfficeMinds both the *relations* between perspectives and their *contents* compile cheaply from templated observations. A dense tracker and an exact planner therefore leave nothing worth allocating.
- **The one setting this evidence leaves open.** *Provenance is cheap and content is costly.*
  - The agent sees for almost nothing who communicated with whom, and when: message headers, presence, room logs.
  - What was said (free text) needs an expensive extraction call to turn into a belief value.
  - Here, relations such as "F's information predates R's last change of plan" come from provenance at CPU cost. Only some content reads change the decision.
  - Choosing *whose* conversation to read, along *which* perspective path, is then a real resource decision.
  - Dense parse-once reading pays for every transcript. An exact planner can price reads but cannot obtain content without them.
- **The caveat.** The expected contribution is **narrow**. It reduces to value-of-information over a provenance graph, and the savings depend on how sparse relevance is in the generator. §5 lists stop rules that would end it cheaply.

## 1. Why mental inference must be costly, and when it is

The cost per unit is one extraction call over one transcript. Measured on the local backbone: a requested note cost 4,027 processed tokens (repair block, all attempts), against 5,168 for a whole direct episode in the hybrid pilot.

Inference is costly only if **all three** hold:
- **(a) No cheap parser.** The content is free text that a deterministic parser cannot map to the latent value: paraphrase, corrections, coreference.
- **(b) Sparse relevance.** Most transcripts never affect any decision in the episode.
- **(c) Visible provenance.** Headers make relevance predictable without reading.

If (a) fails, parse-once is cheap (this block's regime). If (b) fails, dense encode-once amortizes (E5 below). If (c) fails, selection needs reading, and the economics collapse.

## 2. Worked examples (exact; reproduced by the script)

**Setup.**
- R announced office a, then in transcript t3 told courier F, and only F, its new office m ∈ {b, c}. F forwards packages to m.
- If a later transcript t7 between R and X exists (its header is visible), it says "staying" with probability 1−q, or "moving to the other office" with probability q. F did not hear it.
- Eight other transcripts carry nothing about R under the public model.
- The robot is in the lobby with F and can give(F) or search in person (horizon 8). One read is priced at λc = 0.04 return as a planning operating point; the full comparison would use a frontier over λ.

| case | value with no reads | read t3 | read t7 | decision value picks | entropy picks | structural rule reads | dense reads |
|---|---|---|---|---|---|---|---|
| E1: t7 exists, q = ½ (×1 and ×4) | 0.80 | 0.80 (VOI 0) | 0.90 (VOI **0.10**) | t7 | t7 (1.5 vs 1.0 bit) | 2 | 10 |
| E2: no t7 header | 0.95 (give: provenance alone settles alignment) | 0.95 (VOI 0) | — | **STOP** | t3 | 1 | 10 |
| E3: q = 0.02, ×1 | 0.92 | 0.92 | 0.948 (VOI 0.028 < 0.04) | **STOP** | t3 | 2 | 10 |
| E3: q = 0.02, ×4 | 0.89 | 0.89 | 0.948 (VOI **0.058**) | **t7** | t3 | 2 | 10 |
| E4: q = 0.2, ×1 | 0.80 | 0.83 (VOI 0.03) | 0.93 (VOI **0.13**) | t7 | **t3** (1.0 vs 0.92 bit) | 2 | 10 |

What the examples show:
- **Whose mind and which path.** To judge the handoff to F, the useful read is **R's later conversation**, not F's own source (t3). F's belief is already pinned by provenance; only R's later state is uncertain.
- **Uncertainty is the wrong objective.** It reads F's source in E2–E4.
- **Structural relevance over-reads.** It reads every transcript involving R or F.
- **Stakes matter.** In E3 they alone flip READ vs STOP.
- **E5, the kill case.** If a day's tasks together need all 10 transcripts, encode-once dense reading costs the same as selective reading: saving 0.

## 3. Why the cheap competitors would not erase the advantage, if §1 holds

- **Parse-once / dense tracker.** It must read every transcript once. Its cost is ∝ total text, against selective cost ∝ the union of decision-relevant reads. The advantage is about 1 − U, where U is the union-relevant fraction over the episode. It exists only if U is small, which E5 shows is not guaranteed.
- **Exact planner.** It can compute the value of each read from provenance (it *is* the proposed selector, on CPU), but it still has to buy content.
  - "Planner + read everything" is the dense baseline.
  - "Planner + read nothing" is the provenance-only baseline.
  - The method is "planner + decision-value reads".
  - All three share the same planner, which removes the LLM-action-selection weakness exposed by this block (0.872 vs 0.564) from the comparison.

## 4. Matched-resource test of the original question

The same exact planner and the same extraction model are used throughout; only the **read policy** varies.
- **Read policies:** decision value (frozen), content entropy, structural (R and couriers), retrieval (similarity of headers or text to the task), random, dense encode-once, provenance-only.
- **Separate baseline:** a direct LLM with all transcripts in context.
- **Resources:** processed extraction tokens and calls at read budgets of 1, 2 and all reads.
- **Primary outcome:** return at matched read-token budget, as a frontier over budgets.
- **Grouping:** paired, by base scenario. This tests C1/C2 directly: which perspective to compute, at what cost, against the alternative objectives.

## 5. Gates and stop rules (proposed; none authorized)

**G1: symbolic twin, CPU only.** Contents are latents; no text, no model. Sample the generator over its intended cast and conversation rates, which are fixed *before* the measurement.

| ID | measure | proceed if | stop if |
|---|---|---|---|
| G1a | union-relevant read fraction U (exact decision-value policy at λc) | U ≤ 0.35 and return ≥ full information − 0.02 | U > 0.6 |
| G1b | decision-value choice ≠ entropy choice and ≠ structural bundle | ≥ 25% of decision states, **and** structural needs ≥ 1.5× the reads or loses ≥ 0.05 return | otherwise: structural relevance would be the contribution, not decision value |
| G1c | provenance-only loss vs full information | ≥ 0.10 in ≥ 30% of states | otherwise: nothing costly is needed |
| G1d | STOP and stakes | ≥ 20% of states are STOP, and some flip with stakes | none |

**G2: extraction necessity.** Needs a model and a text generator, so it is **not** authorized now. Small and pre-registered:
- **Proceed only if** a deterministic parser recovers the latent values with accuracy below 0.8, **and** the backbone reaches at least 0.9, **and** one read costs at least 1k processed tokens.
- **Stop if** the parser reaches 0.8 or more (parse-once is cheap), or the backbone falls below 0.85 (extraction noise dominates).

**G3: matched-resource pilot (§4).** Only after G1 and G2. Acceptance:
- decision value beats structural by ≥ +0.05 at equal tokens, **or** uses ≤ 0.6× the tokens with paired CI lower bound > −0.03;
- **and** it comes within 0.02 of dense at ≤ 0.5× the tokens.
- A return/resource frontier replaces this block's single-tolerance screen (D-020 §3).

## 6. Risks to weigh before any authorization

- **Generator-dependence.** U, and so the savings, is set by the generator's conversation rates. Results must be reported as a curve over U, not one point.
- **Novelty.** This is classical value of information over a provenance graph. The claim would rest on directed-path selection (E4: read R's later conversation, not F's source) and matched-resource evidence against the D1–D5 objectives. Prior work on encode-once perspective tracking and decision-guided selection (D-019 literature notes) must be engaged.
- **Building G2/G3 is a new text environment.** It brings its own problems: valid targets, leakage from private content, extraction calibration. That is a separate project extension, not a continuation of OfficeMinds Tier 1.
- **A cheap path to ending this.** If G1 fails, freezing the project's allocation claim is the recommended outcome. G1 costs about one CPU day and no model calls.
