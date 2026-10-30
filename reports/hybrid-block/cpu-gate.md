# Hybrid block (D-019): CPU gate record

Date: 2026-10-30, written before any model call in this block.
- Environment: Windows Python 3 for the gate script; WSL `~/venvs/officeminds` for pytest; WSL `~/venvs/vllm` transformers, used only for the offline tokenizer.
- Code: `src/vomi/relational.py`, `src/officeminds/hybridfam.py`, `scripts/hybrid_cpu_gate.py`, `scripts/hybrid_trigger_audit.py`, `scripts/hybrid_token_forecast.py`, `tests/test_hybrid.py`.
- Numbers: `cpu-gate.json`, `trigger-audit.json` (per-episode rows in `trigger-audit-rows.jsonl`), `token-forecast.json`.

## Verdict

- **The common foundation is sound.** Joint relations are exact and match an independent calculation in every hidden world. The information boundary has zero violations. Observed evidence, queried mental variables and action consequences are kept separate.
- **The hybrid's selection economics fails in this regime.** After cheap compilation, no relational computation is costly:
  - one relation costs 17–28 µs of CPU and 0 tokens;
  - computing *all* relations costs 19–31 µs, because the latent enumeration is shared;
  - one policy decision costs about 1,660 tokens of GPU work (1,465 prompt + 195 completion, measured).

  A selector can therefore save at most about 10 µs per decision. Any informative estimate of a computation's decision value needs the same posterior enumeration it would replace.
- **So H1 (selective) can at best tie H5 (dense encode-once) on every resource.** The hybrid's §5(2) criterion cannot be met, and it would be clearly dominated or matched by the cheap tracker.
- **Under brief §3 this is a hybrid-specific failure.** The block moves to the Concept 2 fallback (§6) without running the 768-episode hybrid pilot. The fallback's trigger audit (below) finds a meaningful opportunity.

There *is* a nontrivial decision-value structure; the table below shows it. It has no resource consequence here only because every computation that could be selected is effectively free.

## 1. Qualification: joint relations vs an independent calculation

- **Families:** `src/officeminds/hybridfam.py`. These are minimally changed dev-v3 constructions with the r6 event semantics. The only changes are the supports and event orders listed in the module docstring.
- **Setup:**
  - 4 qualification seeds (20261500–03, public draws), both stakes levels;
  - **every positive-prior hidden world**, not one draw;
  - for `seq`, five scripted robot histories, including one where the robot misses step 1.
- **Engine:** `ReferentEngine` (terms with provenance, shared latents, exact enumeration).
- **Reference:** world enumeration under the same public model (`ExactOracle` posterior; for each world, the courier's actual route compared with the recipient's room).

| check | result |
|---|---|
| relation P(route = recipient location) and recipient-location marginal, engine vs enumeration | **1,008 checks, 0 mismatches** (tolerance 1e-9) |
| information boundary, dynamic: every world sharing a visible history gives the identical engine output | 1,440 world-histories, **0 violations** |
| information boundary, static: `relational.py` code for `.minds`, `people_rooms`, `.hidden`, `World(`, oracle, `PersonMind`, `.facts`, `timed_events`, `world.log`, privileged | **0 occurrences** |
| cache: reused / refreshed value equals a fresh computation (all `seq` histories, both return draws) | **all equal** (`tests/test_hybrid.py`) |
| full test suite (WSL, `~/venvs/officeminds`) | **318 passed** |

## 2. Joint relations reproduce the intended contrasts (seed 20261500)

Gate inputs: `J = -0.05 + p - (1-p)*0.5*stakes`; V_alt is the declared in-person search from the lobby; ×1 values are shown.

