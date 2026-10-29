# Repair block checkpoint (D-015)

**Block complete (2026-10-29).** The stopping rule from D-015 ("return after this block") is met.

- **Stage 1:**
  - The package revision pilot-v2.2.
  - The regression check.
  - Freeze `27c324e`.
  - Gates (all passed): plan; prompt and renderer; Stage 1 results (Opus, Sonnet).
- **Stage 2:**
  - Run `repair-stage2-20261029-132459-743ace`: 288 base scenarios, 4,032 episodes.
  - Gates: Opus PASS WITH REQUIRED CHANGES, applied in the summary; Sonnet CONSISTENT.
  - Pre-declared outcome: §5(3).
- **Spend:** no paid calls; the ledger stays at USD 3.8690.
- **Services:** the vLLM server is stopped. No cloud sessions were used.
- **Resume:** nothing is pending. The next step is the research review of `FINAL_REVIEW.md`.
  - Seeds 20261100–20261123 are inspected development data.
  - Do not tune anything on the Stage 2 outcomes.
