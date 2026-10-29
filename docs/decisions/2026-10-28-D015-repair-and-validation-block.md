# D-015 — dev-v3 research review: one repair-and-validation block

- Status: **accepted** (research-driver review via Ashraf, 2026-10-28, `research-reviews/DEV_V3_RESEARCH_REVIEW.md`; repo copy `DEV_V3_RESEARCH_REVIEW.md`, sha256 `813bc8c583e7ee6bba48ab3f5828669423a11f4dfe89a3accffddc60dab24d70`)
- Affects: the note package (new version), notes rendering (new revision), the Stage 2 replication on fresh dev-v3 seeds, all later fixed-note reports.

Binding points, restated:
1. The dev-v3 block shows progress on task-level social relevance under scripted semantics. Its correct-note signal is promising but uncertain, and the deployable inferred pipeline still fails. Allocation (requirement 3) is untested. No allocation training.
2. **Q1:** approve one documented package revision:
   - stable, visible citation IDs for public-model facts, registered consistently in prompts, validation and rendering; invented IDs are still rejected;
   - inference instructions revised once to separate prior from posterior after testimony, while keeping no-belief distinct from uncertainty and abstention;
   - no hidden labels in the deployable unit; any new method component (for example an arithmetic tool) is versioned and reported.
3. **Q2:** the primary endpoint is expected task return, with compute stated. Errors, timeouts, steps and compute are reported separately and are not chosen post hoc. No additional API spending is needed now; the scope is the local backbone.
4. **Q3:** depth controls are required (a K(R) first-order control and the 3a/3b contrast) before any depth claim.
5. **Matched interface:** inferred and reference notes go through the same template and fields. The correctness probability is not given to the reference alone; a correctness-augmented reference may only appear as a separately labeled diagnostic. Citations are kept for audit, with a consistent policy-visible display. No source label may act as an authority cue.
6. Score the full distribution: TV against the aligned posterior, unsupported mass, coverage.
7. **Block:** at most two stages.
   - Stage 1: repair and qualify, then freeze.
   - Stage 2: one local replication on fresh, preselected dev-v3 seeds with the generator unchanged; STOP controls, first-order, depth contrast and probabilistic cases; more independent base worlds rather than repeats; pairing by scenario; pre-declared sample size from a precision/power calculation; conditions none, revised inferred and matched reference, plus the depth controls; payloads frozen before policy; failures charged; paired analysis across base scenarios with the error tail kept; compute charged.
8. Return with the frozen protocol, scenario count, paired results, fidelity distributions, compute and traces. The recommendation must be tied to the four listed outcomes. No automatic training or another prompt revision.
