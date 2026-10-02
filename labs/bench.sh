#!/usr/bin/env bash
# Synthetic workload only; not a quality evaluation. Run after serve.sh and smoke_client.py.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${MODEL:-Qwen/Qwen2.5-0.5B-Instruct}"
TOKENIZER="${TOKENIZER:-$MODEL}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
REQUEST_RATE="${REQUEST_RATE:-inf}"
CONCURRENCY="${CONCURRENCY:-4}"
INPUT_LEN="${INPUT_LEN:-512}"
OUTPUT_LEN="${OUTPUT_LEN:-128}"
NUM_PROMPTS="${NUM_PROMPTS:-64}"
RUN_DIR="${RUN_DIR:-$ROOT/results/bench-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
mkdir -p "$RUN_DIR"
command -v vllm >/dev/null || { echo 'Install vLLM first.' >&2; exit 2; }
vllm bench serve --help > "$RUN_DIR/bench-help.txt"
python "$ROOT/labs/collect_env.py" --output "$RUN_DIR/client-environment.json" >/dev/null
args=(bench serve --backend openai --base-url "$BASE_URL" --endpoint /v1/completions
      --model "$MODEL" --tokenizer "$TOKENIZER" --dataset-name random
      --random-input-len "$INPUT_LEN" --random-output-len "$OUTPUT_LEN"
      --num-prompts "$NUM_PROMPTS" --request-rate "$REQUEST_RATE"
      --max-concurrency "$CONCURRENCY" --seed 7 --ignore-eos
      --percentile-metrics ttft,tpot,itl,e2el --metric-percentiles 50,95,99
      --save-result --save-detailed --result-dir "$RUN_DIR" --result-filename metrics.json)
printf '%q ' vllm "${args[@]}" "$@" > "$RUN_DIR/command.txt"
printf '\n' >> "$RUN_DIR/command.txt"
vllm "${args[@]}" "$@" 2>&1 | tee "$RUN_DIR/benchmark.log"
