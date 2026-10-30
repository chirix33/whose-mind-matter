# Review request: 2026-10-30 (D-021 problem design)

**Read first:** `reports/design-argument/DESIGN_ARGUMENT.md` (a proposal; nothing started). The project record is `reports/PROJECT_SUMMARY.md`.

## The argument in brief
- Selective mental computation can pay only when **provenance is cheap and content is costly**: who talked to whom is visible for almost nothing, but what was said needs a model extraction call. It also needs relevance to be sparse over the episode and predictable from provenance.
- Exact small examples (`reports/design-argument/examples.json`):
  - decision value reads R's later conversation while entropy reads F's source;
  - provenance alone gives STOP;
  - stakes flip READ vs STOP;
  - in a kill case where relevance covers the log, dense encode-once reading costs the same.
- The comparison keeps one exact planner and one extraction model and varies only the read policy, at matched read-token budgets. This removes the LLM action-selection weakness exposed by the 0.872-vs-0.564 result.
- **The contribution is narrow:** value of information over a provenance graph. Savings depend on the generator's relevance sparsity.

## Decisions requested
1. **Freeze** the allocation claim now; or **authorize G1 only**: a CPU-only symbolic twin, about one day, no model calls, with the stop rules in §5. If G1 fails, freeze.
2. If episode-level reproduction matters for the record, attach `reports/hybrid-block/audit/` (`episodes.csv`, `interventions.csv`, `episodes-agent.jsonl.gz`, `input-audit-checks.jsonl`, `HASHES.sha256`) to the review conversation.
