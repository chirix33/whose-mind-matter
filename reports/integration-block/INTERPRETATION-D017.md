# Interpretation note added under D-017 (2026-10-29)

The files of this block are hash-pinned in `evidence/hashes.json`, so they are left byte-identical. This note adds the corrected interpretation required by the research review (`INTEGRATION_BLOCK_RESEARCH_DECISIONS.md`).

- **Post-ask implication effect.** `results.md` shows the frozen classifier's reading, "neither (practically small)". That historical output is preserved.
  - The corrected interpretation is: **no demonstrated help; harm not excluded; magnitude unresolved**. The estimate is +0.083 wrong rate, 95% CI [−0.036, +0.208].
  - This branch is closed. It will not be resolved with more seeds.
- **The two harm readings** (the t0 implication line in 3b, and omission of the post-ask stale line) are descriptive. They do not survive Holm correction across the three readings, and there are only sixteen independent base scenarios per construction pair. Neither intervention is to be described as generally harmful or beneficial.
- **The positive controls did not establish selective improvement.** Omitting the warning raised correct and wrong handoffs together, which points to a broad caution effect rather than better discrimination.
- **K(R) was missing from the allocated notes, not from the information available to the policy.** The full visible history and public rules support the inference. The complementarity of K(F→R) and K(R) is an untested hypothesis.
- **The API check** (8 contexts, 1 response per condition, USD 0.05509) shows a ceiling. It gives no evidence of note benefit and is not a model benchmark.
