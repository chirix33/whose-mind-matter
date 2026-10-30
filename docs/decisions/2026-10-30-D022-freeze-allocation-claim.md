# D-022: Freeze the allocation claim

- Status: **accepted**. Ashraf's explicit decision in the implementation session, 2026-10-30 ("Freeze it"), answering the D-021 review request (freeze, or authorize G1 only).
- Affects: the project's central claim (C1/C2, decision-value allocation of theory-of-mind computation) and all further work on it.

## Decision
- **The allocation claim is frozen.** No further experiments, builds, runs or spending pursue it.
  - G1, G2 and G3 in `reports/design-argument/DESIGN_ARGUMENT.md` are **not authorized**. The argument stays on file as a record of the one candidate setting identified, together with its narrow expected contribution.
- **The negative and positive findings stand as recorded** in `reports/PROJECT_SUMMARY.md`. They are not rewritten:
  - **Negative.** No demonstrated advantage from selecting whose mind or which path to compute, at matched resources, in OfficeMinds Tier 1. Correct notes had no practical value for the local policy. Relational computation was effectively free after cheap compilation. A small exact CPU planner (0.872) outperformed every LLM condition.
  - **Positive.** A symbolic checker using a hand-compiled public model of known templates, plus an action gate, improved the local LLM policy by +0.261 [+0.186, +0.336] (agent-reported). It beat generic LLM verification at lower token cost. It failed the frozen screen against ask-first on token cost (+0.294 at 1.26× tokens); D-020 notes that screen was restrictive.
- **Preserved as is:** the code, frozen protocols, run records, exported bundles and decision records. Services stay stopped. About USD 1.076 of the original budget stays unspent.
- **Reopening.** Any future work toward the original question needs a new research decision with its own problem-design case. This record does not pre-authorize any part of it.

## Supersedes
- D-021 item 6 ("design argument before any new block"). It was delivered, and its gates are declined.
