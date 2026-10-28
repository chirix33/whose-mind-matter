# Review request — 2026-10-28 (Stage 0)

For: the research conversation, via Ashraf. These six decisions block label generation and training. In order of importance:

## 1. D-001 — What should an oracle VoMI label measure? (blocking, most important)
**Problem.** "Fill the unit with its true content, compute ΔQ" (outline §4.3) is implemented exactly, with a Bayes-optimal agent over the raw history. It produces the value of *perfect information about a hidden mind*. In `depth1_knowledge` the robot never saw Alice. Even so:
- the gold label says to model Alice: ΔJ(K(alice)) = 0.125 vs. ΔJ(K(rec)) = 0.05;
- the unique minimal sufficient set is {K(alice)}.

The labels point at absent people whose minds happen to encode the answer. Restricting content to what the history supports doesn't rescue this: a Bayes-optimal agent already uses the history, so every unit would get value 0.

**Alternatives.**
- A. Keep these labels: privileged upper bounds, rewarding uninferable units.
- B. A graph-limited "mind-blind" default policy plus evidence-grounded content. Units license interpreting social evidence (testimony, relayed beliefs). This matches outline §4.1 step 5: the policy decides from "physical state and G_t".
- C. B as the training target, A kept as a reported bound.

**Recommendation: C.** It needs a ruling on how a mind-blind policy treats heard testimony. The proposal: uninformative until K/R units license it. The alternative: face value, with units only correcting it.

**Evidence.** `docs/decisions/2026-10-28-D001-label-policy-class-and-content.md`, `reports/tiny-cases.md`, `tests/test_oracle.py`.

## 2. D-002 — Does instantiated content persist? (blocking for RQ2/P1)
Under graph retention, a unit can be valuable without changing the current action. `depth2_handoff` K(alice): P(flip) = 0, ΔJ = 0.05. So the outline's §3.4 decomposition and the P1 pruning test fail as stated.

**Recommendation:** keep retention, and restate the flip in terms of the **trajectory**. The identity then holds exactly. Step-level flips remain the D3 baseline's target, and the residual is reported as value a one-step flip detector cannot see.

Evidence: `docs/decisions/2026-10-28-D002-continuation-semantics.md`.

## 3. D-003 — Gold-allocation definition
The outline's "removal changes the action" gives an **empty** gold set in `substitutes`, where four units are each sufficient and each worth 0.05.

**Recommendation:** score precision and recall against the set of minimal sufficient sets, with tolerance for equivalent sets. Wasted and missed units are defined by conditional ΔJ. D4's target is the union of minimal sufficient sets.

Evidence: `docs/decisions/2026-10-28-D003-gold-allocation-definition.md`.

## 4. D-004 — Ontology
Recommendation: "mistaken" = cooperative + false belief, not a third intent. Questions: should obstructive people lie deterministically or strategically? Should R(j→k) be in core scope?

## 5. D-005 — Tier 1 mechanics
Confirm the irreversible-error mechanics (wrong chute drop, mis-routed handoff), the −0.05 charge on the terminal step, and no timeout penalty.

## 6. D-006 — Stakes pairs
Naive ×4 penalty pairs can change flip probability too (0.05 → 1.0 at q = 0.95).

**Recommendation:** keep only numerically verified isolating pairs for the P5 subset, and report the rest separately. Also: the current isolating pair shows a change in VoMI *magnitude* only, not a ranking change between units. A ranking-change construction is still to be built.

---
**Also for awareness (no decision needed yet):**
- Local Qwen3.6-27B and Gemma-4-31B checkpoints exist. A second family for Tier 2 needs approval and a serving test.
- With the gpt-oss-20b server up, the GPU is at about 29.3 of 32.6 GB, so the role-player and controller must run sequentially.
