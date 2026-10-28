# Whose Mind Matters? — Autonomous Research Development Brief

Version: 2026-10-28  
Owner: Ashraf  
Execution agent: the IDE/cloud agent working in the existing OfficeMinds repository  
Research driver: the separate ChatGPT research conversation, via Ashraf

## 1. Start instruction and authority

**Execute this development block through its stopping rule. Choose local or cloud execution yourself within the resource limits below. Do not stop after preparing a plan, fixing one issue, or declaring that a run is ready. Complete the authorized iterations and return one consolidated research handoff.**

Ashraf has authorized this autonomy. You may make routine engineering decisions, conduct the bounded experiments below, inspect failures, and select the next permitted diagnostic from the resulting evidence. Do not request another approval between these actions. A negative or inconclusive finding is a valid outcome.

Save this brief at the repository root and register it as the active development block in `AGENTS.md` or the repository's existing active-work pointer. Preserve existing instructions and provenance. For this block, this brief supersedes earlier preparation-only check-ins and the unsent `model-diagnostic-review.md`; its relevant rulings are incorporated here. It does not replace the original research outline or authorize a different research project.

Read the existing `AGENTS.md`, `docs/research/methods-experiments-v2.md`, current implementation spec, decision records, and latest model-diagnostic report. Use current repository artifacts as authoritative for exact state; the summary below may be older than the next execution session. Do not repeat completed work unless a relevant change or unresolved error justifies it.

## 2. Research problem and purpose

**Main research question:** Can a resource-bounded agent improve task decisions at matched compute by choosing whose mental state to model, which mental variable to infer, and which directed perspective path to instantiate according to expected decision value?

The intended project remains **Whose Mind Matters? Decision-Value Allocation of Theory of Mind over Perspective Graphs**. OfficeMinds is the environment; VoMI-Router is the intended learned controller.

Preserve these dimensions:

- people/entities;
- Knowledge and Reliability;
- directed paths of depth 0/1/2, with physical reasoning always available;
- deciding when to compute and when to STOP;
- decision return and actual compute, including the controller's own overhead;
- eventual Tier 1 training, Tier 2 language/behavior robustness, and held-out transfer.

The full-paper claims C1–C5 and experiments RQ1–RQ7 remain in the original outline. Do not silently pivot to a hallucination-only, generic prompting, model-comparison, or retrieval paper. Do not manufacture a positive result by withholding ordinary evidence from a baseline or changing the task until direct reasoning fails.

**Purpose of this block:** resolve whether the current environment and pipeline exhibit useful, evidence-grounded mental-computation value, and identify the remaining bottleneck well enough to choose the next research milestone. This block does not need to establish a publication-ready advantage.

## 3. Current evidence and open questions

The existing work has a simulator, symbolic reference calculations, frozen development data, a five-arm local pilot, and a local/API model diagnostic. Preserve all existing runs.

Reported current observations:

- The local direct agent performed reasonably well; explicit notes often reduced return.
- The API policy obtained better decisions on a small crossed subset. Changing the note-generation model alone showed no dependable improvement.
- The revised grounding package often abstained, including on apparently resolvable contexts.
- Some public wording about overheard remarks conflicts with the simulator's belief-update rules and scoring reference.
- The API/API mean advantage over direct depended strongly on one instance. There is no replicated causal conclusion about that case.
- A zero-shot router was evaluated; the proposed learned VoMI-Router has not been tested.
- The latest report estimates about USD 1.31 spent out of an existing USD 5 allowance. Verify the ledger before spending.

Resolve three questions:

1. Are the public rules, mental-state labels, and scoring consistent?
2. Do legally inferred mental notes offer reproducible decision value in any prespecified situations, beyond what direct reasoning already achieves?
3. If value exists, is the limiting factor inference quality, how the policy uses notes, allocation, or compute overhead?

Better log score is evidence of better probabilistic prediction under a stated reference, not sufficient proof of calibration. Good performance with notes does not establish that the notes caused it. Treat both as questions to test.

## 4. Execution environment and resource autonomy

### Local or cloud

Choose whichever available environment is practical. You may move execution between authorized local/cloud sessions, run CPU checks remotely, and use already available inference endpoints. Record the choice and reason once; do not ask Ashraf to choose each time.

