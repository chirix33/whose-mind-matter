# D-013 — Pilot review: interface repairs, grounding package, scoring v2, model diagnostic

- Status: **accepted** (pilot review 2026-10-28, `research-reviews/pilot-model-diagnosis-and-next-step.md`, supplied by Ashraf; gitignored, so binding points are restated here)
- Affects: `src/vomi/pilot.py` (renderer r3, packages), `src/vomi/unit_schema.py`, `src/vomi/graph.py`, `src/vomi/fidelity.py`, `src/vomi/clients.py`, pilot reports

## Rulings
- The pilot does **not** establish that gpt-oss-20b is the cause. Run one documented grounding revision and a small controlled API comparison before any bulk labels or router training.
- Do not pivot to RQ3 alone. The evaluated router was zero-shot, not the proposed learned VoMI-Router.
- **Q1:** approve one versioned grounding revision. A citation-presence rule alone is insufficient and must not turn model uncertainty into claims of human ignorance.
- **Q2:** no bulk labels or controller training yet.
- **Q3:** approve incorrect / unsupported / leaked scoring with explicit abstention, keeping the original scoring.
- **Q4:** keep the zero-shot router fixed during this diagnostic.

## Implemented
| Review item | Implementation |
|---|---|
| A. Evidence in the policy interface | r3 notes show cited evidence IDs and short excerpts, per-hypothesis support (pilot-v2), and the inference status. The validator stays a STRUCTURAL check: a real but irrelevant citation passes, and support adequacy is judged by scoring and audit |
| A. Grounding package | `pilot-v2`: per-hypothesis support (evidence ID, kind = observation / testimony / access_inference, note); generic examples from a warehouse setting (supported false belief; unresolvable attribution) |
| B. Mental ignorance vs. inference uncertainty | `unknown` = the person has no belief; status `insufficient_evidence` = the robot cannot tell, and still carries a distribution over the person's possible states |
| B. Scoring | `vomi/fidelity.py`: correct_supported, correct_unsupported, incorrect_supported, unsupported_incorrect, leakage, abstained; log score, Brier, cross-entropy vs. the evidence-grounded posterior. Top-1 kept as a diagnostic |
| C. Epistemic contract | r3 task card adds one neutral, identical paragraph of people rules (witness / sincere tell / claims do not change listeners' beliefs / trusted adoption / deliberate misleading / no belief without access). It matches the scripted event semantics and exposes no hidden state. Frozen worlds unchanged; all arms use the same description |
| D. Factual refutation ≠ false belief | `refutation_mode="fact_only"` (r3): a physically refuted claim marks K(speaker) `fact_refuted` (shown to the policy as "may still believe it"), other paths `stale`; no forced refresh |
| Reporting corrections | erratum at the top of `reports/pilot/pilot-report.md`; runs now record dirty paths |
| API reference | `OpenAIResponsesClient` (Responses API mapping checked against official docs), `configs/models/api_gpt_6_1_sol.json`, persistent spend ledger with a hard cap (default USD 5, env `OFFICEMINDS_API_CAP_USD`); the key is read from env `OPENAI_API_KEY` only |

r2 rendering stays reproducible (`rev=2`, `refutation_mode="contradict"`). The original pilot-v1 results and traces are unchanged. A fresh pilot-v1 replay at r3 is the corresponding repaired-interface comparison, not a byte-identical rerun.
