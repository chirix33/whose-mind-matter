# D-023: Authorize one bounded CPU-only G1 check, with amendments

- Status: **accepted**. Ashraf supplied the research recommendation in the implementation session on 2026-10-30 (the pasted research-driver text). It reverses D-022's freeze **for this one check only**.
- Supersedes D-022 only in that one bounded G1 evaluation is authorized. The allocation claim otherwise stays frozen.

## Binding amendments
1. **Stronger cheap selectors.** Besides "read every conversation involving R or F", include:
   - "read the latest relevant update";
   - an action-specific provenance rule;
   - a simple rule using recency, change probability and stakes.

   If such a rule matches decision-value selection, that is a meaningful stopping result.
2. **Perspectives must matter.** Include paired cases where changing who heard which message changes the best read while the physical situation stays fixed. State that provenance establishes *alignment*; it does not necessarily reveal F's belief value.
3. **Freeze the complete experiment before measuring:** generator, parameter ranges, task reuse, seeds, baselines and resource accounting.
   - Include sparse and dense relevance conditions.
   - Conversation rates are not adjusted afterwards.
4. **Judge outcomes, not selection disagreements.**
   - Report return and reads against every baseline, with ties handled explicitly.
   - U in (0.35, 0.60] is **not** a pass.
   - STOP frequency is defined over comparable initial decision states.
5. **Narrow authorization.**
   - One frozen evaluation pass; at most one CPU day.
   - No model calls, spending, text-environment construction or automatic progression to G2.
   - Failures and inconclusive results are reported without revising thresholds.
6. **What a pass would mean.** Passing G1 establishes a promising symbolic setting. It does not establish a successful method, novelty, a paper, or that real text extraction is expensive.
7. **G2's 1,000-token floor is withdrawn.** Any later G2 measures the cheapest reliable extraction approach instead.

Protocol: `reports/g1/G1_PROTOCOL.md`, frozen and hash-pinned in `reports/g1/g1-freeze.json` before any measurement.
