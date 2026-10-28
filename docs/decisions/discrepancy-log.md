# Discrepancy log (outline v2 vs. AGENTS.md vs. implementation)

Each row records where sources disagree or where the implementation had to narrow an ambiguity. A row closes only with a reviewed decision.

| # | Outline § | Outline says | Conflict / ambiguity | Current handling | Decision |
|---|---|---|---|---|---|
| 1 | §3.3 | "Q* is the true action value, which the simulator can compute" | AGENTS §5.2: don't call it Q* unless solved exactly. A fully informed oracle and an observation-limited agent differ | implemented as observation-limited belief-optimal values (exact under the model); full-information value reported separately as a privileged bound | D-001 |
| 2 | §4.3 | oracle-content VoMI is "symbolic and cheap" | AGENTS: three distinct records; oracle content given to an *LLM* needs real LLM calls. Also, with true content the label is perfect-information value about uninferable minds | only record 1 (exact symbolic) implemented; labeled as such | D-001 |
| 3 | §3.4 / §3.5 P1 | VoMI = P(flip)·E[ΔQ|flip] − λc; no flip ⇒ −λc | fails when instantiated content persists (retain): value without a first-step flip | both continuation modes implemented; residual reported | D-002 |
| 4 | §5.4 | gold = "minimal set whose removal changes the oracle action" | ambiguous; non-unique; empty under substitutes | minimal-sufficient, minimum-cost, LOO-value, LOO-action all computed | D-003 |
| 5 | §5.1 | intent types: cooperative, mistaken, obstructive | AGENTS: separate stable intent from statement correctness | mistaken = cooperative + false belief | D-004 |
| 6 | §3.5 P5 | scaling the penalty leaves flip and entropy rankings unchanged | AGENTS: conditional; counterexample at q = 0.95 (P(flip) 0.05 → 1.0) | isolating pairs filtered numerically | D-006 |
| 7 | §3.5 P4 | greedy ≥ (1−e^{−γ}) of optimum | AGENTS: needs stated set-function assumptions; pure complements give γ = 0 (seen in `depth2_handoff`) | not implemented; no claim | — (theory TODO) |
| 8 | §4.1 | depth-2 precondition "recorded co-presence, communication, or a relayed message" | must be robot-visible; hidden co-presence leaks | visible co-presence or an utterance naming the other | spec §5.2 |
| 9 | §5.5 | Menti-Bench 448 items | AGENTS: first milestone uses the 320 text items | staging only; reports must state the subset | AGENTS (authorized) |
| 10 | §6.3 RQ3 | mediation analysis | AGENTS: exploratory unless a causal design is reviewed | to be labeled exploratory | AGENTS (authorized) |
| 11 | §5.5 | ≥ 400 paired episodes "should resolve ~5 points" | AGENTS: confirm by pilot power analysis | pending pilot | — |
| 12 | §4.1 step 5 | policy chooses a_t "from the physical state and G_t" | current exact oracle uses the full raw history h, not only G_t | the motivation for D-001 option B | D-001 |
