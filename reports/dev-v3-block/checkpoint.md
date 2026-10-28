# dev-v3 block checkpoint

**Block complete (2026-10-28).** The stopping rule from D-014 ("return after these two rounds") is met.

- **Round A:** complete and gated; frozen at `7871e4c`, committed in `984cb50`.
- **Round B:** local run `dev-v3-notes-20261028-165208-67f601` is complete and gated (Opus PASS WITH REQUIRED CHANGES, applied; Sonnet reproduced the numbers, and its discrepancies are fixed). The B2 API batch was not run: its estimated cost exceeds the 0.80 allowance, and this is recorded as a deviation.
- **Spend:** no paid calls in this block. The ledger reads USD 3.8690 of 5.00, with 0 reservations and 0 unresolved.
- **Services:** the vLLM server is stopped. No cloud sessions were used.
- **Resume:** nothing is pending. The next step is the research review of `FINAL_REVIEW.md` → "Decisions for the research review". Do not rerun Round B, and do not tune on its outcomes.
