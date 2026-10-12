# Q7 · Benchmark Like a Pro: TTFT, ITL and the lie of averages

**Needs:** one GPU with vLLM installed (24 GB+ recommended) · **Time:** 45 min · **Episodes:** E17, E24 · **XP:** +75
**[繁體中文](Q7-benchmark-like-a-pro.zh-TW.md)**

"It's 2× faster" means nothing without a workload, a baseline and percentiles. You'll run one honest A/B experiment, prefix caching off vs on, and write it up the way performance engineers do. This kind of write-up is portfolio material that gets interviews.

> ⚠️ **Not yet validated by a maintainer.** Flags change between vLLM releases, so check `vllm bench serve --help` for your version. Record your vLLM version, GPU, driver and exact commands; without them, the numbers mean nothing.

## 1. Write the hypothesis first

Decide what you expect *before* measuring. Our workload: 200 requests, each with a 1,536-token shared prefix plus 512 unique tokens and 128 output tokens, at 8 requests/s.

```text
Hypothesis: with prefix caching ON, TTFT p50 and p99 drop sharply because 75% of every prompt is reused;
output throughput rises modestly; median ITL barely changes (decode work is the same), but p99 ITL may
drop because smaller prefill chunks share steps with decode.
```

> ✅ **Checkpoint:** your hypothesis names the metric, the direction and *why*. Copy `templates/EXPERIMENT_REPORT.md` from the vllm-academy repo and paste it in.

## 2. Record the environment

You can't reproduce results you can't describe.

```bash
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__)"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv  # or: rocm-smi --showproductname
```

> ✅ **Checkpoint:** the versions and GPU are pasted into your report.

## 3. Run A: prefix caching OFF

Start the server with caching disabled, then benchmark from a second terminal. Use a fixed seed so both runs send identical prompts.

```bash
vllm serve Qwen/Qwen3-8B --no-enable-prefix-caching --max-model-len 4096 --port 8000
# second terminal:
vllm bench serve --model Qwen/Qwen3-8B --dataset-name random --random-prefix-len 1536 --random-input-len 512 --random-output-len 128 --num-prompts 200 --request-rate 8 --seed 0 --percentile-metrics ttft,tpot,itl,e2el --metric-percentiles 50,90,99 --save-result --result-filename off.json
```

> ✅ **Checkpoint:** `off.json` exists, and the console shows TTFT, TPOT and ITL at p50, p90 and p99, plus output token throughput.

## 4. Run B: prefix caching ON

**Restart the server.** Otherwise run A's leftovers pollute run B. Prefix caching is on by default.

```bash
vllm serve Qwen/Qwen3-8B --max-model-len 4096 --port 8000
# second terminal: same bench command, different file name
vllm bench serve --model Qwen/Qwen3-8B --dataset-name random --random-prefix-len 1536 --random-input-len 512 --random-output-len 128 --num-prompts 200 --request-rate 8 --seed 0 --percentile-metrics ttft,tpot,itl,e2el --metric-percentiles 50,90,99 --save-result --result-filename on.json
```

> ✅ **Checkpoint:** `on.json` exists. Glance at `/metrics` for the prefix-cache hit counters to confirm caching actually happened.

## 5. Compare like a pro

Print the deltas side by side. Report percentiles, never just the mean, and repeat each run 3 times if you can, so you know your noise level. Restart the server (or change `--seed`) between repeats; otherwise repeat 2 hits the cache on the *whole* prompt and inflates the win.

```python
import json
a, b = json.load(open("off.json")), json.load(open("on.json"))
for k in ["output_throughput", "p50_ttft_ms", "p99_ttft_ms", "p50_itl_ms", "p99_itl_ms"]:
    if k in a and k in b:
        print(f"{k:<20} off={a[k]:>9.1f}  on={b[k]:>9.1f}  change={100 * (b[k] - a[k]) / a[k]:+6.1f}%")
```

> ✅ **Checkpoint:** you have a table of changes. Did TTFT move in the direction you predicted? If ITL changed a lot, can you explain why?

## 6. Stress the claim

A result you can't break is a result you can trust. Change **one** variable: drop the shared prefix to 0, or double the request rate. Watch which metric changes and which doesn't. Run it against both servers (caching OFF and ON, restarting in between).

```bash
vllm bench serve --model Qwen/Qwen3-8B --dataset-name random --random-prefix-len 0 --random-input-len 2048 --random-output-len 128 --num-prompts 200 --request-rate 8 --seed 0 --save-result --result-filename noprefix.json
```

> ✅ **Checkpoint:** with no shared prefix, caching ON gives no TTFT win, which shows the win came from reuse and not from noise.

## 7. Bonus: speculative decoding (E17)

Restart with an n-gram drafter (no extra model needed), rerun the benchmark, and compare ITL and throughput. Random-token prompts give n-gram matching almost nothing to work with. Explain why that makes this an unfair test, and which workload would be fair (code editing, RAG).

```bash
vllm serve Qwen/Qwen3-8B --max-model-len 4096 --speculative-config '{"method": "ngram", "num_speculative_tokens": 4, "prompt_lookup_max": 4}'
```

> ✅ **Checkpoint:** you can say why the speedup depends on acceptance rate and workload, with your own numbers as evidence.

## 8. Publish the report

Fill in the template: hypothesis, environment, exact commands, raw JSON, table, one chart, what surprised you, and threats to validity. Post it in `#show-your-work`. Gist it or blog it, then link it on your CV (E26).

```text
Title: Prefix caching on Qwen3-8B: TTFT p99 −X% on a 75%-shared-prefix workload (vLLM 0.31, 1× <GPU>)
```

> ✅ **Checkpoint:** someone else in the community can rerun your exact commands from your report.

## What you learned

- Hypothesis first, one variable at a time, restart between runs, fixed seeds.
- Percentiles (p50/p99) tell the story; averages hide the tail your users feel.
- Every speedup has a workload attached. Name it, or the claim is meaningless.
