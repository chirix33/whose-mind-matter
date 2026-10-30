# Project summary: Whose Mind Matters? (as of 2026-10-30, D-021)

**Status.** The OfficeMinds Tier 1 implementation line is **closed** (D-021).
- The intended contribution, choosing whose mental state and which perspective path to compute at a competitive resource budget, has **not** been demonstrated.
- No runs, spending, training or prompt work are authorized.
- Next decision: problem design (`reports/design-argument/DESIGN_ARGUMENT.md`, a proposal only).
- Budget: USD 3.924 of the original 5 spent; about 1.076 unspent. vLLM stopped.

## Findings by block (development evidence only; nothing confirmatory)

| block (record) | main finding |
|---|---|
| Stage 0–1 (D-001…D-012) | Simulator, exact symbolic oracle, label records and tiny cases qualified against hand derivations |
| Pilot v1 (D-013) | Direct full-history LLM policy strongest (+0.617). Explicit units hurt via unsupported content (C3 mechanism observed). The router did not track the reference |
| Model diagnostic / autonomous block | The policy model drives gains; notes show no reliable value. The one fix was a caution cue, not content value |
| dev-v3 (D-014), repair (D-015) | On 288 fresh scenarios, correct reference notes have no practical value (−0.024 [−0.074, +0.028]). The policy does not integrate them |
| Integration (D-016) | Action-consequence lines harmed. The stale label works as a caution cue. The API policy is at ceiling |
| Method review (D-017), concept (D-018) | Notes are functions of the full history (zero value to a Bayes actor). They expose marginals while handoffs need joints. Each costs about 77% of a no-note episode |
| Hybrid block (D-019) | A provenance/referent engine matches enumeration (1,008/1,008). Every relation costs about 20 µs and 0 tokens, so there is nothing to allocate and the hybrid is closed |
| Fallback pilot (D-019) | Symbolic checker + action gate vs direct: +0.261 [+0.186, +0.336]. Beats the generic LLM check by +0.131 at 0.76× tokens. Beats ask-first by +0.294 but at 1.26× tokens: **failed** the frozen screen, which D-020 notes was restrictive |
| Audit (D-020, D-021) | See the input contract and evidence status below |

## Corrected input contract (D-020 / D-021)

- **The deployed checker is a *symbolic checker using a hand-compiled public model of known templates*.**
  - It received generator metadata (`inst.scenario`: construction ID, role mapping).
  - A model compiled from the LLM's own task card gives identical outputs on every audited check and state.
  - Arbitrary language understanding, and compiling unseen templates, were not evaluated.
- The rollout gain is **not** credited to the joint referent representation. The pilot used `ExactOracle`, and no marginal-vs-joint ablation was deployed.
- A small exact CPU planner on the same public inputs reaches **0.872** realized return (0.885 expected), against 0.564 for checker+LLM. It is a post-pilot diagnostic, built with substantial task-specific engineering.

## Evidence status

| quantity | status |
|---|---|
| 1,008 relation-qualification checks; 1,440 history-equivalence checks | **reviewer-reproduced** |
| text-compiled = instance model on 192/192 states (t0 value and best action); history pins one pattern on 192/192 | **reviewer-reproduced** |
| planner 0.884575 expected; 0.871875 realized (×1 0.870833, ×4 0.872917) | **reviewer-reproduced** |
| fallback pilot means, paired CIs, criterion outcomes | agent-reported (records in `reports/hybrid-block/audit/`, not yet attached for review) |
| 380 logged checker comparisons; 384 episode replays; 320-test suite | agent-reported |
| all earlier blocks | agent-reported, with reviewer arithmetic checks as recorded in each FINAL_REVIEW |

## Where things are

- **Hybrid block handoff:** `reports/hybrid-block/FINAL_REVIEW.md` and `audit/AUDIT.md`. Exported records are in `audit/`, listed in `HASHES.sha256`:
  - `episodes.csv`, `interventions.csv`, `episodes-agent.jsonl.gz`;
  - `source-ef77ad6.zip`, run manifests.
- **Raw runs:** `~/officeminds-runs/` (WSL).
- **Decisions:** `docs/decisions/` (D-001…D-021 and the discrepancy log).
- **Original plan:** `docs/research/methods-experiments-v2.md` (verbatim outline). C1–C5 remain hypotheses. C1/C2 are unsupported in the tested regime; C3–C5 are untested since D-013.
