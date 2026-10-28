# Autonomous block — pre-registered experiment plan

Each entry is written before the round's new outputs are inspected. Brief: `AUTONOMOUS_RESEARCH_BRIEF.md`.

**Execution environment (recorded once):** local workstation (WSL Ubuntu 24.04, RTX 5090, local vLLM serving gpt-oss-20b; OpenAI Responses API for gpt-6.1-sol).
- Cloud sessions are not used. The API key, the authoritative spend ledger, the gitignored frozen data and the GPU are all on this machine.
- A cloud session would need them published or copied, which this block forbids.
- Billable jobs run one process at a time, under the file-locked ledger.

**Review gate (Ashraf, 2026-10-28):** two reviewer sub-agents check each round. Opus 5.5 checks scientific validity; Sonnet 5.5 independently recomputes the reported numbers from raw artifacts. A round's conclusion is recorded only after both pass; unresolved disagreements are logged for the research conversation.

---

## Round 1 — contract and uncertainty package (declared 2026-10-28, before any r4 / pilot-v2.1 output)

**Question / hypothesis**
- **H1a (contract):** stating the simulator's actual belief contract (r4 rules) removes the known conflicts between the public wording and the scoring reference (uc14, uc16; and the recipient-self-location cases uc04, uc05, uc21, uc24 that r3 left undisclosed).
- **H1b (package):** pilot-v2.1 separates "the person has no belief", "the robot is unsure" and abstention. Against pilot-v2 under the same r4 contract, it should cut abstention on resolvable contexts without increasing committed unsupported content.
- **H1c:** do the package differences hold on both the local and the API model?

**Change from the preceding version**
1. Renderer r4: a numbered people-rules paragraph replaces the r3 paragraph for every arm and package. Each clause is tested against the simulator (`tests/test_r4_rules.py`, 8 tests, all dev-v2 instances).
   - A self-location clause is included only in the scope the tests establish (the recipient, at the start; movement updates no one).
   - Re-rendering at r3 reproduces the frozen r3 requests exactly, so the rules paragraph is the only request change for pilot-v1/v2.
2. Package pilot-v2.1 (new `prompts/pilot-v2.1/unit_system.txt`; schema/validator `unit_output_schema_v21` / `validate_unit_output_v21`):
   - statuses `grounded` / `uncertain` / `abstain`;
   - support may cite a numbered rule (`RULE<n>`, kind `public_rule`).
3. Scoring v3 (`score_output_v3`):
   - one category per output, partitioning n: invalid, abstained, ambiguous_reference, correct_supported, correct_unsupported, incorrect_supported, leakage, unsupported_committed (top p ≥ 0.5), unsupported_hedged (top p < 0.5);
   - a total-variation distance to the reference.
4. Reference audit (`reports/autonomous-block/reference-audit.json`, written before outputs):
   - 5 contexts are ambiguous: uc02, uc06 and uc07 (undisclosed base rates); uc10 and uc11 (undisclosed R(j→k) template);
   - 19 are consistent under r4.
5. Ledger: file-locked and cross-process, with ambiguous transport failures kept charged. This is a bug fix and is not a method variant.

**Configurations and data/context IDs**
- Contexts: `reports/autonomous-block/unit-contexts-v1-r4.jsonl` (sha256 `e8e0dfd5…2ff8`), the same 24 contexts uc01–uc24 as `unit-contexts-v1`, with histories verified identical.
- Local: gpt-oss-20b, effort low, temperature 0, 4,096 output tokens, concurrency 1. Packages pilot-v1, pilot-v2, pilot-v2.1 (72 requests).
- API: gpt-6.1-sol, effort low, provider-default sampling (single draw), concurrency 1. Packages pilot-v1, pilot-v2, pilot-v2.1 (72 requests).
  - The output cap is cut to 6,000 tokens (from 16,000) to bound the runaway-output failure seen once (about $0.16 at 16,000). Measured mean output was 334–828 tokens, so the cap should not bind on normal outputs.
- Comparison rows, already run under r3 and not re-run: local low/medium and API low, pilot-v1/v2. They are rescored with v3 and labeled r3.

**What stays fixed**
- Contexts, histories and units.
- The reference posterior and the ambiguity flags.
- Per-model decoding (except the API output cap above) and the failure protocol (3 attempts).
- Frozen dev-v2 and unit-contexts-v1.

**Metrics, denominators, inclusion rules**
- Per cell, the v3 category counts partition n = 24. They are reported in two blocks:
  - **primary:** the 19 consistent contexts;
  - **ambiguous:** the 5 flagged contexts.
