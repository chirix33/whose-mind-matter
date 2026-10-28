# Environment inventory (measured 2026-10-28)

All commands ran on the workstation itself, a Windows 11 Enterprise host with WSL2 Ubuntu 24.04.5. No secrets or environment dumps are recorded here.

## Hardware and OS
| Item | Value | Where measured |
|---|---|---|
| GPU | NVIDIA GeForce RTX 5090, 32,607 MiB (≈2 GiB used by Windows desktop at idle) | `nvidia-smi` on Windows and in WSL |
| Driver | 610.60 | `nvidia-smi` |
| Host RAM | 63.5 GiB total | Windows CIM |
| WSL RAM | 31 GiB visible to WSL | `free -g` in WSL |
| Disk | C: 1.3 TB free; WSL root 644 GB free | `df -h` |
| WSL kernel | 6.18.33.2-microsoft-standard-WSL2 | `uname -r` |
| System `nvcc` | none (`/usr/local/cuda` absent) | WSL |

## Python environments
| Env | Python | Contents | Use |
|---|---|---|---|
| Windows `py` | 3.14.7 | — | not used for this project |
| WSL `/usr/bin/python3` | 3.12.3 | stdlib | smoke script (stdlib-only) |
| `~/venvs/vllm` (pre-existing, **unmodified**) | 3.12.3 | vLLM 0.32.0, torch 2.13.0+cu132 (CUDA available), transformers 5.19.0, openai 3.36.0, pydantic 2.14.1, flashinfer 0.7.0.post1, triton 3.7.1; pip `nvcc` at `site-packages/nvidia/cu13/bin`, `ninja` in `bin/` | model serving |
| `~/venvs/hf` (pre-existing) | 3.12.3 | empty of ML packages | unused |
| `~/venvs/officeminds` (**new, isolated**) | 3.12.3 | pytest 9.2.0 only | CPU test suite |

The project's code is stdlib-only, so the simulator, oracle and client need nothing beyond Python ≥ 3.11.

## Local model weights (HF cache `~/.cache/huggingface/hub`, 86 GB total)
| Model | Size on disk | Notes |
|---|---|---|
| `openai/gpt-oss-20b` @ `6cee5e81ee83917806bbde320786a8fb61efebee` | 13 GB | agent-backbone pilot candidate; native MXFP4 |
| `nvidia/Qwen3.6-27B-NVFP4` | 21 GB | possible second family (Qwen); **not approved or tested** |
| `nvidia/Gemma-4-31B-IT-NVFP4` | 31 GB | possible second family (Gemma); not approved or tested |
| `RedHatAI/gemma-4-31B-it-NVFP4` | 22 GB | Gemma family; not approved or tested |

There is no Ollama binary in WSL, nothing listening on :11434, and no Ollama API key assumed.

## Serving gpt-oss-20b (working recipe)
`scripts/serve_local_model.sh` (config: `configs/models/local_gpt_oss_20b.json`). Getting there took four attempts. Each failure is recorded so it isn't repeated:
1. Default `vllm serve` failed: CUDA-graph profiling wants `nvcc`, and there is no system CUDA toolkit. **Fix:** `CUDA_HOME` points at the venv's pip CUDA (`nvidia/cu13`).
2. Then `ninja` was not on PATH, because the venv was not activated. **Fix:** prepend `~/venvs/vllm/bin`.
3. Then FlashInfer's JIT build failed: "CUDA compiler and CUDA toolkit headers are incompatible" (the pip headers and FlashInfer's bundled CCCL disagree). **Fix:** `--attention-backend TRITON_ATTN`, which avoids the FlashInfer JIT. The MoE runs on the MARLIN MXFP4 backend.
4. Working. Measured from the server log: model load 13.8 GiB in 7.5 s; torch.compile 8.4 s; engine init 26.6 s; KV cache 11.17 GiB = 387,686 tokens; max concurrency 23.7× at 16,384 tokens per request. GPU memory with the server up: 29,324 MiB used. That is the reservation set by `--gpu-memory-utilization 0.85`, not an activation peak.

Consequence: with the backbone server up, the GPU has **no room for a second concurrent model** (role-player or controller training). Run those jobs sequentially, or lower the utilization and re-measure.

## Commands (all actually run)
```bash
# CPU-only test suite (WSL)
~/venvs/officeminds/bin/python -m pytest -q
# Tiny-case exact oracle labels + replayed episodes (CPU)
~/venvs/officeminds/bin/python scripts/run_tiny_cases.py --seed 0
# Local model: serve, then smoke test (WSL)
bash scripts/serve_local_model.sh            # long-running
python3 scripts/smoke_local_model.py --config configs/models/local_gpt_oss_20b.json --n 10 --concurrency 4
```
Raw outputs live outside Git under `~/officeminds-runs/` (WSL), at `{serve,smoke,tiny}/<run_id>/`.
