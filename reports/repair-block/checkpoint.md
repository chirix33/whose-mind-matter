# Repair block checkpoint (D-015)

**Updated:** 2026-10-28, after a PC restart.

**Done:**
- Pre-registration (Entry 1) and the plan-gate amendment (Entry 1a, RC1–RC14).
- The pilot-v2.2 package: PM citation IDs, the prior-vs-posterior section, the r7 matched renderer and validator v22.
- Tests: 304 passing.
- Precision simulation: K = 24, the largest feasible K, since the criterion was not met (`power.md`).
- Fresh-seed symbolic qualification: 576 states, all pass (`stage2-qualification.json`).
- The Stage 2 runner and analysis scripts (`scripts/run_repair.py`, `scripts/report_repair_stage2.py`).
- Last commit: `9b0c38d`.

**Next, in order:**
1. The Opus gate on the v2.2 prompt, renderer and K, before any model call. It was re-run after the restart.
2. `run_repair.py regress`: the Stage 1 regression check on inspected Round B states.
3. The Stage 1 results gate (Opus and Sonnet).
4. `run_repair.py freeze` from a clean tree, then commit.
5. `notes`, then commit `stage2-notes-freeze.json`.
6. `policy`, in complete seed blocks, within 4 h.
7. `report_repair_stage2.py`, the gates, and the handoff.

**Rules in force:**
- No model call before step 1 passes.
- No prompt, decoding or validator-acceptance changes after any regression output (RC11).
- Nothing on dev-v3 Stage 2 runs before the freeze commit.
- No paid calls: the ledger stays at USD 3.8690.