- Coverage = attributed / 24.
- Proper scores: log score vs. truth (1e-3 floor), Brier, CE vs. posterior and TV vs. posterior, over all valid outputs (abstentions included through their distributions). Repeated over attributed outputs only.
- "Hallucination-type content" means unsupported_committed + leakage. unsupported_hedged and incorrect_supported are not counted.
- Package effect: paired Δ on the same contexts, same model and same r4 contract.
- Contract effect: the same package and model at r4 minus r3. This is a combined rules effect, never called a prompt effect.
- The API r4 rows use a different output cap from the API r3 row; that cap change is reported with the contract comparison.
- All failed or invalid outputs stay in the denominators as `invalid`.

**Expected cost and maximum allocation**
- Local: free (GPU time only).
- API: 72 requests at about $0.003–0.005 each, so about $0.25–0.35.
- Maximum allocation **$0.60**, which covers retries and up to 4 runaway attempts at the 6,000 cap (about $0.06 each).
- The ledger's worst-case reservation per request is about $0.064.

**What each outcome would imply**
- **pilot-v2.1 is used as the inferred-notes package in Round 2 whatever its relative score** (the brief's "revised package"; no winner-picking). The one exception: if its API invalid rate is above 10%, Round 2 uses pilot-v2 at r4, and this is recorded.
- If coverage rises (abstained ≤ 6/24 on API) and committed unsupported content does not increase relative to pilot-v1, the uncertainty package works as intended.
- If v2.1 still abstains on most contexts, or replaces abstention with committed unsupported content, inference quality is a likely bottleneck. Round 2's grounded-reference condition then tests whether better content would matter.
- If r4 changes pilot-v1/v2 outputs at uc14/uc16 toward `unknown`, the contract repair reached the model. If not, the earlier errors were not caused by the wording alone.

**Post-declaration changes (disclosed)**
- *Scoring v3.1 tie rule, found after inspecting the Round 1 local outputs.*
  - **The bug:** when several values share the top probability, v2 and v3 picked the "top" value by JSON list order. The same 0.5/0.5 output could therefore be scored correct or incorrect. Examples: uc01 vs. uc24, local v2.1.
  - **The fix:** a supported tied value is preferred over an unsupported one. When the truth is among the supported tied values, the new category `supported_spread` applies, not a top-1 hit. When all tied values are unsupported, the tie does not change the category.
  - **Scope:** the rule applies identically to every row, old and new, and the old categories stay reconstructible from the raw records.
  - **Effect:** it moves some outputs between "correct" and "incorrect"/"spread" in every cell. It does not use outputs selectively.
- *Reference-audit wording* (uc01, uc10, uc11): corrected after the Sonnet facts check. No flag changed.

**Plan-gate outcome and amendment** (2026-10-28; Opus gate: PASS WITH REQUIRED CHANGES; review in `reviews/round1-plan-opus.md`)
- *Timing disclosure:*
  - The local r4 cells (run `unit-contexts-20261028-083007-1512c0`) ran after the plan commit `03a52c1` but **before** the gate returned. The checkpoint had said the gate came first.
  - The v3.1 tie rule came after those outputs.
  - The Opus reviewer read `round1-results.md` and some local v2.1 records, but only to confirm defects it had already found in the code.
- *Amendment A, before any API output in this block: rules r5 replace r4.*
  - The r4 clause tests checked only realized draws. Over the full prior support, which the reference averages over, rule 5 was false in two cases: backstory updates passed on as claims (directed-perspective `heard_told` worlds), and distrusting listeners.
  - r5 scopes rule 1 to before the task, rules 2 and 3 to during it, and qualifies rule 5. Rule numbering is unchanged.
  - Every clause is now tested over **all positive-prior worlds** (`tests/test_r4_rules.py`, 9 tests).
  - The remaining Round 1 cells (local and API, all three packages) and all of Round 2 use r5: `reports/autonomous-block/unit-contexts-v1-r5.jsonl`, sha256 `bb7835eb…eee8`, same 24 contexts.
  - The local r4 run is kept and reported as a superseded contract.
  - No reference or flag changes. uc15 stays consistent because rule 5 was qualified, not dropped.
- *Amendment B, analysis (items 3–6):*
  - **H1b is judged on the status-agnostic content category and on CE/TV over the 19 consistent contexts.** Status-based coverage is reported separately.
  - Unsupported mass is reported per output and per cell. The committed/hedged categories stay as declared, with the limitation stated.
  - Proper scores are reported for the 19 consistent contexts separately.
  - The API r3 → r5 comparison is labelled "rules + output cap + fresh sampled draw (descriptive only)".
  - The Round 2 fallback threshold now reads "≥ 3/24 invalid on API".
- *Pinned revisions:* every runner records the render revision it used (`render_revision` in its manifest). The global default is now r5 for new runs only.
