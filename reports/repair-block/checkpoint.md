# Repair block checkpoint (D-015)

**Updated:** 2026-10-29, after the second PC restart.

**Done:**
- Entries 1, 1a, 1b and 1c, with every gate passed and its required changes applied: plan, prompt, Stage 1 results (Opus), Stage 1 recompute (Sonnet, CONSISTENT).
- The Stage 1 regression check.
- Freeze: `stage1-freeze.json`, committed in `27c324e` (K = 24; seeds 20261100–20261123; 576 states); `verify` passes.

**Running / next:**
1. DONE: notes (856/864 valid; proof committed in `aa75046`).
2. DONE: policy run `repair-stage2-20261029-132459-743ace` (24 blocks, 4032 episodes, 39 min).
3. `report_repair_stage2.py <run_dir>`, then the results gates (Opus and Sonnet), then the handoff.

**Rules in force:**
- No prompt, decoding or validator changes.
- Stage 2 outputs are never used to change anything.
- No paid calls: the ledger stays at USD 3.8690.
- The vLLM server must be started (`scripts/serve_local_model.sh`) after any restart.
