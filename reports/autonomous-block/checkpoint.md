# Autonomous block checkpoint

**Updated:** 2026-10-28, Round 1 declared; no new model outputs yet.

**State**
- Block registered: `AUTONOMOUS_RESEARCH_BRIEF.md`, with a pointer in `AGENTS.md`.
- Round 1 is declared in `experiment-plan.md`. Code ready: r4 rules, pilot-v2.1, scoring v3, re-rendered contexts, cross-process ledger. 275 tests pass.
- Running jobs: none.
- **Spend** (ledger `~/officeminds-runs/api-spend-ledger.json`, WSL): USD 1.3123 spent before the block, 0 in this block, no reservations. Cap USD 5; USD 3.69 remains.

**Next action**
1. Opus reviewer gate on the Round 1 plan, plus Sonnet check of the reference-audit facts.
2. Local cells:
   ```bash
   python3 scripts/run_unit_contexts.py --config configs/models/local_gpt_oss_20b.json --effort low --max-tokens 4096 --contexts reports/autonomous-block/unit-contexts-v1-r4.jsonl --packages pilot-v1 pilot-v2 pilot-v2.1
   ```
   The local server must be running (`scripts/serve_local_model.sh`).
3. After the plan review, the API cells: same command with `--config configs/models/api_gpt_6_1_sol.json --max-tokens 6000`.
