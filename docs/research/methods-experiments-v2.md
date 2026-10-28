# Whose Mind Matters? Decision-Value Allocation of Theory of Mind over Perspective Graphs

Methods and experiments outline, v2 (scoped for IJCAI 2027 or ACL 2027 via ARR)

Working names: environment **OfficeMinds**; controller **VoMI-Router** (VoMI = value of mental information).

---

## 0. Submission frame

### 0.1 Venue facts that shape the paper
| | IJCAI 2027 | ACL 2027 (ARR January cycle) |
|---|---|---|
| Deadline | Abstract Jan 4, full paper Jan 11, 2027 (AoE) | Jan 4, 2027 (AoE) |
| Length | 7 pages body + 2 pages references; appendices go in supplementary material | 8 pages (9 at camera-ready); Limitations section required |
| Review | Two-phase; papers can be summary-rejected after two reviews, with no rebuttal | ARR reviews and meta-review, then commit to ACL; Responsible NLP checklist |
| Source | [IJCAI 2027 CFP](https://2027.ijcai.org/ijcai-2027-call-for-papers-main-track/) | [ACL 2027 CFP](https://2027.aclweb.org/calls/main/) |

- **Pick one by about Dec 14.** Both CFPs forbid concurrent submission: IJCAI won't accept papers under review at another venue with formal proceedings, and ACL states "dual submissions are not allowed." Write to IJCAI's 7-page body; it will fit ACL's 8 pages with room to spare.
- **How to choose:**
  - Go with **IJCAI** if the theory (§3.5) and multi-agent decision-making framing come out strongest.
  - Go with **ACL** if the Tier 2 language-robustness results and the Menti-Bench transfer are the strongest story.
- **IJCAI-specific:** because of the summary-reject phase, page 1 has to carry the paper. Put the teaser figure, the three claims, and one headline number there.

### 0.2 Claims the paper must prove (and the competitor each one defeats)
| Claim | Competitor it separates us from | Experiment |
|---|---|---|
| **C1.** Choosing whose mind to model, which variable, and which perspective path, by decision value, gives better task return at equal compute | Dense MWM/Mentis, depth-only (A-ToM), entity-only, query-chain methods (SimToM, RecToM) | RQ1 |
| **C2.** The *objective* matters: decision value beats reducing mental-state uncertainty and beats predicting whether the action flips | [AutoToM](https://arxiv.org/html/2502.15676v3) (entropy minus complexity); a flip-probability controller; a relevance classifier | RQ2 |
| **C3.** Unnecessary mental modeling *hurts* decisions, measured as hallucinated mental content and perspective leakage | "Just model everyone," "just think longer" ([Gong et al.](https://arxiv.org/html/2602.10625v2)) | RQ3 |
| **C4.** Depth belongs to directed perspective paths, not to people | Per-person depth, A-ToM | RQ5 |
| **C5.** A controller trained only on scripted people transfers to LLM role-played people and to MWM's own benchmark | The "toy environment" criticism | RQ7 |

Theory results (§3.5) back C1, C2 and C4.

### 0.3 Scope
- **In scope:**
  - Tier 1 (scripted people) for training and controlled experiments.
  - Tier 2 (LLM role-played people grounded in private role cards) for robustness.
  - Menti-Bench as a held-out transfer test only, per its license.
- **Out of scope:**
  - Tier 3 (human-played episodes), presented as future work (§8).
  - Emotions, long-horizon goals, and an "ask the human" action.

---

## 1. Introduction (outline only)
- **Hook:** an office robot delivering a package. In an empty hallway it needs no mental reasoning. Asking the receptionist requires modeling her knowledge. Trusting her answer requires modeling her intentions. "Alice thinks you already delivered it" requires modeling the receptionist's belief about Alice. A coworker who is there the whole time never needs modeling. Relevance changes over the course of the task.
- **Gap:**
  - MWM models every character and every mental variable at every step ([MWM](https://arxiv.org/html/2607.27201v1); [Mentis](https://github.com/mental-world/Mentis) parser).
  - Adaptive theory-of-mind methods either adapt depth for a single partner (A-ToM), take the target person from the question (SimToM, RecToM), or expand to reduce uncertainty about a question that is already given (AutoToM).
  - Wagner et al. split theory of mind into "deciding whether and how deeply to mentalize" and "doing the inference," and argue AI has addressed only the second ([Mind Your Theory](https://arxiv.org/abs/2412.13631)). We address the first.
- **Contributions:**
  1. VoMI over directed perspective paths, with flip-necessity, margin-pruning and non-additivity results.
  2. VoMI-Router, a single-pass controller trained from exact oracle labels.
  3. OfficeMinds, with controlled factors and certified depth, plus a grounded LLM role-play tier.
  4. Evidence for C1–C5.

## 2. Related work (compact; full version in the appendix)
- **MWM** and structured social world models ([S3AP](https://arxiv.org/abs/2509.00559v3)): dense representations of every participant.
- **Adaptive theory of mind:**
  - [AutoToM](https://arxiv.org/html/2502.15676v3): uncertainty-driven model discovery.
  - [A-ToM](https://arxiv.org/html/2603.16264v1): online selection of depth for one partner.
  - [Zing](https://arxiv.org/html/2607.23740v1): gates modules by the queried mental variable.
  - [RecToM](https://arxiv.org/html/2606.11724v2): recursion along the question's character chain.
  - [HopToM](https://arxiv.org/html/2610.17777v1): effective vs. merely syntactic nesting.
- **Perspective filtering:** SimToM, PercepToM, Thought-tracing. All need the target person to be given.
- **Rational metareasoning and value of computation:** Russell and Wefald; [rational metareasoning for LLMs](https://arxiv.org/html/2410.05563); I-POMDP behavioral equivalence. We cite these as foundations; we apply them to a structured, language-grounded space of mental-modeling actions.
- **Choosing whom to observe:** [Rational Mentalizing](https://arxiv.org/html/2607.28601v1) studies external observation; we study internal computation.
- **Choosing whose memory to retrieve:** [EgoMAS](https://arxiv.org/html/2603.09827v2) retrieves memories; we instantiate uncertain mental-state hypotheses.

---

## 3. Problem formulation

### 3.1 Setting
- An agent \(R\) acts among people \(\mathcal{P}=\{1,\dots,N\}\) and sees only its own surroundings: observation \(o_t\), history \(h_t=o_{1:t}\), action \(a_t\in\mathcal{A}\).
- **Egocentric by construction.** The agent never sees the global state, including other people's minds. MWM, by contrast, parses the scene from an all-seeing narrator and then removes what a character couldn't know. That removal step is a source of perspective leakage.

### 3.2 Modeling units
- **Perspective path:** \(\pi=(j_1,\dots,j_\ell)\), with \(\ell\in\{0,1,2\}\). \(\ell=0\) means physical reasoning only. Examples: (Receptionist), (Receptionist → Alice).
- **Variable:** \(v\in\{\textsc{Knowledge},\textsc{Reliability}\}\).
- **Unit:** \(u=(\pi,v)\). The candidate set at step \(t\) is \(\mathcal{U}_t\).
- **Perspective graph \(G_t\):** a sparse graph that stores each instantiated unit with its content, evidence sources, timestamp, confidence, and the compute spent on it.
- **Allocation:** \(S_t\subseteq\mathcal{U}_t\), the units instantiated at step \(t\). Everything else is left unmodeled.

### 3.3 Value of Mental Information
\[
\mathrm{VoMI}(u\mid S)=\mathbb{E}\big[Q^\star(s_t,a(S\cup\{u\}))\big]-\mathbb{E}\big[Q^\star(s_t,a(S))\big]-\lambda\,c(u)
\]
- \(a(S)\) is the action the policy chooses given allocation \(S\).
- \(Q^\star\) is the true action value, which the simulator can compute.
- \(c(u)\) is the measured cost of instantiating \(u\).
- \(\lambda\) is the price of compute. Sweeping it traces the return–compute frontier.
- **Link to MWM.** MWM §4 defines the value of mental information for a whole scene but never computes it. VoMI breaks it down per path and variable and makes it computable.

### 3.4 Decomposition that separates the three competing objectives
\[
\mathrm{VoMI}(u\mid S)=\underbrace{\Pr[\text{flip}\mid u,S]}_{\text{would the action change?}}\cdot\underbrace{\mathbb{E}[\Delta Q^\star\mid\text{flip}]}_{\text{how much is the change worth?}}-\lambda c(u)
\]
- **Mental-state entropy (AutoToM-style):** rewards uncertainty about a person's mind even when the action can't change.
- **Flip probability:** captures whether the action would change, but ignores stakes, so it treats a costly and a harmless flip the same way.
- **VoMI:** weights by the value of the change. It is the only one of the three that responds to stakes when observations are identical.
- **This is the paper's sharpest novelty statement.** Each competitor drops one factor, and RQ2 tests each separately.

### 3.5 Theory (proofs in the supplementary material)
- **P1. Flip necessity.** If no possible content of \(u\) changes \(a(S)\), then \(\mathrm{VoMI}(u\mid S)=-\lambda c(u)<0\).
  - The flip check is therefore a sound pruning test.
- **P2. Margin pruning.** If the gap between the top two actions under \(S\) exceeds the largest change in action values that any content of person \(j\)'s units could cause, every unit rooted at \(j\) has negative VoMI.
- **P3. Non-additivity.** VoMI is not submodular in general. Give explicit OfficeMinds constructions of:
  - (a) **complementary units:** neither "Receptionist → Alice" nor "Alice" changes the action alone; both together do.
  - (b) **substitutable units:** modeling "Bob → Alice" makes a direct model of Alice redundant.
- **P4. Bounded-interaction greedy guarantee.** With submodularity ratio \(\gamma>0\), greedy allocation under a budget achieves at least \((1-e^{-\gamma})\) of the optimal value. Report the empirical \(\gamma\).
- **P5. Stakes sensitivity.** With observations fixed, scaling the penalty for irreversible errors changes VoMI rankings but leaves flip probability and entropy rankings unchanged.
  - This is a short proposition that motivates the stakes experiment.

---

## 4. Method: VoMI-Router

### 4.1 Per-step pipeline
1. **Physical update (depth 0).** Always runs.
2. **Candidate generation with structural preconditions:**
   - A depth-1 unit on person \(j\) requires that \(j\) has been observed or mentioned.
   - A depth-2 unit \((j\to k)\) requires recorded co-presence, communication, or a relayed message between \(j\) and \(k\).
   - A Reliability unit requires conflicting evidence or a stated incentive.
3. **Allocation.** One controller pass scores all candidates and outputs a ranking plus a STOP probability.
4. **Instantiation.** For each selected unit, an LLM call infers its content from the agent's own history \(h_t\) only.
5. **Decision.** The policy LLM chooses \(a_t\) from the physical state and \(G_t\).
6. **Margin-triggered expansion.** If the decision margin is below \(\tau\), add the next-ranked unit and decide again, up to \(k\) rounds. This handles the complementary pairs from P3.

### 4.2 Controller
- **Inputs:**
  - Structural features per candidate: depth, how recently the person appeared, co-location with the goal, whether they have spoken to the agent, the number of conflicting reports, a stakes indicator, and the current decision margin.
  - A compact text summary of \(h_t\) and \(G_t\).
- **Main architecture:** a fine-tuned LM of about 1–2B parameters with a scoring head.
- **Alternative:** gradient-boosted trees over the structural features only. Reported in the ablations.
- **Cost:** report the controller's share of total compute. It must stay well below the cost of one instantiation call.

### 4.3 Training from exact oracle labels (Tier 1 only)
- **Oracle-content VoMI:** fill each candidate with its true content from the simulator, then compute whether the action flips and the resulting \(\Delta Q^\star\). This is symbolic and cheap.
- **Realized VoMI:** fill candidates with LLM-inferred content, on a subset of about 15% of states. This captures the cost of inferring a mind wrongly.
- **Loss:** regression on VoMI (realized where available), a pairwise ranking loss, and binary cross-entropy for STOP.
- **Multi-step distribution shift:** 2–3 rounds of DAgger-style relabeling of states visited by the controller.
- **No Tier 2 or Menti-Bench data is used for training.** This keeps C5 a real transfer test.

### 4.4 Compute accounting
- Report input and output tokens (hidden reasoning tokens where measurable), LLM calls, true end-to-end wall-clock time, and controller cost.
- Don't sum the latencies of calls that ran in parallel; Mentis's statistics code does this.
- All comparisons are at matched total compute, using budget sweeps for every method that has a compute knob.

---

## 5. Environment: OfficeMinds

### 5.1 Tier 1: scripted people (training and controlled experiments)
- **World:** 4–8 rooms, doors that may need a keycard, and objects (package, keycard, notes).
- **Actions:** `move`, `ask(person, q)`, `pick/give`, `deliver`, `wait`.
- **Episodes:** 5–10 steps, with a cap of 15.
- **People:**
  - A knowledge set: events they witnessed or were told about.
  - An intent type: cooperative, mistaken, or obstructive (with a stated incentive).
  - Nested beliefs, created only through relayed messages.
  - Templated answers.
- **Reward:** +1 for success, −0.05 per step, −0.5 for an irreversible error.

### 5.2 Tier 2: LLM role-played people (robustness)
- **Role cards:** the simulator writes a private card for each person from its true state:
  - what they saw and were told, with times
  - their intent type and motive
  - their relayed beliefs about others
  - a speaking style (terse, chatty, hedging, distracted)
- **Free behavior within the card.** A role-player can choose what to reveal, digress, answer only part of a question, misremember details it wasn't told precisely, and improvise stalling if obstructive. This is more open-ended than templates.
- **Truth stays symbolic.** Each person's actual knowledge, intent and nested beliefs come from the card and the event log, not from the generated text. VoMI labels therefore remain exact.
- **Grounding checker after every utterance:**
  - An LLM extractor turns the utterance into atomic claims; a symbolic matcher compares them with the card.
  - A claim that contradicts the card from a mistaken or obstructive person is allowed and logged as an error or lie. The true state is unchanged.
  - A claim outside the card from a cooperative person is regenerated, up to 3 times. If it still fails, the episode is dropped and counted.
  - **Reported:** role-fidelity rate, drop rate, and per-intent-type violation rates.
- **Author audit:** two authors annotate a random sample of about 300 utterances for faithfulness to the card and for naturalness. Report agreement (Cohen's κ).
  - Authors annotating their own data is not a human-subjects study. The Responsible NLP checklist still asks you to describe it.
- **Separation of model families:**
  - Role-players use a different model family from the agent.
  - A cross-family split swaps the role-player family, to rule out the agent exploiting patterns it shares with its own family.
- **Naturalness borrowed from real dialogue:** the style prompts draw hedging, vague directions and correction patterns from public human-robot dialogue corpora:
  - [SCOUT](https://arxiv.org/abs/2411.12844)
  - [TEACh](https://github.com/alexa/teach)
  - the [ARI receptionist data](https://github.com/wsieinska/multi-party-dialogue-dataset)

  Only patterns are used; no data from these corpora is reused.

### 5.3 Controlled factors
| Factor | Levels | Claim it supports |
|---|---|---|
| F1. Distractors | \(N_d\in\{0,1,2,4\}\) | C1, C3 |
| F1b. Distractor plausibility | Obvious vs. plausible (same role, overlapping knowledge, a motive) | C3. Rules out trivially ignorable distractors, which a [story-prompting study](https://arxiv.org/html/2506.19089v6) found barely matter |
| F2. Required depth | \(\ell^\star\in\{0,1,2\}\) as minimal pairs over the same physical scene | C1, C4 |
| F3. Relevance shift | None, or a switch at step \(t_s\) | C1 (when to model) |
| F4. Information holder | Which person holds the key fact, varied with the scene fixed | C1. Rules out position cues |
| F5. Stakes | Penalty ×1 vs. ×4 with identical observations | C2 (P5) |
| F6. Path asymmetry | Task needs Alice and Receptionist → Alice, but not the receptionist's own knowledge | C4 |

- The full factorial design is too large. Use a balanced fractional design across F1–F4, plus dedicated subsets for F5 and F6.

### 5.4 Certification and gold labels
- **Effective depth:** an oracle policy limited to depth below \(\ell^\star\) fails; one at depth \(\ell^\star\) succeeds. This follows [HopToM](https://arxiv.org/html/2610.17777v1)'s argument that nested wording alone doesn't guarantee a higher-order question.
- **Gold allocation:** at each step, the minimal set of units whose removal changes the oracle action.
- **Divergence tags:** steps where the unit that most reduces mental-state entropy, the unit with the highest flip probability, and the unit with the highest VoMI differ. These are the RQ2 subsets.

### 5.5 Splits and sizes (rough planning targets)
| Split | People | Purpose | Size |
|---|---|---|---|
| Train / Val | Tier 1 | Controller training and tuning | About 20k / 1k episodes (cheap, symbolic) |
| Test-T1-IID | Tier 1 | Main controlled results | About 1,000 episodes |
| Test-T1-OOD | Tier 1 | \(N\in\{6,8\}\), 12–15 steps, unseen layouts and intent combinations | About 400 |
| Test-T2 | Tier 2 | Robustness to open-ended language and behavior | About 400 |
| Test-T2-xfam | Tier 2, swapped role-player family | Rules out self-recognition | About 200 |
| RQ2 subsets | Tier 1 and Tier 2 | Divergence (≥300 steps); stakes pairs (≥200) | Drawn from the above |
| Menti-Bench | Held out, evaluation only | Transfer to MWM's own benchmark | 448 items |

- Aim for at least 400 paired episodes in each main comparison. That should resolve differences of roughly 5 points in success rate; confirm with a power check on pilot data.

---

## 6. Experiments

### 6.1 Protocol
- **Backbones:** at least 2 model families in the main table, one open-weight and one API model. Add one reasoning model on Test-T1-IID and Test-T2.
- **Fairness:**
  - Instantiation and policy calls use the same backbone for every method.
  - Every method gets the same tuning budget on Val.
  - All prompts are released.
- **Statistics:** 3 seeds; 95% bootstrap confidence intervals; paired permutation tests at the episode level; Holm correction across the main comparisons.
- **Stated in advance:** the RQ2 and RQ3 hypotheses and analysis plan, fixed before the test runs. Mention this in the paper.

### 6.2 Baselines
The key design choice: the group D baselines share **VoMI-Router's architecture, features and training data and differ only in the training target**. This isolates the objective as the contribution, which is the hardest test for C2.

| Group | ID | Baseline | What it rules out | Main / App. |
|---|---|---|---|---|
| A. No explicit allocation | A1 | Direct agent (ReAct-style; no explicit mental modeling) | "Mental modeling isn't needed" | Main |
| | A2 | Reasoning model with a large thinking budget, matched to compute | "Just think longer" | Main |
| | A3 | Dense MWM-style: everyone, all variables, fixed \(\ell=1\) and \(\ell=2\) | "Model everyone" (Mentis's parser policy) | Main |
| B. One axis only | B1 | Depth-only: global depth chosen online by Hedge over ToM-0/1/2 (A-ToM-style) | Depth adaptation alone | Main |
| | B2 | Entity-only: chosen people, all variables, fixed depth | Entity selection alone | Main |
| | B3 | Per-person depth (no directed paths) | C4 | Main |
| C. Target given by the task | C1 | Perspective filter on the person named in the task (SimToM-style) | Fixed-target methods | App. |
| | C2 | Character chain parsed from the task text (RecToM-style) | Query-chain construction | Main |
| D. Alternative objectives (same controller) | D1 | Mental-state-entropy controller (AutoToM-style utility: entropy reduction minus α·complexity) | **Uncertainty reduction (AutoToM's objective)** | Main |
| | D2 | Original AutoToM, adapted to action selection (iterative, not amortized) | Faithful reimplementation of the closest prior work; also shows the cost of iterative search | Main |
| | D3 | Flip-probability controller (trained on flip labels only) | "VoMI is just action uncertainty" (P5) | Main |
| | D4 | Relevance classifier (trained on gold-allocation membership) | "VoMI is just relevance" | Main |
| | D5 | Prompted router, zero-shot and few-shot (includes a Zing-style variable gate) | Learned vs. prompted control | Main |
| E. Retrieval and compute alternatives | E1 | Selected memory retrieval (EgoMAS-style; no mental inference) | Retrieval vs. mentalizing | App. |
| | E2 | Token-level adaptive reasoning (value-of-computation or fast/slow switching) | Generic adaptive compute | App. |
| F. Bounds | F1 | Random allocation at matched compute | Sanity floor | Main |
| | F2 | Oracle allocation (gold units, LLM-inferred content) | Allocation headroom | Main |
| | F3 | Full oracle (gold units, true content) | Pipeline headroom | App. |

- Approximate reimplementations (A-ToM-style, RecToM-style, Zing-style, EgoMAS-style) are labeled as such, with their fidelity described in the appendix.
- D2 uses the [released AutoToM code](https://github.com/SCAI-JHU/AutoToM) where it can be adapted to action selection.

### 6.3 Research questions
**RQ1 (C1): return at equal compute.**
- Return–compute frontiers on Test-T1-IID and Test-T1-OOD for groups A–D and F.
- **Figure 3**, plus **Table 1** at three compute budgets.

**RQ2 (C2): does the objective matter?**
- Compare VoMI-Router with D1–D5 on:
  - (a) the divergence subset
  - (b) the stakes pairs from F5
- **Report:**
  - wrong-person rate
  - wasted compute (spent on units with negative VoMI)
  - success rate
  - for stakes pairs: how much allocation changes when only the penalty changes. VoMI should change; D1 and D3 should not (P5).
- **Figure 4.** This is the main novelty result.

**RQ3 (C3): does unnecessary modeling hurt?**
- **Intervention,** with an unlimited compute budget:
  - raise plausible distractors \(N_d\) from 0 to 4
  - separately, force \(\ell=2\) on episodes certified as depth 0 or 1
- **Exact measurements, possible because the simulator knows the truth:**
  - hallucinated mental content: inferred states that contradict the true state or have no supporting evidence
  - perspective leakage: facts attributed to a person who never witnessed them or was told them
  - success rate
- **Confound controls:**
  - a length-matched dense baseline padded with neutral filler
  - an "irrelevant text, no people" control
- **Mediation analysis:** how much of the drop in success runs through hallucination and leakage rather than prompt length.
- Run on both Tier 1 and Tier 2. **Figure 5.**

**RQ4 (C1, when): tracking relevance shifts.**
- F3 episodes.
- **Metrics:**
  - switch latency (steps between the shift and the first model of the newly relevant person)
  - missed units with positive VoMI
  - lingering compute on people who are no longer relevant
- **Figure 6:** a heatmap of allocation over time.

**RQ5 (C4): directed paths.**
- On the F6 subset, compare VoMI-Router with B3 and B1 on success and compute.

**RQ6 (theory checks):**
- P1/P2: the share of candidates pruned, and the compute saved with no loss in accuracy.
- P3: how often complementary and substitutable pairs occur.
- P4: greedy vs. pairwise lookahead; the empirical \(\gamma\).

**RQ7 (C5): transfer and robustness.**
- **Tier 1 → Tier 2:** the controller is trained only on scripted people.
  - Report the change in performance and the gap to oracle allocation on Test-T2 and Test-T2-xfam.
  - Analyze results by role-fidelity rate and intent type.
- **Menti-Bench:** VoMI-Router acts as a front end that tells the Mentis parser which characters and variables to fill.
  - Report F1 and compute against full Mentis, by scene category.
  - Expect large savings on object and spatial scenes, with equal or better accuracy on interpersonal scenes.
  - Include an options-only control; MWM reports options-only F1 well above chance.

### 6.4 Ablations (appendix, plus one compact table in the body)
- Remove the STOP head.
- Remove margin-triggered expansion.
- Train on oracle-content labels only (no realized labels).
- Structural-features controller vs. LM controller.
- No DAgger.
- Remove each feature group.
- Controller size (0.5B / 1.5B / 3B).
- Sweep \(\lambda\).
- Remove structural preconditions (candidate set explodes).
- Limit depth to 1.

### 6.5 Metrics
- **Task:** success rate, return, steps, irreversible-error rate.
- **Compute:** tokens, calls, wall-clock time, controller share.
- **Allocation:** precision and recall against gold, wasted and missed units, switch latency, wrong-person rate.
- **Faithfulness:** hallucination rate, leakage rate, calibration of inferred confidence.
- **Tier 2 quality:** role-fidelity rate, drop rate, audit κ, naturalness rating.

### 6.6 Figures and tables (7-page budget)
| Item | Content | Page |
|---|---|---|
| Fig. 1 | Teaser: allocation over one episode. Distractors left unmodeled; Bob added after the keycard reveal; Receptionist → Alice added on the relayed message | 1 |
| Fig. 2 | Pipeline and perspective graph | 3 |
| Fig. 3 | Return–compute frontiers (RQ1) | 5 |
| Fig. 4 | Objective comparison on divergence and stakes subsets (RQ2) | 5–6 |
| Fig. 5 | Over-modeling intervention with mediation (RQ3) | 6 |
| Table 1 | Main results × backbones × budgets, Tier 1 and Tier 2 | 5 |
| Table 2 | Menti-Bench transfer by category (RQ7) | 6 |
| Table 3 | Compact ablations | 7 |
| Supplement | Proofs, Fig. 6 (relevance shift), the RQ5–RQ6 details, environment specification, role-card templates, checker prompts, audit protocol, extra baselines | — |

- **Page budget for the IJCAI body:**

| Section | Pages |
|---|---|
| Intro | 1.0 |
| Related work | 0.5 |
| Formulation and theory | 1.2 |
| Method | 0.9 |
| Environment | 0.9 |
| Experiments | 2.2 |
| Limitations and conclusion | 0.3 |

- For ACL, use the extra page for Tier 2 analysis and a longer Limitations section.

---

## 7. Limitations (draft text)
- People in Tiers 1 and 2 are simulated. Tier 2 behavior is open-ended, but its role-play reflects an LLM's idea of human behavior.
- Only two mental variables and a depth of at most 2.
- Oracle labels need simulator ground truth. In deployment, VoMI has to be estimated without an oracle.
- Wall-clock comparisons depend on the API and on how calls are run in parallel.

## 8. Future work: Tier 3 (human-played episodes)
- **Protocol (designed, not run):**
  - One participant per episode plays the key person from a role card, through a chat interface. Everyone else stays scripted or LLM-played.
  - Answers are collected at standardized decision points, so every method can be evaluated offline on the same recordings.
  - A post-episode questionnaire records what the participant actually believed, which keeps the labels exact.
  - Planned size: 30–50 episodes.
- **Payoff:** a released set of human-played episodes with known true mental states.
- **Prerequisite:** IRB approval. If the application is filed and approved before the camera-ready or ARR resubmission deadline, a pilot can be added during revision.

---

## 9. Timeline to Jan 4 / Jan 11 (about 10–12 hrs/week)
| Week of | Milestone |
|---|---|
| Oct 26 | Freeze formulation (§3); write the P1–P3 constructions |
| Nov 2 | Tier 1 simulator: world, people, events, reward |
| Nov 9 | Episode generator F1–F6; oracle \(Q^\star\); certification; gold labels |
| Nov 16 | Pipeline with the LLM backbones; baselines A1–A3, B1–B3, F1–F2; pilot run and power check |
| Nov 23 | Controller training on oracle labels; realized-label subset; first frontier plot |
| Nov 30 | Group D baselines (D1–D5) on the same architecture; RQ2 subsets |
| Dec 7 | Tier 2 role cards, renderer, checker; generate Test-T2; start the author audit |
| Dec 14 | **Choose IJCAI or ACL.** Full test runs on Tier 1 and Tier 2; RQ3 intervention |
| Dec 21 | Menti-Bench transfer; ablations; DAgger round if time allows |
| Dec 28 | Write; make figures; proofs in the supplement |
| Jan 4 | ACL (ARR) deadline, or IJCAI abstract |
| Jan 11 | IJCAI full paper and supplement |

- If time runs short, cut in this order: E1–E2, the Test-T2-xfam split, DAgger, the controller-size ablation, then P4.
- Keep RQ1, RQ2, RQ3 and RQ7 (Tier 2) at all costs; they carry C1–C3 and C5.

## 10. Risk register and fallback narratives
| Risk | Signal | Fallback |
|---|---|---|
| VoMI ≈ flip probability (D3) | RQ2 shows no gap except on stakes pairs | Center the story on stakes sensitivity (P5) and on the gap to AutoToM's entropy objective, which remains |
| No over-modeling harm | RQ3 success rate is flat as distractors increase | The paper becomes a story about allocation correctness and efficiency. Report hallucination and leakage anyway; they are still novel exact measurements |
| Prompted router (D5) matches VoMI-Router | RQ1 and RQ2 gaps are small | Emphasize controller overhead and the cost of iterative search (D2); show where prompting fails (relevance shifts, stakes) |
| Large drop from Tier 1 to Tier 2 | RQ7 | Analyze by intent type and fidelity rate; add a small Tier 2 fine-tuning set as an ablation, never mixed into the main results |
| No gain on Menti-Bench | RQ7 | Report compute savings at equal F1. Menti-Bench averages about 2 characters per scene, which is a stated reason the new environment is needed |
