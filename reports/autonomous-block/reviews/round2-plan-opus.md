# Round 2 plan gate: Opus 5.5 scientific-validity review

- **Reviewer:** sub-agent, model opus (Opus 5.5).
- **Method:** read-only; no API calls; the ledger was not touched. It rendered all 36 t0 policy prompts with a throwaway script and no client. Commit `2287ad3`.
- **Verdict:** PASS WITH REQUIRED CHANGES.

## Design and leakage
- **Design matches brief §6:** 4 conditions, payloads frozen before policy calls, 3 replicates reusing them, counterbalancing verified (each condition appears 6–7 times in each dispatch position; 108 unique jobs), allocation disabled, no refresh under fact_only, note cost kept separate, no client-side cache.
- **Leakage:** none found in the none, inferred or reference conditions.
  - `source` is never rendered; evidence IDs are empty; `about` is public.
  - The oracle conditions only on the visible history.
- **Indirect channel:** the reference uses the family-specific generator prior.
  - s3 equals truth at 1.0 (renders like the privileged note; legitimate).
  - s2, s6 and s7 put 0.95 / 0.975 / 0.867 on the truth through undisclosed base rates.
  - The other five states are 0.5/0.5.

## Required changes, all done before any Round 2 output (see the plan amendment)
1. **Blocking:** `REV = 4` in the runner; must be r5. → Fixed, with an r5 marker assert on every request.
2. **Pre-declare reference strata** {s3} / {s2, s6, s7} / {s1, s4, s5, s8, s9}, and amend the mapping. → Done.
3. **The presentation confound is larger than declared** (support, cited evidence, excerpts, unresolved items, model-chosen status). → Added the `inferred_bare` condition.
4. **The 'reliable' criterion** was biased toward 'not reliable' and fragile to single draws. → Replaced; added label and stratum breakdowns, a drop-one-draw check and per-state success/error counts.
5. **Budget enforcement and missing data.** → Stage cap set through `OFFICEMINDS_API_CAP_USD`; exceptions recorded as `blocked`; complete-layer analysis rule.
6. **Freeze provenance.** → Commit, dirty status, timestamps, USD and rendered-note hashes; tracked proof file committed before the policy stage.

## Optional items, adopted
- Rendered-note hashes.
- Residue applied to the largest mass, with an assert that every p ≥ 0.
- Fallback note text recorded.
- Extra contrasts, replicate SD and first-action change.
