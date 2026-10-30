# Whose Mind Matters? — OfficeMinds + VoMI-Router

Research code for *Decision-Value Allocation of Theory of Mind over Perspective Graphs*. The full plan is in [docs/research/methods-experiments-v2.md](docs/research/methods-experiments-v2.md), a verbatim copy of the outline. Implementation rules are in [AGENTS.md](AGENTS.md).

Current status (2026-10-30): **frozen (D-022).** The decision-value allocation claim was not demonstrated and is frozen; findings stand as recorded. See [reports/PROJECT_SUMMARY.md](reports/PROJECT_SUMMARY.md) and [reports/latest.md](reports/latest.md).

## Layout
```
src/officeminds/   world (physical state, private minds, observations), tiny scenarios, episodes/replay
src/vomi/          units + defaults + visible-only candidates; exact evaluator with four label records
                   (legacy privileged, privileged-bounded, grounded typed, grounded scalar diagnostic), D_action/D_memory;
                   best-subset reference + D4/STOP; perspective graph + refresh; typed LLM unit schema; audits; client
configs/models/    model/endpoint configs
scripts/           thin entry points (tiny-case labels, model serve, model smoke test)
tests/             invariants and hand-checked scientific constructions (CPU only)
docs/research/     outline, implementation spec, environment, roadmap, baseline fidelity
docs/decisions/    proposed/accepted research decisions + discrepancy log
reports/           milestone reports and review requests
```

## Commands (all run on the workstation; WSL Ubuntu 24.04)
```bash
# CPU-only tests (isolated venv with pytest only; code is stdlib-only, Python >= 3.11)
~/venvs/officeminds/bin/python -m pytest -q
# Exact labels (legacy + grounded) + replayed episodes + review bundle for the tiny cases
~/venvs/officeminds/bin/python scripts/run_tiny_cases.py --seed 0
# D-006 stakes ranking-reversal search (and a per-criterion failure diagnostic)
python3 scripts/search_stakes_reversal.py --samples 1000 --seed 0
python3 scripts/search_stakes_reversal.py --samples 300 --seed 0 --diagnose
# Local backbone: serve gpt-oss-20b with the existing vLLM venv, then smoke test it
bash scripts/serve_local_model.sh
python3 scripts/smoke_local_model.py --config configs/models/local_gpt_oss_20b.json --n 10 --concurrency 4
```
Raw run outputs go to `~/officeminds-runs/` (WSL), outside Git.