| case | courier | route marginal | recipient marginal | P(equal), joint | P(equal), product of marginals | gate (joint) | gate (product) | Bayes action |
|---|---|---|---|---|---|---|---|---|
| 2d (N heard 2nd move) | yara | ½ / ½ | ½ / ½ | **1** | 0.5 | allow (0.95 ≥ 0.80) | veto | give(yara) |
| 2d (H heard 1st move) | ravi | ½ / ½ (identical) | ½ / ½ | **0** | 0.5 | veto | veto | — |
| 3a (F told R) | grace | ½ / ½ | ½ / ½ | **1** | 0.5 | allow | veto | give(grace) |
| 3b (R told separately) | vik | certain (R's statement) | ½ / ½ | 0 | 0 | veto | veto | ask (then search) |
| 3c (R not told) | sara | certain | certain | 1 | 1 | allow | allow | give(sara) |
| 2e (plan kept w.p. ¾) | grace | ½ / ½ | ½ / ½ | **¾** (uncertain provenance) | 0.5 | veto (0.575 < 0.80) | veto | search |

What the table shows:
- **2d is the representation-necessity case.** Physical state and every marginal are identical; only the event order (who heard the later move) differs. The best decision differs, and independence-based marginal notes would veto the correct handoff.
- **2e is the uncertain-provenance case.** Union-find equalities cannot represent it; exact enumeration does.
- **3b vs 3c** have the same certain route. The relation depends on R's provenance, which is the K(F→R) + K(R) complement that the integration block found unallocated.

**Separation of evidence, mental variables and consequences** (2d, robot asks ravi):
- ravi's term stays `<Q1>`: an answer changes no one's state.
- The robot's estimate collapses: ravi's route marginal goes from ½ / ½ to 1 on one office, and the recipient marginal becomes certain.
- Both relations are unchanged (1 and 0).
- The gate (consequence) is computed only from the engine's outputs.

**Reuse / refresh / unobserved change** (`seq`; ops logged per step):
- Robot watching, R returns: at t1 both couriers' relations are refreshed (person-state change). At t2 they are reused (N's arrival is not a dependency). Bayes action: give(H).
- Robot watching, R does not return: everything is reused. Bayes action: give(N).
- Robot away at t1: both relations are refreshed to P = ½ as an unobserved-interval change, never silently reused as fresh. Bayes action: ask.

## 3. Decision-value structure (seed 20261500)

Exact gain in expected return of the shared interface from one computation.
- **safe default:** without the computation, that commitment is not considered.
- **commit default:** the proposed give executes unless checked, so the gain is the value of a veto.
- L = recipient-location marginal.

| state | L | relation gains (safe default; commit default) | reading |
|---|---|---|---|
| 3a, 3c, 2d-N | 0 | +0.10 to +0.15; 0 | compute the relation: it licenses a handoff |
| 3b, 2d-H, 2e | 0 | 0; +0.23 to +3.0 | worth computing only to veto a proposed handoff |
| stop_visible | 0 | 0; (veto value only) | STOP: deliver() is certain |
| stop_announced | +0.10 | 0 given L | STOP for relations once the announcement is used |
| seq, R returned (watched) | 0 | H +0.41; N veto 1.5–3.0 | refresh changes *which* courier is right |
| seq, no return (watched) | 0 | N +0.15 (reuse) | reuse |
| seq, robot away at t1 | 0 | 0; +0.33 / +1.08 | no relation licenses a commit (ask instead) |

So different states justify different queries, reuse, refresh and STOP, and stakes change the veto values. What is missing is any cost to trade against: see §4.

## 4. Cheap compiler costs (median of 200 runs, Windows CPU, µs)

| construction | index build | one relation (incl. compile) | all relations + location | world enumeration (independent) | worlds |
|---|---|---|---|---|---|
| 3a / 3b / 3c | 6–7 | 17–19 | 19–20 | 264–284 | 6 |
| 2d / 2e | 6–9 | 23–25 | 27–30 | 239–355 | 6 / 12 |
| stop_visible / stop_announced | 7–9 | 23–28 | 27–31 | 384–429 | 12 |
| seq | 7 | 18 | 21 | 894 | 24 |
| dev-v3 1a…4c (fallback checker, world enumeration at t0) | — | — | — | 93–1,379 (4b: 30 worlds) | 3–30 |

