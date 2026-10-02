#!/usr/bin/env bash
# Run INSIDE a correctly installed vLLM CUDA/ROCm environment. Does not install it.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
: "${BACKEND:?Set BACKEND=cuda or BACKEND=rocm to detect wrong-wheel installs}"
[[ "$BACKEND" == cuda || "$BACKEND" == rocm ]] || { echo 'Invalid BACKEND' >&2; exit 2; }
MODEL="${MODEL:-Qwen/Qwen2.5-0.5B-Instruct}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
TP="${TP:-1}"
EAGER="${EAGER:-1}"
PREFIX_CACHING="${PREFIX_CACHING:-0}"
RUN_DIR="${RUN_DIR:-$ROOT/results/server-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
mkdir -p "$RUN_DIR"
command -v vllm >/dev/null || { echo 'Install the platform-specific vLLM build first.' >&2; exit 2; }
python "$ROOT/labs/collect_env.py" --expect "$BACKEND" --output "$RUN_DIR/environment.json"
args=(serve "$MODEL" --served-model-name "$MODEL" --host "$HOST" --port "$PORT"
      --tensor-parallel-size "$TP" --max-model-len "${MAX_MODEL_LEN:-4096}"
      --max-num-seqs "${MAX_NUM_SEQS:-16}" --max-num-batched-tokens "${TOKEN_BUDGET:-1024}"
      --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION:-0.8}" --seed 7
      --generation-config vllm)
case "$EAGER" in 1) args+=(--enforce-eager);; 0) ;; *) echo 'EAGER must be 0 or 1' >&2; exit 2;; esac
case "$PREFIX_CACHING" in
  1) args+=(--enable-prefix-caching);;
  0) args+=(--no-enable-prefix-caching);;
  *) echo 'PREFIX_CACHING must be 0 or 1' >&2; exit 2;;
esac
[[ -z "${MODEL_REVISION:-}" ]] || args+=(--revision "$MODEL_REVISION" --tokenizer-revision "$MODEL_REVISION")
# No blanket AITER, quantization, or attention-backend flags: first establish the default path.
printf '%q ' vllm "${args[@]}" "$@" > "$RUN_DIR/command.txt"
printf '\n' >> "$RUN_DIR/command.txt"
printf 'Evidence directory: %s\n' "$RUN_DIR"
vllm "${args[@]}" "$@" 2>&1 | tee "$RUN_DIR/server.log"
