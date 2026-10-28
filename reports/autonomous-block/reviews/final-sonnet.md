# Final gate: Sonnet 5.5 independent numbers check (Round 3 + block totals)

**Verdict:** CONSISTENT, with presentation nits only. Commit checked: `8250247`. The reviewer used its own scripts on the raw episodes, payloads and freeze proofs.

## Round 3
- **Integrity:**
  - 112 episodes and 28 cells, each with replicates 0–3; 0 blocked.
  - 0 injected-hash mismatches. Payload hashes recompute.
  - reference_doubt = reference × 0.8 + 0.2 unknown with the status copied (max rounding difference 4e-5).
  - Rendered hashes at s1 and s9 equal Round 2's inferred_bare.
- **round3-results.md:** every number reproduced (s9 counts, H3a/H3b/H3c verdicts, H3c mean −0.03125 with 3 negative and 1 positive state, per-state and group tables, replication and cost tables). Policy spend is 0.913026.
- **Nit:** at s6 the reference first actions are split 2/2, so the "differs from modal" column depends on a tie-break → disclosed.

## Block totals
- Token-based spend:

  | Item | USD |
  |---|---|
  | Round 1 API | 0.544626 |
  | Round 2 notes | 0.061016 (= freeze delta) |
  | Round 2 policy | 1.03794 |
  | Round 3 policy | 0.913026 |
  | **Sum** | **2.556608** |

- The ledger reads 3.86895 over 1,114 calls, with no reservations and 0 unresolved; 1.13105 remains.
- **Nits:** the rounded components sum to 2.5565, not 2.5566, and the ledger strictly rounds to 3.8689 → both disclosed.

## FINAL_REVIEW claims
- Verified:
  - 8 of 9 states succeed under `none`;
  - s9 0/14 (none 0/7 + reference 0/7; also privileged 0/3, inferred 1/3);
  - doubt 10/11 (3/3 + 7/8).
- The "+29% tokens" figure is the Round 2 inferred condition, per episode. Part of it is more steps: per call it is +16%. In Round 3, reference_doubt is +18% per episode and reference −12% → qualified.
- The registry is complete for all block runs, and all 5 manifests are present.
- The evidence CSVs (135 / 112 rows) match the jsonl, with no hidden-state columns.
