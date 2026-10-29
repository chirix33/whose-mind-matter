# Whose Mind Matters? — Implementation Agent Instructions

Version: 2026-10-28. Place this file at the root of the fresh repository.

> **Active development block (registered 2026-10-29, fourth):** `REPAIR_BLOCK_RESEARCH_DECISIONS.md` (sha256 `90b2bcfa…53f9`; recorded as D-016). It authorizes one bounded integration diagnostic: an audit of existing traces; a frozen single-decision probe (3b and 2b plus positive controls 3a and 2a; fresh seeds; exact reference notes; content vs content-plus-action-consequence mapping × after-ask stale warning shown vs omitted; no-note baselines; t0 and standardized post-ask contexts; about 1,536 local calls); and a 16-call API policy check, at most USD 0.50 extra within the USD 5 total. No allocation training, prompt revisions, environment changes, or larger API runs. State and plan: `reports/integration-block/`. Same two reviewer sub-agents.
>
> **Previous block (complete, registered 2026-10-28, third):** `DEV_V3_RESEARCH_REVIEW.md` (sha256 `813bc8c5…4d70`; recorded as D-015). It authorizes one bounded repair-and-validation block of at most two stages: Stage 1 makes one documented package revision (citable public-model IDs, a prior-vs-posterior inference revision, a matched note renderer, full-distribution scoring), then qualifies and freezes it; Stage 2 runs one local replication on fresh, preselected dev-v3 seeds with depth controls. No allocation training, reward changes, new templates, model shopping, or new API spending. State and plan: `reports/repair-block/`. Same two reviewer sub-agents. **Complete (2026-10-29):** handoff `reports/repair-block/FINAL_REVIEW.md` (pre-declared outcome §5(3)); awaiting research review.
>
> **Previous block (complete, registered 2026-10-28, second):** `POST_BLOCK_RESEARCH_DECISIONS.md` (sha256 `caf9b8fd…54c1`; copy of Ashraf's `research-reviews/POST_BLOCK_RESEARCH_DECISIONS.md`, recorded as D-014). It accepts the autonomous block below and authorizes a two-round scenario-and-reference qualification block (Round A: dev-v3 generator and public-model qualification; Round B: a small fresh-context value-of-notes check, local first; optional API batch only within the remaining original USD 5 cap). No controller training, prompt search, or full API five-arm run. State and plan: `reports/dev-v3-block/`. The same two reviewer sub-agents gate each round. **Complete (2026-10-28):** handoff `reports/dev-v3-block/FINAL_REVIEW.md`; awaiting research review.
>
> **Previous block (complete):** `AUTONOMOUS_RESEARCH_BRIEF.md` (sha256 `044e594c…ec0c12`; copy of Ashraf's `research-reviews/AUTONOMOUS_RESEARCH_BRIEF.md`). It authorizes a bounded autonomous loop of at most three methodological rounds under the existing USD 5 total cap. Within that block it supersedes preparation-only check-ins. It does not replace this file or the outline. State and resume point: `reports/autonomous-block/checkpoint.md`. Clarifications supplied by Ashraf: two reviewer sub-agents gate each round (Opus 5.5 checks scientific validity; Sonnet 5.5 independently recomputes the numbers); Round 2's inferred notes come from the API model; execution stays local.

## 1. Mission and research ownership

Implement **Whose Mind Matters? Decision-Value Allocation of Theory of Mind over Perspective Graphs** for a potential IJCAI 2027 or ACL 2027 submission. Working names: **OfficeMinds** for the environment and **VoMI-Router** for the controller.

The central question is: **Can an agent improve decisions at matched compute by choosing whose mental state to model, which variable to infer, and which directed perspective path to instantiate, according to decision value?**

Ashraf owns this project and runs implementation through this IDE/agent. The separate ChatGPT research conversation serves as the main research driver: it reviews evidence, resolves methodological questions, and aligns revisions with the original goal. Do not address Ashraf as Professor Roy. Do not imply that research review has happened unless Ashraf has supplied its outcome.

Your responsibility is working, reproducible implementation and honest evidence. Preserve the original research objective. Do not replace it with generic adaptive reasoning, retrieval, a benchmark-only project, or an efficiency-only narrative without research review. A cheaper engineering prototype is a milestone toward the method, not a replacement for it.

## 2. Source documents and decision authority

Read the complete attached outline, originally named:

`Methods & Experiments Outline  Whose Mind Matters.md`

The preferred repository location is `docs/research/methods-experiments-v2.md`. Locate the supplied original and preserve its contents verbatim at this canonical path; record its SHA-256 and original filename. Do not invent missing content or silently rewrite the source outline. If unavailable, request it and continue only independent repository setup and environment diagnostics.

Use these sources in order:

1. Ashraf's explicit instructions and research decisions supplied during implementation.
2. This file: agreed execution defaults, scientific safeguards, and clarifications of the outline.
3. Later reviewed decision records under `docs/decisions/`.
4. The outline for the full method, experimental matrix, hypotheses, and planned scope.

A later reviewed decision may supersede a provision of this file only when the record names that provision and records the supplied decision. If sources conflict, identify the conflict; do not silently choose the interpretation most convenient to code.

### Autonomy

Proceed independently with reversible engineering choices: package layout, implementation details, meaningful tests, bug fixes, profiling, small local smoke runs, and refactoring that preserves the specified behavior. Do not ask for repeated confirmation of these defaults.

Bring changes to definitions, hypotheses, oracle semantics, training/test boundaries, statistical protocols, required baselines, or research scope back for research review. First prepare a concrete short proposal with the problem, alternatives, recommendation, consequences, and a minimal example or evidence. Continue independent work while the affected decision is pending. Do not mark a proposal as accepted yourself.

The clarifications below are authorized constraints. Unresolved choices explicitly identified below remain provisional and must be documented before bulk label generation, training, or confirmatory evaluation.

## 3. Confirmed workstation and resource policy

- Fresh repository, WSL Ubuntu, one NVIDIA RTX 5090 with 32 GB VRAM.
- vLLM and some model weights are already installed; `gpt-oss-20b` is available locally. Exact versions, weight paths, formats, and endpoint settings must be inspected on the actual workstation.
- An Ollama API key may become available. Do not assume it exists. Distinguish local Ollama serving from hosted/cloud access.
- Prefer existing local resources and free-to-cheap options. No numeric paid API budget has been established.
- Begin with a small local pilot. Do not start paid API calls, cloud GPU jobs, subscriptions, or large downloads without the corresponding resource decision. Once Ashraf supplies a budget and scope, operate within it without repeatedly asking.
- Do not assume this chat workspace exposes the workstation GPU or installed models. Report the environment in which a command actually ran.

Inventory Python, the NVIDIA driver, CUDA availability, PyTorch, vLLM, available model IDs/paths, free VRAM, RAM, and disk space. Record useful versions and capabilities without dumping environment variables or secrets. Reuse a working environment; isolate necessary changes instead of upgrading the entire stack.

Use the installed `gpt-oss-20b` as the first **agent-backbone pilot candidate**, subject to a real serving smoke test. Respect its native chat format and separate reasoning/output channels. Do not use it as the small routing controller by default. Select the approximately 1–2B controller checkpoint after checking compatibility, license, training feasibility, and measured overhead. Keep the feature-only controller as an ablation and early diagnostic.

Measure actual peak VRAM, context length, batch/concurrency settings, latency, throughput, and structured-output validity. Advertised weight memory is not total runtime memory. Do not assume the backbone, role-player, and trainable controller fit concurrently. Sequential jobs and model switching are acceptable; record their timing separately.

Keep provider/model selection configuration-driven. Build a small model-client interface for the working local endpoint and later adapters; avoid an unnecessary orchestration framework. Keep keys in environment variables or ignored local files. Never commit keys, credentials, model weights, or caches.

## 4. Preserve the intended scientific scope

Retain the outline's five claims as **hypotheses**, not facts to manufacture:

- **C1:** decision-value allocation improves return at matched compute.
- **C2:** decision value provides an advantage over uncertainty, flip probability, and relevance objectives.
- **C3:** unnecessary modeling can harm decisions through hallucinated content or perspective leakage.
- **C4:** depth is associated with directed perspective paths rather than simply with people.
- **C5:** a controller trained on scripted Tier 1 data transfers to Tier 2 and held-out Menti-Bench.

Core scope: depths 0/1/2, Knowledge and Reliability variables, Tier 1 training, Tier 2 robustness, and held-out transfer. No emotions, long-horizon goal modeling, new ask-the-human action, or human-participant collection. Retain the normal environment action `ask(person, q)`; it is distinct from asking a real human for assistance.

**RQ1, RQ2, RQ3, and the Tier 2 component of RQ7 are core deliverables.** Keep the directed-path comparison and learned router in the roadmap. Use the outline's fallback priorities when proposing scope reductions; do not remove a difficult core experiment silently.

The first Menti-Bench milestone uses the **320 text items**, not the entire 448-item multimodal collection. Image/video adapters are later work. State the evaluated subset in every transfer report. This is a staging choice, not permission to claim full-benchmark results.

## 5. Specify the scientific contract before scaling

Create `docs/research/implementation-spec.md` and a short decision record for unresolved semantics. Use executable tiny examples to expose ambiguity. The first milestone includes repository setup and these examples; it must not jump directly to the outline's roughly 20k training episodes.

### 5.1 State, history, and information access

Separate at the type and serialization boundaries:

- physical simulator state;
- each person's private perceived events, belief contents, and intent;
- robot-visible observations and action-observation history;
- the robot's inferred perspective graph;
- privileged oracle/evaluator annotations.

Use history containing past actions as well as observations. Policy inputs, controller features, candidate construction, summaries, inference prompts, and graph updates must use robot-visible information only. Keep privileged annotations in a separate record or artifact and never serialize them into agent inputs.

Define Knowledge to represent the person's epistemic state, including uncertainty and false beliefs, rather than merely a set of objectively true facts. Distinguish `unknown`, supported belief, and objective truth. Define Reliability with a finite schema separating stable intent from statement-level correctness; a mistaken cooperative speaker is not automatically an intentional liar. Record a proposed ontology for review rather than silently adding new scientific variable families.

For a path `(j, k)`, specify that the content is **j's belief about k's state**. It is neither k's actual state nor the robot's direct belief about k. The unit variable must have an explicit interpretation at each path depth. Physical reasoning at depth 0 is mandatory and is not duplicated as separate mental units.

### 5.2 VoMI and oracle contracts

Use the outline's marginal-value objective as the starting point:

`VoMI(u | S) = E[Q_ref(s, a(S union {u})) - Q_ref(s, a(S))] - lambda * c(u)`.

The implementation spec must name:

- the decision policy that defines `a(S)`, its inputs, and deterministic tie-breaking or sampling convention;
- the hidden-world/content distribution used by the expectation and how it is conditioned on visible history;
- the finite horizon, reward, discount convention, transition model, and continuation policy that define action values;
- the units of cost, treatment of cache reuse, and meaning of lambda;
- the allocation S and graph state for which each label is valid.

Do not call a value `Q*` or a label exact unless the corresponding optimization and expectation are actually solved exactly under the stated model. A fully informed state oracle and an observation-limited agent can have different continuation values. Label privileged bounds as such.

Maintain distinct records for:

1. **Exact symbolic-oracle VoMI:** calculated under a fully specified symbolic decision policy and finite simulator model, where exact computation is feasible.
2. **Oracle-content LLM marginal value:** true content supplied to the LLM policy; requires actual LLM decisions and can be stochastic. It is an oracle-content bound/diagnostic, not cheap exact symbolic labeling.
3. **Realized LLM VoMI:** actual LLM-inferred content and decisions; estimate with recorded sampling and uncertainty when stochastic.

Symbolic labels do not establish how an LLM will act. Document the symbolic-to-LLM gap. True hidden content may be used for supervision, evaluation, and clearly labeled bounds, never as an unreported deployment input. Include history-ambiguous examples so the controller is not expected to recover unknowable private facts perfectly.

For small worlds, compare the oracle with exhaustive enumeration or an independent calculation. If a scaled solver uses sampling or approximation, record that distinction per label. Tier 2's symbolic role cards keep state labels known, but unconstrained LLM responses do not automatically yield exact future action values. Use explicitly estimated Tier 2 values where necessary.

### 5.3 Allocation labels, candidates, and memory

Candidate eligibility must be derived from observed/mentioned people and visible evidence of communication or incentives/conflict. Do not read private intent, hidden co-presence, or generator relevance tags. Measure candidate-generation recall against privileged reference candidates separately from router performance.

Preserve the outlined structural preconditions, but audit false exclusions. A constraint that prevents the correct unit from being considered is a pipeline failure; do not hide it by scoring the router only over surviving gold units.

Gold allocation may be non-unique. Distinguish a minimal sufficient set, a minimum-cost sufficient set, and leave-one-out necessity. Identify which definition drives each metric. Enumerate valid alternatives in tiny cases and make precision/recall tolerant of equivalent valid sets under the chosen protocol. A unit is not universally irrelevant merely because it has zero singleton value.

Each graph unit stores path, variable, typed content, confidence, visible evidence IDs, timestamp, and incurred cost. Specify retention, invalidation, updates, and contradictions. A retained unit is not a newly inferred unit; retrieval and prompt-processing still have costs. Never silently erase the graph every step or treat stale content as fresh.

Provide the controller with the current S/graph, budget or lambda as appropriate, and all named visible features. Specify how STOP labels are computed. A one-pass ranking is a heuristic for conditional marginal values; document when it is frozen and when it is rescored. Preserve the intended one-pass main controller and bounded margin-triggered expansion unless a reviewed decision changes them.

Define a decision margin without consulting true action values at deployment. If LLM scores are used, define their extraction, units, and calibration. Count any initial decision/scoring call needed to obtain the controller's margin feature. Do not introduce an uncounted oracle margin.

### 5.4 Theory safeguards

- **P1:** no-flip pruning is conditional on the current S, fixed decision semantics, and all feasible contents under the stated model. A finite sample with no observed flips is not a proof. Reconsider a unit after S changes when complements are possible.
- **P2:** bound changes in pairwise action-value differences. A bound on each action's change is not automatically the same bound on the gap. State all assumptions and test boundary/tie cases.
- **P3:** implement explicit complementary and substitutable constructions with known calculations. Low-margin expansion is a proposed heuristic; do not claim it always discovers complementary pairs.
- **P4:** optional conditional theory. Do not assert a general greedy guarantee for cost-penalized, potentially non-monotone VoMI. Specify the set function, monotonicity/normalization assumptions, constraint, and algorithm required by the cited theorem. Pure complementarities can yield gamma = 0. Sampled empirical gamma is a diagnostic, not a certified global lower bound.
- **P5:** stakes invariance of flip rankings is conditional, not universal. Changing penalties may change the initial policy and flip probabilities. Construct paired cases with unchanged flip probabilities and uncertainty but different consequences; verify this numerically before using them to isolate the value factor. Do not suppress genuine stakes sensitivity in a competing controller.

### 5.5 Depth certification

State exactly what lower-depth policies can represent and observe. One shallow policy failing does not prove all shallow policies must fail. Prefer controlled history pairs indistinguishable under the specified shallow representation but requiring different optimal decisions, with a depth-appropriate policy resolving the distinction. Report certification relative to that formal policy/representation class.

Prevent shortcuts from names, room positions, template wording, task text, or generator metadata. An LLM with raw history can reason implicitly about minds even without explicit graph units; distinguish absence of explicit allocation from absence of all mental reasoning. Do not claim to enforce an LLM's internal reasoning depth through prompting alone.

## 6. Staged implementation and acceptance criteria

### Stage 0 — Bootstrap and specification

Create a modest Python package, reproducible dependency setup, configuration files, tests, and repository documentation. Prefer Python 3.11+ where compatible with the installed stack; do not force a version migration without a reason. Suggested organization:

```text
src/officeminds/       # world, events, observations, people, generation
src/vomi/              # oracle, allocation, graph, clients, controllers, evaluation
configs/               # environment, models, pilot, experiments
prompts/               # versioned templates
tests/                 # invariants and small scientific constructions
scripts/               # thin reproducible entry points
docs/research/         # original outline, spec, analysis plan, baseline fidelity
docs/decisions/        # proposed/accepted/superseded research choices
reports/               # reviewable milestone findings
```

Adapt layout when helpful; do not build a web UI or unnecessary services. Keep large datasets, checkpoints, and raw run outputs outside normal Git tracking, with manifests and access paths. Do not initialize an external remote or publish data without instruction.

Deliver: environment inventory; source-outline checksum; implementation spec with open choices; roadmap mapped to C1–C5/RQ1–RQ7; CPU-only test command; local model smoke command. Document commands only after implementing and running them, or mark them explicitly as proposed/unrun.

### Stage 1 — Simulator and symbolic validation

Implement a deterministic seeded Tier 1 world: rooms, doors, objects, event visibility, people, messages, actions, rewards, and horizon limits. Represent false beliefs and directed nested beliefs explicitly. Use the outline's +1 success, -0.05 per step, and -0.5 irreversible-error defaults; specify terminal/error behavior and the stakes variant.

Build tiny cases for depth 0/1/2, plausible distractors, an information-holder permutation, a relevance shift, path asymmetry, stakes pairs, complementary units, and substitute units. Add balanced generation only after the examples work.

Acceptance: replay reproduces events and rewards; invisible events do not appear in agent inputs; belief updates respect access and communication; reference action values match exhaustive tiny-case checks; certification and gold-set ambiguity are visible in reports. Bring unresolved scientific semantics for review before bulk generation.

### Stage 2 — End-to-end local pilot

Integrate the real local model for instantiation and decision-making with validated schemas, bounded retries, explicit unknown/abstain outputs, and complete usage records. Separate mock-client tests from real model evaluations.

Start with roughly 30–50 scenario groups on development seeds. Compare direct reasoning, dense modeling, random allocation, symbolic/oracle allocation diagnostics, and a simple routed prototype. Measure label-policy mismatch and observe whether task decisions actually depend on mental content. Do not use this pilot as a confirmatory test set later.

Deliver real traces and a pilot report: outcome metrics, compute breakdown, memory/latency, invalid-output rate, estimated cost of the full matrix, and a recommendation for backbones, controller training, second family, and any paid pilot allowance. Resource estimates are not measured results; label them.

### Stage 3 — Training and objective comparisons

After the scientific contract is reviewed and the pilot supports scaling, generate Tier 1 training/validation data. The outline's counts and approximately 15% realized-label subset are planning targets, not a command to launch an expensive sweep immediately.

Implement the small LM router with scoring/ranking and STOP objectives; compare the feature-only model. Retain realized-label supervision and DAgger-style relabeling in the roadmap. Demonstrate learning on a small subset before full training.

For D1, D3, and D4 use the same architecture, visible inputs, scenario splits, state examples, and comparable tuning budget. Their supervision targets differ. Define entropy priors, hypothesis spaces, and the queried target. Do not describe AutoToM as reducing arbitrary uncertainty over every mind: its published objective concerns the query's target variable minus model complexity.

Implement D2 from released AutoToM code where feasible, with a documented action-selection adapter. Give D5 comparable information and an honestly counted prompting budget. Maintain `docs/research/baseline-fidelity.md` covering every baseline's source version, adaptation, known differences, and compute knobs. Label style-based adaptations as such. Never label OfficeMinds dense modeling as a verbatim Mentis reproduction.

### Stage 4 — Tier 2 and transfer

Generate Tier 2 role cards from private symbolic state. Keep their contents private from the robot. Use a different role-player model family from the agent; a second checkpoint in the same family is not a cross-family control. If a second family is unavailable, finish independent Tier 2 infrastructure and report the blocked experiment.

Implement claim extraction and grounded checking, with bounded regeneration and logged failures. Distinguish an allowed character lie/error from a role-card violation. Do not equate extractor output with perfect semantic truth: validate it against a blinded author audit. Track exclusions by scenario and intent type; avoid method-dependent episode dropping. Retain dropped episode IDs and reasons.

Freeze evaluation scenarios and role-player settings, not one universal response transcript: different agents can legitimately ask different questions. Record actual interactions and use reproducible event/randomness conventions where possible. Treat Tier 2 action-value estimates honestly.

Provide the approximately 300-utterance audit export, rubric, randomized IDs, independent author labels, agreement calculation, and naturalness summary. Do not fabricate annotations or certify institutional ethics determinations yourself. No human-played Tier 3 collection is authorized.

For Menti-Bench, start with the 320 text items and preserve its official scoring conventions. Build a documented adapter for scene/history inputs, visible controller features, candidate paths, and Knowledge/Reliability-to-Mentis fields. Hold other Mentis variables constant between full and routed comparisons; document the coverage limitation. Count candidate extraction and adapter calls in compute. Never train, tune prompts, choose thresholds, or select checkpoints on Menti-Bench. Use separate development fixtures. Pin and respect the actual code/data licenses and dataset revision.

### Stage 5 — Frozen evaluation and paper evidence

Freeze the confirmatory configurations and RQ2/RQ3 analysis plan before test execution. Run the agreed baseline/budget matrix, required seeds, robustness analyses, and ablations with resumable manifests. Report negative findings and pipeline failures alongside improvements.

Do not choose a venue based on fabricated or selectively reported evidence. The research conversation reviews the resulting story and submission choice. Verify official submission policies again near submission; do not assume calendar facts remain unchanged.

## 7. Experimental integrity and compute accounting

- Group train/validation/test splits by underlying scenario family, world seed, paired variants, and shared templates/layouts as appropriate. Names or penalty variants of one scenario must not cross splits. Keep paired test items together for analysis.
- Freeze test IDs and hashes. Use development data for debugging and tuning. If a test set is inspected for method development, disclose it and establish a fresh held-out evaluation where feasible.
- Every evaluated method gets the same legal observation channel, action interface, task rewards, backbone for shared roles, and comparable validation tuning budget.
- Preserve the outline's baseline inventory and mark each item implemented, pilot-only, planned, deferred with a supplied decision, or blocked. Do not hide missing competitors.
- Separate task return from compute-penalized utility. Compare return at matched total compute and provide budgets/frontiers, not just one convenient operating point. Keep success, errors, and task length visible.
- Log input/output/reasoning tokens when available; never interpret an unavailable reasoning-token count as zero. Tokens from different tokenizers are not identical compute. Report them with model identity, hardware time, and monetary cost where applicable.
- Count controller inference, summaries, candidate extraction, retries, policy rescoring, inference calls, and graph reuse costs. Separate one-time training/label-generation costs from deployment costs and report both. Account for any bootstrap decision used to obtain a margin.
- Measure true request/episode wall-clock time with a monotonic clock. Do not sum parallel call latencies as elapsed time. Record concurrency, warm/cold conditions, model loading, caching, and local resource contention.
- A router being small does not establish negligible overhead. Measure the controller's fraction of total time/compute under realistic deployment conditions.
- For RQ3, unlimited budget means removal of the experimental budget constraint under a finite, documented runtime/context cap. Preserve the task and causal mechanism when adding distractors. Include matched-length controls, actual counts and normalized rates of hallucination/leakage, and task outcomes.
- Distinguish factually false mental attributions, unsupported attributions, and perspective leakage. Use the person's accessible evidence and the defined inference rules; reasonable supported inference need not require direct witnessing.
- Treat RQ3 mediation as exploratory unless a justified causal design is reviewed. Correlation between hallucination and failure is not proof of mediation.
- Plan three seeds for main stochastic comparisons; distinguish training seeds, environment seeds, and inference replicates. Pair methods by scenario. Bootstrap/permutation units must preserve scenario groups and paired variants; steps from one episode are not independent samples. Predefine Holm comparison families.
- Confirm sample sizes with pilot-based power calculations using paired discordance and the primary endpoint. The outline's approximate episode counts do not automatically guarantee power to detect a five-point difference. Predefine practical tolerances for equal-quality compute-savings claims.

## 8. Reproducibility and review handoffs

Each run records: run ID, Git commit and dirty status, resolved config and hash, dataset/split hashes, prompt versions, model IDs/revisions/quantization, server and library versions, seeds, decoding/reasoning settings, start/end time, hardware, usage, failures, retries, and output locations. Save enough intermediate decisions, allocations, evidence references, and graph updates to diagnose results. Keep privileged traces separated from agent-visible records. Never record credentials.

Make runs resumable and cache keys sensitive to model revision, prompt, input, decoding configuration, and relevant state. Do not reuse a stochastic draw as an independent replicate. Replaying cached outputs is not a fresh latency measurement. Preserve failed records instead of silently retrying until success.

At each milestone, produce or update:

- `reports/latest.md`: milestone, claims/RQs addressed, actual commands run and outcomes, links to manifests, a small results table, failure examples, limitations, resource usage, and next action.
- `reports/review-request.md`: only when needed, the concrete methodological question with alternatives and a recommendation, plus paths to supporting evidence. Ashraf can bring this to the research conversation; no automatic cross-agent communication is assumed.
- `docs/decisions/`: short dated records with status (`proposed`, `accepted`, `superseded`), rationale, affected configurations, and the supplied review outcome. Keep a discrepancy log against outline sections.

Every number must be traceable to artifacts. Label mocks, estimates, pilots, and held-out results distinctly. Never claim a test passed without running it. Never adjust data or metrics to force the expected advantage. Explain negative findings and propose the next diagnostic within the original research goal.

## 9. Definition of done and first action

A milestone is complete when its implementation runs in the stated environment, its relevant correctness checks pass, configuration and evidence are reproducible, limitations are recorded, and the review handoff is usable. A paper-ready claim additionally requires the relevant frozen evaluation and research review. Code completion alone is insufficient.

**Start now with Stage 0 and the smallest Stage 1 examples.** Read the outline, inspect the actual environment, create the repository scaffold and spec, and demonstrate a replayable tiny episode plus a checked symbolic value calculation. Do not start with router fine-tuning or mass API generation. Continue authorized engineering work without waiting for unnecessary confirmations.

## 10. Primary references to verify and pin

The outline contains the full related-work list. Verify original papers, official repositories, versions, and licenses before making comparative implementation claims. Useful starting sources, checked during the research handoff on 2026-10-28:

- MWM paper: https://arxiv.org/html/2607.27201v1
- Mentis and benchmark documentation: https://github.com/mental-world/Mentis
- AutoToM paper: https://arxiv.org/html/2502.15676v3
- AutoToM code: https://github.com/SCAI-JHU/AutoToM
- Greedy guarantee assumptions: https://proceedings.mlr.press/v70/bian17a.html
- Installed pilot candidate's official model card: https://huggingface.co/openai/gpt-oss-20b
- Current vLLM model support: https://docs.vllm.ai/en/latest/models/supported_models/
- IJCAI main-track CFP: https://2027.ijcai.org/ijcai-2027-call-for-papers-main-track/
- ACL main-track CFP: https://2027.aclweb.org/calls/main/

Do not copy old installation commands from a model card without checking the installed environment and current serving documentation. No specific new provider, model purchase, paid budget, or second-family checkpoint is approved by this reference list.
