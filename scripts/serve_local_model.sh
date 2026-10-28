#!/usr/bin/env bash
# Serve the installed gpt-oss-20b snapshot with the existing vLLM venv (WSL, offline, no downloads).
# Settings mirror configs/models/local_gpt_oss_20b.json. Logs go outside Git.
set -euo pipefail
export HF_HUB_OFFLINE=1
export CUDA_HOME="$HOME/venvs/vllm/lib/python3.12/site-packages/nvidia/cu13"
export PATH="$HOME/venvs/vllm/bin:$CUDA_HOME/bin:$PATH"
LOG_DIR="${OFFICEMINDS_RUNS:-$HOME/officeminds-runs}/serve"
mkdir -p "$LOG_DIR"
exec "$HOME/venvs/vllm/bin/vllm" serve openai/gpt-oss-20b \
  --served-model-name gpt-oss-20b \
  --host 127.0.0.1 --port 8000 \
  --max-model-len 16384 --gpu-memory-utilization 0.85 \
  --attention-backend TRITON_ATTN \
  >"$LOG_DIR/vllm-serve-$(date +%Y%m%d-%H%M%S).log" 2>&1