The known local workstation has WSL Ubuntu, an RTX 5090 with 32 GB VRAM, a working vLLM recipe, and local gpt-oss-20b. An API model has already been validated in the repository. Reuse working configurations before installing replacements. Do not assume a cloud session can reach a workstation's localhost endpoint or possesses its files, GPU, or credentials. If local weights are inaccessible, use another already authorized endpoint for a clearly labeled experiment, or move the job to the environment that has them. Do not silently merge different backends as one condition.

Switching execution location must not silently change task data, prompts, model revision, decoding, unit semantics, or scoring. Record actual hardware, endpoint, concurrency, and timing. Local and hosted latency are different measurements.

### Spending and credentials

The existing **USD 5 total paid-experiment cap remains in force**, including amounts already spent. Reconcile actual usage estimates at startup; approximately USD 3.69 may remain. Count any additional metered API or cloud-compute charges against the remaining allowance unless Ashraf supplies a separate explicit budget. Existing included/subscription resources do not create permission to purchase new capacity.

Use one authoritative spend ledger with in-flight reservations and atomic writes. Coordinate across processes/sessions; a thread lock in one process is insufficient for two cloud/local writers. Serialize billable jobs when cross-process coordination is unavailable. Preserve unresolved usage on ambiguous transport failures rather than treating it as proven zero cost.

Estimate each batch before dispatch. Keep enough allowance for retries and final evidence collection. Stop billable work at the cap; do not switch providers or omit unfavorable cases to continue it. You can still finish free analysis and reporting.

Use credentials through approved local/cloud secret facilities. Do not print keys, commit credential files, or ask Ashraf to paste a key into the research conversation. Do not make the workstation model endpoint publicly accessible merely to connect a cloud session.

## 5. What you may change independently

Within this block, you may:

- repair implementation, serialization, citation rendering, metric accounting, concurrency, and reproducibility bugs;
- clarify public wording so it faithfully describes existing simulator rules, without disclosing private episode truth;
- revise one grounding/abstention package and, if justified, one further note-integration or allocation-prompt variant;
- make schemas robust while preserving the same mental-variable meanings;
- compare existing validated models and supported inference settings under declared configurations;
- inspect model errors and implement meaningful regression checks;
- choose local/cloud scheduling and reuse safe intermediate results with accurate accounting;
- stop an unpromising branch and document why.

Do not independently:

- change the research question, mental-variable definitions, reward function, hidden-state transitions, or oracle information boundary;
- overwrite a frozen dataset, reinterpret old results as if run under a new contract, or turn inspected development data into a confirmatory test set;
- add a new environment version selected to defeat the previously successful baseline;
- start bulk label generation, controller fine-tuning, DAgger, large sweeps, Tier 2 collection, or a full new API-backed five-arm run;
- claim a general greedy guarantee, guaranteed oracle-content bound, or general human-ToM conclusion from these diagnostics;
- publish or submit work, change external sharing, or increase the spending cap.

If a prohibited scientific change is necessary, prepare a concrete recommendation and supporting evidence. Continue independent work; return early only if that unresolved choice blocks all remaining authorized work.

## 6. Bounded iteration loop

Run **at most three methodological revision rounds** in this block. Routine debugging that restores the declared behavior is not a new method variant, but log it. If the questions resolve in fewer rounds, stop and prepare the final handoff.

Before each round, append a short entry to `reports/autonomous-block/experiment-plan.md`:

```text
Question / hypothesis:
Change from the preceding version:
Configurations and data/context IDs:
What stays fixed:
Metrics, denominators, and inclusion rules:
Expected cost and maximum allocation:
What each possible outcome would imply:
```

Declare that entry before inspecting the round's new outputs. Run the relevant checks, execute the comparison, inspect failures, and record outcomes before choosing the next permitted action. Keep every tried configuration and its failures in an experiment registry. Do not report only the winning variant.

### Round 1 — Repair the contract and uncertainty package

Incorporate these research rulings without waiting for another review:

**Public rules (r4 or the next unused version):** clarify hearing a statement versus adopting its content versus attributing a belief to its speaker. Apply identical rules across compared conditions. Do not expect an LLM to distinguish hidden event types with indistinguishable public renderings. If the present evidence cannot resolve an interpretation, label the scoring reference ambiguous and report it separately rather than counting a proven model error.

Add a self-location rule only if tests establish it for the relevant facts and times, including movement. A person being physically in a room, remembering a meeting room, and knowing another person's belief are different facts. If the simulator does not implement a proposed rule, omit that rule from the clarification and document the limitation; do not quietly change the frozen world.

