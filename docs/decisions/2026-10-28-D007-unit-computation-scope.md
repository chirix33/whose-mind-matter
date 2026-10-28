# D-007 — Scope of a unit computation (Stage 1 review Q1)

- Status: **accepted** (Stage 1 research review, 2026-10-28; supplied by Ashraf from the research conversation; source file `research-reviews/stage-1-research-review.md` is gitignored, so binding points are restated here)
- Affects: D-001 implementation; `vomi/oracle.py` unit outputs; LLM pilot unit schema; compute accounting

## Ruling
- **Exact generator marginal (option A)** is acceptable as an *exact symbolic reference under the declared model*. It is not the deployment algorithm and not evidence that the computation is cheap.
- The local-model marginal (B) is an optional sensitivity diagnostic. No hand-engineered person-local table (C).
- Whole-history context is permitted. The output must stay about the selected (path, variable) and be justified by robot-visible evidence. It must not contain other minds' full states, a task-action recommendation, or a query to the actual hidden world.
- **Record inference dependencies and shared preprocessing cost.** Offline exact-reference cost is reported separately from deployment cost. A deployed adapter that calls an exact global solver must count that work.
- A single scalar can still depend on expensive global inference and can correlate with the answer. **Output dimensionality guarantees neither low cost nor absence of leakage.**
- **Helpfulness alone is not leakage.** A result legally derived from visible evidence may answer the task. Audit inputs and semantics instead. (This supersedes the Stage 1 report's description of the K(alice) content marginal as a "leak".)
- **Typed outputs are the main method.** Every LLM pilot unit returns, as applicable:
  - path, variable, fact or assessment, and time;
  - a typed belief/intent hypothesis or a finite distribution, including `unknown`;
  - confidence and supporting visible event/utterance IDs;
  - unresolved contradictions.
- The scalar P(default holds | h) is kept only as a separately named **diagnostic record**.
- K(j) = what j believes; K(j→k) = j's belief about k's belief; R(j→k) = j's assessment of k. Exact posterior correctness probabilities may be evaluator annotations or optional uncertainty fields. They are never read from hidden truth by a deployed unit.
- Keep the timestamp and update semantics of every output. Stale and contradicted records are visible to the policy, with a defined refresh or abstain rule. **Add one trace where new evidence changes an earlier useful inference.**

## Implementation (Stage 2 corrections)
- Records `grounded_scalar` (diagnostic) and `grounded_typed` (exact typed symbolic reference over (content, default-holds) hypotheses).
- `vomi/unit_schema.py` defines the typed LLM unit output.
- The graph has an explicit `refresh` with counted cost, plus the evidence-change trace `reports/bundle/trace-evidence-change.json`.
