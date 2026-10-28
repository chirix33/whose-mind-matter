# dev-v3 block checkpoint

**Round A: complete.**
- Plan gate: Opus PASS WITH REQUIRED CHANGES R1–R15, applied as Entry 1a.
- Results gate: Opus PASS WITH REQUIRED CHANGES RC1–RC4, applied as Entry 1b; Sonnet CONSISTENT.
- Freeze: `dev-v3-freeze.json` from clean commit `7871e4c`. `run_dev_v3_notes.py verify` passes.
- No LLM had touched dev-v3 before the freeze commit.

**Round B: next.** Local gpt-oss-20b.
1. Freeze the notes (`notes`), then render (`render`).
2. Run the policy for 3 replicates (`policy`).
3. Report (`scripts/report_dev_v3.py`).
4. Opus and Sonnet results gates.
5. Optional B2 API batch, under Entry 1a R12.

**Spend:** no paid calls in this block so far. The ledger still reads USD 3.8690 of 5.00; reconcile it before any B2 call.