**Grounding package (pilot-v2.1 or next unused version):** distinguish the person's `unknown` mental content from the inferer's uncertainty and from full abstention. Broad distributions can be valid outputs. Permit grounded attributions when public evidence and verified rules support them. Do not use a self-reported probability threshold alone as proof of support, and do not use privileged truth to force deployment outputs. Preserve per-hypothesis evidence links in the notes actually shown to the policy.

**Scoring:** distinguish incorrect content, unsupported attribution, perspective leakage, uncertainty, and abstention/coverage. A correct lucky guess can lack support, and an uncertain prediction differing from one realized hidden state is not automatically hallucination. State how abstentions are scored. Reconcile all 24 contexts in category counts; the previous local/medium pilot-v2 row accounts for only 23 through its displayed categories.

Use the existing 24 fixed contexts. Start with local checks and a small evidence audit, then use the existing API model within budget. If measuring package improvement, compare packages under the same corrected public contract. Preserve older results; do not call a combined rules-and-prompt change a pure prompt effect.

### Round 2 — Replicated value-of-notes diagnostic

Start with the original **nine prespecified intervention states**, keeping their original labels, including the scalar-selected probes. They are a mixed diagnostic set, not nine certified cases of required mental reasoning. Record the selected unit or bundle for each state before outcomes.

With the same API policy and fixed allocation, compare four conditions:

1. **No explicit notes.**
2. **Inferred notes:** generated from legal visible evidence with the revised package.
3. **Grounded-reference notes:** the content distribution implied by the declared public model and the same visible history; no actual hidden-world identity, correctness flag, or action recommendation is allowed. Identify any reference-model knowledge beyond what the ordinary LLM prompt was given.
4. **Privileged true-content notes:** the actual selected mental content for the realized world, in the same representation. Label this privileged; it is not a guaranteed upper bound and is not deployable inference.

Freeze exact note payloads before policy outcomes and reuse them across **three fresh policy continuations per condition/state**. Record payload hashes. This measures policy variation conditional on those notes. Multiple draws from the same note generator are not identical notes, and repeated policy calls are not new independent scenarios.

Reset the same environmental state. Counterbalance condition order. Keep policy model/settings, task rules, retention/status logic, and legal observations fixed. Disable new allocations during these continuations. If refreshes are allowed, specify them symmetrically; do not supply free later hidden truth to only the privileged condition. Measure complete return, success, error, steps, and compute, rather than first-action flips alone.

Show note-generation cost separately from replicated policy cost. Experimental reuse of a note does not make it free in deployment. Keep variants grouped in all summaries and clearly distinguish scenario count, note samples, and policy draws.

Previously failed direct-agent instances may be analyzed in a separate **failure-selected exploratory slice**, not pooled into a primary estimate. They can improve on rerun through selection and sampling effects alone. Do not select new primary cases based on which model just failed.

Re-estimate cost for this four-condition design before dispatch. The earlier USD 1.5–2.5 estimate covered a different proposal. If needed, reduce the state count by a declared hash order before outcomes, or stage complete conditions within the remaining allowance. Preserve incomplete records; do not reduce the sample based on which condition wins.

### Round 3 — One evidence-driven follow-up, if needed

Choose **one** of the following based on the completed prior rounds and remaining budget, recording the reason first:

- If grounded-reference notes help but inferred notes do not, test one targeted inference/support repair on the existing contexts.
- If grounded or inferred notes are accurate but the policy mishandles them, test one note-integration change, such as a clearer evidence/uncertainty presentation, with the same contents and policy.
- If useful computation is visible and integration is adequate, test one compact selection/STOP prompt or a frozen few-shot router variant on development cases. Keep the unit pipeline fixed. Use separate synthetic/development demonstrations, report their provenance, and count routing cost. Do not train a learned router in this block.
- If an apparent gain is dominated by one sample or suspected note-length effects, spend the round on replication or one matched diagnostic control instead of another prompt variant.
- If none of these is justified, stop with a negative/inconclusive diagnosis. Round 3 is optional.

Do not change inference, policy, router, scenario distribution, and scoring together and then attribute the result to one component. If a shared bug correction forces a change, record its scope and rerun the affected comparison fairly.

## 7. Scientific invariants throughout the loop

