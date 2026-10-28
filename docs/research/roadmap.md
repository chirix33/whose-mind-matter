# Roadmap mapped to claims and research questions

Status legend: ✅ done · 🟡 in progress · ⏳ planned · ⛔ blocked on review/resources

## Claims → RQs → required evidence
| Claim (hypothesis) | RQ | Needs | Status |
|---|---|---|---|
| C1 decision-value allocation improves return at matched compute | RQ1, RQ4 | labels (D-001/2), generator, LLM pipeline, router, groups A–D/F, compute accounting, frontiers | ⏳ (core) |
| C2 VoMI beats entropy / flip / relevance objectives | RQ2 | divergence subset, isolating stakes pairs (D-006), D1–D5 on the same architecture | ⏳ (core) |
| C3 unnecessary modeling harms decisions | RQ3 | LLM records 2/3, hallucination/leakage scoring, length-matched controls; mediation exploratory | ⏳ (core) |
| C4 depth belongs to directed paths | RQ5 | path-asymmetry (F6) cases, B3 baseline | ⏳ (roadmap; tiny case TODO) |
| C5 transfer Tier 1 → Tier 2 → Menti-Bench (320 text items first) | RQ7 | role cards, grounding checker, second family, Mentis adapter | ⏳ (Tier 2 core) |
| theory checks | RQ6 | P1/P2 pruning stats, P3 frequencies, P4 empirical γ (diagnostic only) | 🟡 P1/P3 constructions exist |

## Stages
| Stage | Content | Status |
|---|---|---|
| 0 | repo, outline checksum, environment inventory, spec + open decisions, CPU tests, model smoke | ✅ (this milestone) |
| 1 | tiny cases: depth 0/1/2 ✅, plausible/obvious distractor ✅, substitutes ✅, complementary ✅, stakes pairs ✅ (magnitude only); **TODO:** information-holder permutation as its own visible-scene pair, relevance shift (F3), path asymmetry (F6), stakes ranking-change pair, P2 tests, trajectory-flip labels (D-002), record-B labels (D-001); then balanced generator F1–F6 | 🟡 |
| 2 | end-to-end local pilot (30–50 dev scenario groups): gpt-oss-20b agent; direct, dense, random, oracle diagnostics, simple router | ⏳ needs D-001 |
| 3 | Tier 1 data, ~1–2B controller + feature-only ablation, D1–D5 | ⛔ review of D-001..D-003 |
| 4 | Tier 2 role cards and checker; Menti-Bench adapter | ⏳; second family (Qwen3.6-27B / Gemma-4-31B are present locally but unapproved and untested) |
| 5 | frozen evaluation | ⏳ |

## Calendar reality check (outline §9)
The outline puts "freeze formulation" in the week of Oct 26 and the simulator and generator in Nov 2–9. D-001 and D-002 are formulation decisions, so they are on the critical path now.

## Baseline inventory status (outline §6.2)
| Baseline | Status |
|---|---|
| A1 direct agent | ⏳ planned (Stage 2) |
| A2 long-thinking reasoning model, matched compute | ⏳ planned (gpt-oss reasoning effort is a knob; measure) |
| A3 dense MWM-style (ℓ=1, ℓ=2) | ⏳ planned; style-based adaptation, not Mentis verbatim |
| B1 depth-only (Hedge, A-ToM-style) | ⏳ planned |
| B2 entity-only | ⏳ planned |
| B3 per-person depth | ⏳ planned |
| C1 SimToM-style filter | ⏳ planned (appendix) |
| C2 RecToM-style chain | ⏳ planned |
| D1 entropy controller | ⏳ planned; oracle already computes H(c_u \| c_S) |
| D2 original AutoToM adapted | ⏳ planned; code/license to be pinned |
| D3 flip-probability controller | ⏳ planned; flip notion depends on D-002; tie-break artifact noted |
| D4 relevance classifier | ⏳ planned; target depends on D-003 |
| D5 prompted router | ⏳ planned |
| E1 EgoMAS-style retrieval | ⏳ appendix (first to cut) |
| E2 token-level adaptive reasoning | ⏳ appendix (first to cut) |
| F1 random allocation | ⏳ planned |
| F2 oracle allocation, LLM content | ⏳ planned |
| F3 full oracle | ⏳ planned |
