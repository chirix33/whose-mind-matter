# Hybrid block (D-019) checkpoint

Resume point after a restart: read this file first.

| step | state |
|---|---|
| D-019 registered (decision record, AGENTS pointer, repo copies) | done |
| Common foundation: `relational.py`, `hybridfam.py`, tests | done; 318 tests pass |
| CPU gate (`cpu-gate.md`) | done. Foundation sound; hybrid selection economics fails, so fallback |
| Fallback trigger audit (`trigger-audit.json`) | done; opportunity present |
| Token forecast (`token-forecast.json`) | done |
| Smoke probes (48 of 96; `smoke.jsonl`) | done; 48/48 parsed; no changes made |
| Fallback freeze (`fallback-freeze.json`) | next |
| Fallback pilot (1,536 episodes) | pending. Run dir under `~/officeminds-runs/hybrid/`; resume with `--resume DIR` |
| Report + FINAL_REVIEW | pending |

**Serving log (WSL clock):**
- vLLM started 2026-10-29 about 23:34:50; ready 23:35:40.
- Smoke 23:35:46–23:36:01.
- Stop the server with `pkill -f "vllm serve"` in WSL.
