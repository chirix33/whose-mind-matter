# Review request: 2026-10-30 (D-020 audit of the hybrid block)

**Read first:** `reports/hybrid-block/audit/AUDIT.md`. Evidence is in the same directory and listed in `HASHES.sha256`. The source is `source-ef77ad6.zip`.

## Findings
- **Input contract.** The deployed checker and the Bayes reference received the per-instance generator `Scenario`: the disclosed prior plus a builder carrying the construction ID and role→name mapping. That is not literally what the LLM saw.
- **Equivalence test.** Compile a public model from the LLM's own card: every generator pattern with a byte-identical task card, mixed uniformly. It gives identical p, location, verdicts, t0 values and actions (380/380 checks, 192/192 states). The visible history always pins a single pattern.
  - So the metadata was redundant for these templates. The checker still depends on hand-compiled template engineering and does not read text.
- **Bayes planner.** Realized deterministic return on the same 192 hidden draws: 0.872 (expectation 0.885). This is a CPU evaluation added in the audit.

## Decisions requested
1. Accept the audit, and the corrected description of the checker ("hand-compiled model of the task-card templates, output-equivalent to the card"), as closing D-019/D-020.
2. Next step. Freeze and consolidate this line, or specify, as a separate project-extension proposal, how to establish evidence of a genuine perspective-reconstruction bottleneck before any new environment. No experiment is proposed or started here.