- Actor prompts/features never read the actual hidden state, privileged labels, family/category names that reveal the intended solution, or gold actions. Privileged diagnostic conditions are explicit exceptions confined to their defined cells.
- A person can retain a false belief after the robot learns the contrary fact. Physical refutation alone does not invalidate a correct attribution of that person's belief.
- Current-action value and retained-memory value remain distinct under the agreed decomposition. Do not use a no-current-flip check to prune possible carryover/complementary value.
- Use `delta_J` for gross return gain and net VoMI only after applying a stated compute price. Report task return separately from cost-penalized utility.
- True mental content can help by revealing otherwise unavailable information, and can hurt a bounded policy through partial-model integration. It is a diagnostic, not automatically an upper bound.
- Baselines retain the same legal observations and ordinary language understanding. Do not force the direct agent into naive testimony assumptions to create headroom.
- Report tokens, calls, retries, incomplete outputs, actual elapsed time, and money. Tokenizers and hosted/local latency are not interchangeable compute measures.
- Extra-inference share of an arm's own tokens is not additional-token overhead relative to direct. Label both correctly.
- Preserve frozen dev-v1/dev-v2 and their hashes. Any bug that changes a dataset requires versioning and disclosure. New outcomes from inspected development contexts remain development outcomes.
- Maintain a consistent scoring reference. Report unresolved ambiguity instead of quietly relabeling a model answer to fit the desired narrative.

## 8. Stopping rules and allowed conclusions

Stop this block and produce the consolidated handoff when the first of these applies:

- the questions in §3 have a sufficiently clear development-level answer to recommend the next milestone;
- three methodological rounds are complete;
- the remaining paid allowance is exhausted or cannot cover the next declared comparison;
- a substantive research decision outside this authorization blocks further useful work;
- an execution/session limit requires a checkpoint and resume handoff.

Allowed conclusions include:

- **Usable grounded value signal:** recommend the next allocation-learning milestone, with evidence, limits, and cost. Do not begin it automatically.
- **Inference-limited:** grounded-reference notes help but current inferred notes do not; recommend a specific next inference improvement.
- **Privileged-information dependence:** only true-content notes help; revisit evidence availability and the label target before training.
- **Integration-limited:** accurate notes are not used well by the policy under this representation.
- **Little headroom here:** direct reasoning already exploits the evidence or physical search makes explicit modeling unnecessary in these cases. Propose, without implementing, a causally justified expansion within the original outline if appropriate.
- **Inconclusive:** uncertainty, insufficient budget, or unresolved scoring semantics prevent a defensible choice. State precisely what is missing.

Do not turn a nine-state diagnostic into a general claim about LLM theory of mind. Do not automatically pivot the paper after a negative pilot. No particular conclusion is required for this block to be successful.

## 9. Persistence and handoff requirements

Maintain `reports/autonomous-block/checkpoint.md` with completed rounds, exact current state, running jobs, spend including reservations, artifact paths, and the next command/action. Save after each completed batch and before session boundaries. Stop unused GPU/API/cloud services where appropriate. Resume from the checkpoint; do not restart completed comparisons or reset the budget in a new session.

If the runtime stops, provide a truthful resume checkpoint. Do not claim background execution or future continuation unless the execution environment actually supports it.

Return **one consolidated bundle** containing:

1. `reports/autonomous-block/FINAL_REVIEW.md`: recommendation first; what was tested; per-round changes; results and uncertainty; failure mechanisms; limitations; total spend; and the next research decision.
2. `reports/autonomous-block/experiment-registry.csv` or JSON: every attempted configuration, data/context IDs, hypothesis, model/settings, prompt/schema/renderer versions, run/commit/hash, outcomes, failures, and cost. Include negative and stopped branches.
3. Corrected all-context coverage/classification/proper-score tables, with clear denominators and an explicit ambiguity policy.
4. Per-state, per-condition, per-replicate return/action/compute records and exact note payload hashes. Include representative successful, failed, and ambiguous traces with visible/private separation.
5. Exact revised prompts/rules/schema and readable diffs; relevant scoring, graph, and invariant-test excerpts; actual commands and test outcomes.
6. Manifests, code/prompt/data hashes, dirty-path provenance, usage/spend summary, and the final checkpoint. Include a compact source-only archive or focused diff so the research conversation can inspect it.

Keep the main review compact, approximately 2–4 pages of Markdown, with detailed evidence in referenced files. Do not send weights, credentials, or large uncurated run directories. In the final user message, link the review and bundle, state the recommended next step, and list only decisions that genuinely require research review.

**Begin by inspecting the existing state and ledger, register this block, choose the execution environment, and continue through the loop. Do not return merely to say that preparation is complete.**
