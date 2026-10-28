# Review request — 2026-10-28 (pilot model diagnostic)

Write-up: `reports/pilot/model-diagnostic.md`. Supporting files:
- `reports/pilot/unit-contexts-results.md` (generated table and per-context outputs);
- `reports/pilot/unit-contexts-audit.md` (10-context evidence audit, readable extracts);
- `reports/pilot/unit-contexts-v1.jsonl` (the exact frozen request payloads);
- D-013.

All local cells ran. **All API cells are blocked:** the key now loads from the repo `.env`, but the OpenAI account has no credits. No paid call was made.

## Needed from Ashraf (not a research question)
- The key is configured (repo `.env`), but the OpenAI account has no credits (HTTP 429 `credit_balance_exhausted`). Add credit; the cap stays USD 5 unless `OFFICEMINDS_API_CAP_USD` is set. The estimated spend for all API cells is about USD 1.4–2.9 (illustrative).

## Q1. The scoring reference conflicts with the r3 public rules (audit uc14, uc16)
The simulator creates nested beliefs only through tell/claim/assert events. Statements people overhear (`say` events) update no one, yet the r3 rules say listeners "learn what was said". The evidence posterior therefore scores some publicly reasonable nested attributions as unsupported.

**Options:**
- **(a)** Clarify the public rules: "hearing a statement tells you what the speaker claimed, but people do not form beliefs about others' beliefs from casual remarks." This is a shared interface revision r4, rerun for all cells.
- **(b)** Keep the rules, and score nested units against a public-rules-consistent reference (a scoring change).
- **(c)** In a new dev version, give the simulator nested updates from `say` events (a world change; frozen sets untouched).

**Recommendation: (a).** It is the smallest change, it keeps the frozen worlds, and it makes the contract explicit. It would also add "everyone knows where they themselves are", the most common substantive miss (3/10).

## Q2. Over-abstention in pilot-v2
pilot-v2 abstains on 12–14 of 24 contexts, including ones the evidence settles, and still puts mass on "unknown" inside abstentions.

**Recommendation:** do not tune the package further before the API comparison shows whether this is a model or a package limit. If needed later, a single documented v2.1 revision.
