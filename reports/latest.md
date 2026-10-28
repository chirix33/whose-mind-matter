# Milestone report — Stage 0 + smallest Stage 1 examples (2026-10-28)

**Claims/RQs addressed:** none evaluated. This milestone is infrastructure plus the scientific contract. The tiny cases are executable constructions for P1, P3a, P3b, P5 and depth certification (RQ6 groundwork, C4 groundwork).

**Environment:** every command below ran on the workstation: Windows 11 host, WSL2 Ubuntu 24.04.5, RTX 5090 32 GB, driver 610.60. Details: `docs/research/environment.md`.

## What exists
- **Repo:** branch `main`. Commits `e5b4f15` (Stage 0) and `a71bb7c` (regenerated tiny-case table). No remote. `.gitattributes` forces LF and stores the checksummed source documents byte-for-byte. Layout follows AGENTS §6; see `README.md`.
- **Source outline:** preserved verbatim at `docs/research/methods-experiments-v2.md`, SHA-256 `8cc540f0…22d7d`; see `docs/research/source-manifest.md`.
- **Simulator** (`src/officeminds/`): deterministic seeded Tier 1 world with private minds, sincere tells vs. insincere claims, nested beliefs, robot-visible observations, a privileged trace kept separate, and JSON replay.
- **Exact symbolic oracle** (`src/vomi/oracle.py`): exact Bayesian conditioning by replay, belief-space expectimax, J(S), VoMI, flip probability with the decomposition residual, content entropy, exhaustive gold sets (three definitions), effective depth, and indistinguishable world pairs.
- **Visible-only candidate generation** (`src/vomi/units.py`).
- **Model client:** stdlib OpenAI-compatible client plus mock (`src/vomi/clients.py`), run manifests (`src/vomi/runlog.py`), model config (`configs/models/local_gpt_oss_20b.json`).
- **Spec and decisions:** `docs/research/implementation-spec.md`; six proposed decisions D-001…D-006; `docs/decisions/discrepancy-log.md` (12 rows); `docs/research/roadmap.md` (C1–C5 / RQ1–7 / baseline status); `docs/research/baseline-fidelity.md` (stub).

## Commands run and outcomes
| Command | Outcome |
|---|---|
| `~/venvs/officeminds/bin/python -m pytest -q` | **46 passed** in 9.3 s (CPU only), at commit `e5b4f15` |
| `python scripts/run_tiny_cases.py --seed 0` | 10 cases; all replays identical; run **`tiny-20261028-032629-565fb8`** (commit `e5b4f15`, clean tree) |
| `bash scripts/serve_local_model.sh` | gpt-oss-20b served after three fixes (see environment.md); engine init 26.6 s |
| `python3 scripts/smoke_local_model.py --n 10 --concurrency 4` | run **`smoke-20261028-032706-260d3d`** (commit `a71bb7c`, clean tree); results below |

Manifests: `~/officeminds-runs/{tiny,smoke}/<run_id>/manifest.json` (WSL). The runs cited here record a commit hash and `git_dirty: false`.

Earlier runs on the uncommitted tree are kept on disk but superseded: `tiny-20261028-032629-565fb8`, `tiny-20261028-032310-90b650`, `tiny-20261028-032315-8982a4`, `smoke-20261028-031813-05c2f6`. The clean re-runs reproduced every label value. Episode returns differ only by seed. The smoke numbers stayed within ±0.02 s median latency.

## Results (exact symbolic oracle, record A — see D-001 before interpreting)
| Case | J(∅) | J(all candidates) | ℓ* | Minimal sufficient sets |
|---|---|---|---|---|
| depth0_visible | 0.9500 | 0.9500 | 0 | {} |
| depth1_knowledge | 0.8250 | 0.9500 | 1 | {K(alice)} ← uninferable-content issue (D-001) |
| distractor_plausible | 0.8375 | 0.9500 | 1 | {K(alice)} |
| distractor_obvious | 0.8250 | 0.9500 | 1 | {K(alice)}; K(carol) pruned (constant content) |
| substitutes | 0.9000 | 0.9500 | 1 | four singletons; no LOO-necessary unit |
| depth2_handoff | 0.8000 | 0.9000 | **2** | {K(alice), K(rec→alice)}, {K(alice), K(alice→rec)} |
| stakes m1 / m4, q = 0.975 | 0.9125 / 0.8750 | 0.95 | 1 | R(bob): ΔJ 0.0375 / 0.075, P(flip) 0.025 / 0.025 |
| stakes m1 / m4, q = 0.95 | 0.8750 / 0.8450 | 0.95 | 1 | R(bob): P(flip) 0.05 / **1.0** (P5 caveat) |

All of these match the hand derivations in spec §6. Full per-unit table: `reports/tiny-cases.md`.

**Local model smoke** (gpt-oss-20b, vLLM 0.32.0, Triton attention, MXFP4/MARLIN MoE, temperature 0, reasoning effort low, one 276-token decision prompt from `depth1_knowledge`):
| Mode | n | Valid JSON + legal action | Median latency | Median completion tokens |
|---|---|---|---|---|
| prompt-only | 10 | 100% | 0.226 s | 59 |
| JSON-schema constrained | 10 | 100% | 0.237 s | 62 |
| schema, 4 concurrent | 8 | 100% | 0.296 s | 61 |

- Concurrent batch: 0.60 s wall clock vs. 2.37 s sum of latencies (13.4 requests/s).
- GPU memory with the server up: 29,284 MiB.
- Reasoning text and reasoning-token counts are reported by the server.
- Every call chose `ask(rec,alice_loc)`, the same as the exact oracle's a(∅) for this case. These are **10 repeats of one prompt at temperature 0**, not independent samples and not an evaluation.

## Failures and problems found
1. **Simulator bug (fixed):** sincere tellers did not hold the belief they told, so `K(alice) = unknown` leaked hidden state. Caught because the hand value for `depth2_handoff` disagreed (oracle 0.90 vs. hand 0.85). A regression test was added.
2. **vLLM serving failed three times** before working: no system `nvcc`; `ninja` not on PATH; FlashInfer JIT header mismatch. Worked around with environment variables plus `--attention-backend TRITON_ATTN`. The existing venv was not modified. The FlashInfer path may be faster; that is untested.
3. **Scientific issues surfaced by the exact labels:** D-001 (labels reward uninferable minds), D-002 (§3.4 decomposition fails under retention), D-003 (outline gold definition is empty under substitutes), D-006 (naive stakes pairs change flip probability). Plus a tie-break artifact that makes flip-probability labels asymmetric in a symmetric scene.

## Limitations
- Ten hand-built tiny cases only; no balanced generator yet.
- Cost c(u) = 1 call is a placeholder.
- The perspective graph and memory are specified but not implemented.
- Records 2 and 3 (LLM labels) are not implemented.
- The "independent check" is brute-force search for point-mass beliefs plus hand derivations. There is no second implementation of belief-space expectimax.
- GPU memory figures are the server's reservation, not a measured peak.

## Resource usage
Local only: no paid APIs, no downloads except pytest into a new venv. The GPU was used only for the smoke test. The vLLM server is **still running** in WSL on 127.0.0.1:8000 and holds about 27 GB of VRAM. Stop it when it's not needed.

## Next actions
1. Research review of D-001…D-006 (`reports/review-request.md`).
2. Meanwhile, the review-independent Stage 1 work: holder-permutation pair, relevance shift (F3), path asymmetry (F6), a stakes ranking-change pair, P2 gap-bound tests, trajectory-flip computation, and perspective-graph memory records.
3. After D-001: implement record-B labels and re-derive the tiny-case expectations by hand.
