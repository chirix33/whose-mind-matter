# Review request — 2026-10-28 (Stage 2 pilot results)

Full write-up: `reports/pilot/pilot-report.md`. Bundle contents:
- `reports/bundle/`: pilot manifest and summary, three diagnostic traces, the earlier symbolic bundle;
- `reports/pilot/dev-v2-manifest.json` and `dev-v2-freeze.md`;
- `prompts/pilot-v1/` and `src/vomi/unit_schema.py`;
- input-check reports;
- a source archive.

The pilot's purpose was to see whether the task elicits meaningful mental inference, and whether selective computation has usable signal at affordable overhead.

## Findings that need a decision
1. **On average, explicit typed units hurt or tie the direct LLM.** Mean return per instance vs. direct:
   - dense −0.051, random −0.058, router −0.068;
   - symbolic-reference allocation +0.019, using 0.5 units per episode and 15% token overhead.
2. **Unit content is often unsupported.** The LLM asserts specific beliefs when the truth is `unknown` (K(j) top = truth 0.43, even at top-p ≥ 0.8), and the policy acts on them. That produced the largest losses (one irreversible error at ×4 stakes).
3. **Retained state helps in the carryover family:** +0.225 vs. +0.037, with n = 8.
4. **The prompted router does not track the symbolic reference:** Jaccard 0.38; it STOPs in only 11/40 symbolic zero-value instances. Its own call costs more tokens than the units it buys.

## Questions
**Q1. Is the unit failure mode a prompt/schema issue worth one documented revision before any label generation?**
- Proposal: a unit-prompt revision `pilot-v2`, rerun on the same frozen `dev-v2` set, reported as pre/post revision, with no scenario changes. Two concrete changes:
  - require each non-`unknown` hypothesis to cite a supporting evidence ID;
  - add a validator rule that rejects confident (> 0.5) non-unknown hypotheses without such a citation.
- Alternative: treat current fidelity as the realistic baseline and proceed.
- **Recommendation:** one revision. Without it, any learned router would be trained to buy units whose content is unreliable, which makes C1/C2 untestable.

**Q2. Proceed toward training labels and a small learned controller?**
- **Recommendation: not yet.** First establish, on dev data, that some allocation beats direct after the Q1 revision. The symbolic-reference tie at low overhead is the only positive allocation signal.
- If Q1 does not raise typed-unit fidelity, the next step should be the RQ3-style over-modeling intervention (dense vs. selective vs. direct), since unsupported attributions are what the pilot most clearly shows.

**Q3. Should the fidelity taxonomy be split now (false vs. unsupported vs. leaked attribution), to report RQ3-relevant counts in the next pilot round?**
- **Recommendation:** yes. It is cheap (privileged scoring of existing outputs), and it separates "value instead of unknown" from "wrong value".

**Q4. Router baseline:** keep the single zero-shot router as the D5 seed, or give it a few-shot variant at equal budget?
- **Recommendation:** add a few-shot variant only after Q1, so router and unit changes are not confounded.