Not exercised, and outside this regime: compiling an *unseen* public-model template from text. Here the structured public models are hand-compiled once per template (engineering cost, not runtime). For new templates this would be one parse per task (about 1.2–1.6k prompt tokens, from the t0 task-card sizes in §6). It covers all persons and paths at once, so selecting persons or paths would not reduce it.

## 5. Fallback trigger-coverage audit (existing no-note traces)

`scripts/hybrid_trigger_audit.py` (CPU, 37 s). Source: repair-block Stage 2, condition `none`, **1,152 episodes** (seeds 20261100–23, already inspected development data). The public-model checker is applied counterfactually at every recorded irreversible commitment.

| quantity | value |
|---|---|
| mean return (direct) / mean Bayes value V*(h0), evaluation only | 0.381 / 0.885 |
| lost return vs Bayes per episode: total / in error episodes / timeouts / successes | 0.504 / **0.398** / 0.073 / 0.033 |
| commitment triggers / wrong / right | 805 / 205 / 600 |
| gate vetoes of wrong / of right (ex-post lucky) commitments | **196 of 205** / 161 of 600 |
| wrong commitments allowed (ex-ante J ≥ V_alt) | 9 |
| optimistic gain, ideal continuation after the first veto (diagnostic only) | +0.350 per episode |
| episodes with no commitment where the Bayes first action commits (missed opportunity) | 213 (lost 0.060 per episode); a veto gate cannot recover these |

**By class:**
- **Social-belief handoffs (give):** 248 triggers, 80 wrong, all 80 vetoed, 0 right vetoed.
- **Physical drops:** 397 triggers, 102 wrong, 100 vetoed, 96 right vetoed. These are mostly p ≈ ½ drops that happened to succeed.
- **Testimony-reliability drops (4b/4c):** 160 triggers, 23 wrong, 16 vetoed, 65 right vetoed. These are mostly ×4 drops where searching has the higher expected value.

**Losses concentrate in 1b, 2b, 2c and 3b** (error rates 0.29–0.60, larger at ×4). 1a/1c/3a/3c lose little. The brief's opportunity condition holds, so the fallback proceeds.

## 6. Token and runtime forecast (actual tokenizer)

`scripts/hybrid_token_forecast.py` uses the gpt-oss-20b HF tokenizer and chat template on the rendered t0 prompts (`rendered-t0.json`).

| prompt at t0 | tokens (range over the 12 constructions) |
|---|---|
| policy decision | 1,177–1,575 (server-measured 1a: 1,185) |
| generic check | 1,170–1,546 |
| re-decision after a veto | 1,227–1,625 (+50: the veto line) |

Measured from the 1,152 direct traces: 3.1 decisions per episode, 1,465 prompt and 195 completion tokens per decision attempt. That is about 5.1k processed tokens per direct episode.

Planning forecast, not a measurement:
- generic_gate adds about 0.7 checks and 0.3 re-decisions per episode, roughly 1.7k tokens;
- checker_gate adds only re-decisions, roughly 0.5k tokens;
- ask_first adds about one step.
- 1,536 episodes is roughly 5,500 calls, about 25–35 min at the measured local throughput (about 230 decisions per minute at concurrency 8). That is within the 2 h serving cap.

## 7. Branch protocol

- The hybrid pilot (H0–H5, 768 episodes) is **not run**.
- The fallback runs under `reports/hybrid-block/fallback-protocol.md`, frozen and hash-pinned in `fallback-freeze.json` before any pilot outcome. It contains the conditions, gate state machine, caps, seeds and analysis rule.
- Interface smoke probes (at most 48 of the 96 allowed) run before the freeze, to catch code and schema failures only.
