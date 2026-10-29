# Integration block evidence

Start with `../FINAL_REVIEW.md`.

- Plan: `../experiment-plan.md`.
- Freeze: `../integration-freeze.json`.
- Qualification: `../qualification.json` (asks, statuses, implication table, Bayes-optimal sets).
- Audit: `../audit.*`, plus the pre-gate `../audit-v1-pregate.*`.
- Analysis: `../results.md` / `.json`.
- API check: `../api-check.json`.
- Gate reviews: `../reviews/`.
- `decisions-local.csv`: one row per local decision (1,536).

Raw rows, including reasoning, are in gitignored `data/integration-block/`.

Hashes in `hashes.json` are computed over the exact exported bytes.
