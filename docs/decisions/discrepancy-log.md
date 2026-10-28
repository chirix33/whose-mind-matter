# Discrepancy log (outline v2 vs. AGENTS.md vs. implementation)

Each row records where sources disagree or where the implementation had to narrow an ambiguity. A row closes only with a reviewed decision. "Accepted" means the Stage 0 research review (2026-10-28) supplied the outcome; see each D-00x record.

| # | Outline § | Outline says | Conflict / ambiguity | Current handling | Decision |
|---|---|---|---|---|---|
| 1 | §3.3 | "Q* is the true action value, which the simulator can compute" | AGENTS §5.2: don't call it Q* unless solved exactly; a fully informed oracle and an observation-limited agent differ | `Q_ref` = realized return under a fixed, observation-limited continuation of a *specified actor*; the evaluator enumerates worlds; the full-information value is a separate privileged bound | **D-001, D-002 accepted** |
| 2 | §4.3 | oracle-content VoMI ("fill each candidate with its true content") is the training signal; "symbolic and cheap" | perfect hidden content rewards uninferable minds (legacy K(alice) 0.125 in depth1) | kept only as the *legacy privileged perfect-content reference*; main target = grounded bounded-policy value | **D-001 accepted (option C, constrained)** |
| 3 | §3.4 / §3.5 P1 | VoMI = P(flip)·E[ΔQ\|flip] − λc; no flip ⇒ −λc | fails with retention | retention kept; VoMI_retained = D_action + D_memory; P1/P2 apply to D_action only; carryover labeled | **D-002 accepted (modified)** |
| 4 | §5.4 | gold = "minimal set whose removal changes the oracle action" | ambiguous; non-unique; empty under substitutes | value-preserving sufficiency; one matched gold set per prediction; D4 = conditional relevance plus STOP | **D-003 accepted (revised)** |
| 5 | §5.1 | intent types: cooperative, mistaken, obstructive | AGENTS: separate stable intent from statement correctness | mistaken = cooperative plus false/outdated belief (derived slice); R(j→k) kept in core | **D-004 accepted** |
| 6 | §3.5 P5 | scaling the penalty leaves flip and entropy rankings unchanged | conditional; counterexample at q = 0.95 | isolating pairs verified numerically; general pairs reported separately; ranking reversal searched (see latest.md) | **D-006 accepted** |
| 7 | §3.5 P4 | greedy ≥ (1−e^{−γ}) of optimum | needs set-function assumptions; pure complements give γ = 0 (grounded `nested_reliability` pair) | not implemented; no claim | — (theory TODO) |
| 8 | §4.1 | depth-2 precondition "recorded co-presence, communication, or a relayed message" | must be robot-visible | visible co-presence or an utterance naming the other; R(j→k) also needs visible reliability evidence about k | spec §5 |
| 9 | §5.5 | Menti-Bench 448 items | AGENTS: the first milestone uses the 320 text items | staging only | AGENTS (authorized) |
| 10 | §6.3 RQ3 | mediation analysis | exploratory unless a causal design is reviewed | to be labeled exploratory | AGENTS (authorized) |
| 11 | §5.5 | ≥ 400 paired episodes "should resolve ~5 points" | confirm with a pilot power analysis | pending pilot | — |
| 12 | §4.1 step 5 | the policy chooses a_t "from the physical state and G_t" | the legacy oracle used the full raw history | the grounded actor uses the physical state, the literal report ledger, and graph outputs; units are bounded computations | **D-001 accepted** |
| 13 | §5.1 rewards | +1 / −0.05 / −0.5 | terminal-step charge, timeout, handoff irreversibility unspecified | −0.05 on every step incl. terminal; error component × stakes; last-step success counts; give terminal because there is no recovery action | **D-005 accepted** |
| 14 | §3.5 P3(a) | complement: "Receptionist → Alice" and "Alice" | under the grounded record this specific pair is not complementary (path_asymmetry: K(rec→alice) suffices alone) | grounded complement shown with {K(bob→rec), R(bob)}; the legacy record keeps the outline's example | reported; no change needed unless review objects |
| 15 | §5.4 | certified depth via "oracle policy limited to depth below ℓ*" | the result depends on the actor class | ℓ* reported per record (grounded ℓ* = 2 in path_asymmetry and nested_reliability) | spec §8 |
| 16 | — (new) | — | bounded actor's hypothesis space = generator support; entailed default violations leak structure | grounded cases built to avoid entailment; audit proposed | **OPEN Q2** (review-request) |
