# D-001 — Policy class and content semantics for VoMI labels

- Status: **proposed** (awaiting research review)
- Date: 2026-10-28
- Affects: outline §3.3, §4.3 (oracle-content labels), §5.4 (gold labels, certification); AGENTS §5.2; `vomi/oracle.py`
- Blocks: any bulk label generation and controller training

## Problem
The outline's oracle-content label "fills each candidate with its true content from the simulator." With the current implementation (a Bayes-optimal agent over raw history h, plus true content), that label is the **value of perfect information about a hidden mind**. It is not the value of *modeling* that mind from the evidence the robot has.

Evidence, from the exact tiny cases (`reports/tiny-cases.md`, run `tiny-20261028-031743-88659e`):
- `depth1_knowledge`: the robot never saw Alice, so nothing in h supports inferring Alice's mind. Yet ΔJ(K(alice)) = 0.125 > ΔJ(K(rec)) = 0.05, and the unique minimal sufficient set is {K(alice)}. The label says "model the absent person who holds the answer". The reason is that the true content of Alice's belief *is* the hidden target.
- The same happens in `distractor_plausible` (ΔJ 0.1125), `distractor_obvious` and `substitutes`.
- The flip side: if content were restricted to what h supports, a Bayes-optimal agent over h *already* conditions on h. So every unit would have ΔJ = 0. Under this policy class, record-1 labels can only measure information the robot does not have.

A controller trained on these labels would learn to instantiate people whose minds are uninferable from h. That conflicts with AGENTS §5.2 ("include history-ambiguous examples so the controller is not expected to recover unknowable private facts perfectly") and probably creates hallucination pressure, the C3 mechanism.

## Alternatives
**A. Keep the current labels (Bayes-optimal over h, true content).**
- For: simple; the outline's literal reading.
- Against: labels are privileged VPI upper bounds. They reward uninferable units. Realized labels (~15% of states) must correct the bias, which they may not do at that coverage.

**B. Graph-limited policy plus evidence-grounded content (recommended).**
- The label policy sees only the physical/visible state and task. Mental information enters **only** through instantiated units. This matches outline §4.1 step 5: "the policy chooses a_t from the physical state and G_t".
- Unit content is what a specified symbolic inference rule concludes from the robot-visible evidence, e.g. "rec was seen in the hall when Alice walked by ⇒ rec believes alice_loc = x". When evidence underdetermines it, the content is the posterior distribution over the person's state given h (or `unknown`).
- VoMI then measures the decision value of *performing* that inference. That is the quantity the router allocates.
- True content is still used to score inference error (realized labels) and for bounds.

**C. Both, kept as distinct records.**
- B is the training target.
- A is reported as a privileged "perfect-mind-information" bound and for analysis (e.g. the F3 full-oracle bound).
- Cost: roughly 2× label compute. That is negligible for symbolic Tier 1.

## Recommendation
**C, with B as the training/gold target.** B is well defined only after two sub-choices are fixed:
1. **The mind-blind default policy (S = ∅).** Proposal:
   - It is Bayes-optimal over *physical* hypotheses, using physical observations: rooms, who is present, outcomes.
   - It treats heard utterances as uninformative about physical facts. Interpreting testimony ("rec said alice_loc = A" ⇒ Alice is probably in A) is what K and R units license: K(rec) says whether rec's belief is informed, R(rec) whether her statements track her belief, and K(j→k) supports reasoning about relayed or second-order beliefs.
   - Each instantiated unit adds exactly the conditional structure for its person and variable.
2. **The evidence-grounded content rule.** The exact posterior over the person's mental variable given h, computed by the same replay filter. It needs no extra assumptions and is computable exactly.

## Consequences
- The oracle gains a second policy class. Information still cannot hurt a Bayes-optimal policy, so record-1 VoMI is still ≥ −λc, and C3 harm still has to come from LLM records (2 and 3).
- Value now flows from *interpreting social evidence*, which is what the router allocates. A person with no visible evidence (Alice in `depth1_knowledge`) gets ≈ 0 value. The receptionist, whose answer must be interpreted, gets positive value.
- Depth certification becomes relative to the graph-limited class. That is arguably the class the paper is about.
- Every tiny-case expectation must be re-derived by hand before switching. The current tests stay as the record-A regression suite.
- The definition of "mind-blind" is itself a modeling choice. A reviewer can ask why literal testimony is not physical evidence. The alternative is to let the default policy take testimony at face value and have units only *correct* it. That gives negative-free but differently shaped labels. Either way, it must be fixed explicitly.

## Minimal example
`depth1_knowledge` (rec saw Alice with probability ½; the robot saw nothing about Alice):
- Record A (current): ΔJ(K(alice)) = 0.125 and ΔJ(K(rec)) = 0.05, so the gold set is {K(alice)}.
- Record B: the evidence-grounded K(alice) is the prior, so ΔJ ≈ 0. The mind-blind policy walks (0.80). With K(rec) ("rec's belief is truthful-if-informed, informed with probability ½") it can ask and use the answer (0.825), so ΔJ(K(rec)) ≈ 0.025. Here the gold set points at the receptionist, as the outline's hook intends.

(The B numbers are hand estimates under the proposed rule. They are not implemented yet.)

## Review outcome
_(pending — record the decision supplied by Ashraf here)_
