# D-017 — Integration-block review: method review before any further LLM run

- Status: **accepted** (research-driver ruling via Ashraf, 2026-10-29, `research-reviews/INTEGRATION_BLOCK_RESEARCH_DECISIONS.md`; repo copy `INTEGRATION_BLOCK_RESEARCH_DECISIONS.md`, sha256 `adee8bfeb4146b1439dee39d5d7dfe680f9559c5645896c3390f8b130670b70b`)
- Affects: everything after D-016. The deliverable is `reports/method-review/METHOD_REVIEW.md`, which is a proposal and was not launched.

Binding points, restated:
1. **Stop the content/display tuning sequence.**
   - No allocation controller training, probe expansion, new backbone comparison or environment redesign.
   - No further LLM data collection, prompt tuning, new seed sweep or task modification during the review.
2. **The post-ask implication effect is closed as unresolved.** Its reading is: no demonstrated help; harm not excluded; magnitude unresolved. The historical classifier output "neither (practically small)" in `reports/integration-block/results.md` is preserved, not rewritten.
3. **No new paid calls.** About USD 1.076 remains under the USD 5 cap. A future backbone comparison must answer a specified allocation or compute-efficiency question.
4. **The required method review (A–D):**
   - (A) the bounded actor, history, memory, budget, unit output and all charged computation, with value defined for that actor, return at matched compute primary, and action and retained-memory effects kept distinct;
   - (B) a relationship audit, separating robot-estimate uncertainty from a person's uncertainty, false belief or lack of belief, with no oracle success field as a fix;
   - (C) a complementarity test specified but not run, with singletons, the pair, irrelevant and redundant controls, a matched generic computation, and cost accounting;
   - (D) explicit feasibility and proceed/stop criteria that avoid endless revision.
5. **Return one method-review document** that states what is retained from the original method and what would be a versioned change. Do not launch it.

Corrections carried from the ruling:
- K(R) is missing from the allocated notes, not from the information available to the policy.
- The K(F→R)+K(R) complementarity is a hypothesis.
