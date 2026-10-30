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
| Fallback freeze (`fallback-freeze.json`) | done, commit `b42589d` |
| Fallback pilot (1,536 episodes) | done: `~/officeminds-runs/hybrid/hybrid-fallback-20261029-233643-d93b61`, 1,503 s, 0 errors |
| Report + FINAL_REVIEW | done: `FINAL_REVIEW.md`. **Block complete; awaiting research review** |

**Serving log (WSL clock):**
- vLLM started 2026-10-29 about 23:34:50; ready 23:35:40.
- Smoke 23:35:46–23:36:01.
- Pilot 23:36:43 to 00:01:46; server stopped at about 00:02 (total about 27 min of serving).
- Stop the server with `pkill -f "vllm serve"` in WSL.

**D-020 (2026-10-30):** audit and export delivered in `audit/` (`AUDIT.md`, `HASHES.sha256`). No model calls. vLLM stopped.
