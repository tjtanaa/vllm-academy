# Q1 · First Token: your own vLLM server in 15 minutes

**Needs:** a free Google Colab GPU, or any NVIDIA/AMD GPU with vLLM installed · **Time:** 15 min · **Episodes:** E01, E02, E28 · **XP:** +75
**[繁體中文](Q1-first-token.zh-TW.md)**

By the end you'll have a live OpenAI-compatible server, you'll have watched tokens stream out one at a time, and you'll know where the startup log hides the KV-cache size.

> ⚠️ **Not yet validated by a maintainer on Colab.** vLLM changes fast. If a step fails, post the last 20 lines of `server.log` in `#labs-help`. No GPU at all? Do Q2–Q4 first: they run on any laptop.

## 1. Get a GPU

In Colab, open **Runtime → Change runtime type → T4 GPU**, then run this cell. On your own machine, just run it in a terminal.

```bash
!nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv
```

> ✅ **Checkpoint:** you see one GPU and its memory, e.g. `Tesla T4, 15360 MiB, 7.5`. A T4 has no BF16, so we'll use `--dtype half` below.

## 2. Install vLLM

This downloads a few GB of wheels and takes about 3–5 minutes. Use a fresh runtime.

```bash
!pip install -q vllm openai
!python -c "import vllm; print('vLLM', vllm.__version__)"
```

> ✅ **Checkpoint:** it prints a version, e.g. `vLLM 0.31.0`. Write it down: your results depend on it.

## 3. Start the server and time it

We use Qwen3-0.6B because it fits anywhere. The server runs in the background and writes to `server.log`. Note the start time: E28 is about why this takes so long.

```bash
!date +%T && nohup vllm serve Qwen/Qwen3-0.6B --dtype half --max-model-len 4096 --gpu-memory-utilization 0.85 > server.log 2>&1 &
!sleep 90; grep -E "KV cache|startup complete|Error" server.log | tail -5; date +%T
```

> ✅ **Checkpoint:** the log shows `Application startup complete` and a line with the GPU KV cache size in tokens. Write down that number and how many seconds startup took. If you see neither, wait 30 s and run the `grep` again.

## 4. Send your first request

The server speaks the OpenAI API, so any OpenAI client works. Start with plain `curl`. Qwen3 "thinks" out loud by default, so we switch thinking off to get a short direct answer.

```bash
!curl -s localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"Qwen/Qwen3-0.6B","messages":[{"role":"user","content":"In one sentence, what is vLLM?"}],"max_tokens":60,"chat_template_kwargs":{"enable_thinking":false}}' | python -m json.tool | head -30
```

> ✅ **Checkpoint:** you get JSON with `choices[0].message.content` and a `usage` block counting `prompt_tokens` and `completion_tokens`.

## 5. Watch tokens stream (E01)

ChatGPT is a for-loop: one forward pass, one token. Streaming makes that visible. This prints each token with its arrival time, so you can see time-to-first-token (TTFT) and the inter-token gap (ITL).

```python
import time
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")
t0 = last = time.perf_counter()
stream = client.chat.completions.create(model="Qwen/Qwen3-0.6B", stream=True, max_tokens=40,
    messages=[{"role": "user", "content": "Count from 1 to 10 in English."}],
    extra_body={"chat_template_kwargs": {"enable_thinking": False}})  # Qwen3 "thinks" by default
for i, chunk in enumerate(stream):
    now = time.perf_counter()
    text = chunk.choices[0].delta.content or ""
    print(f"{(now - t0) * 1000:7.1f} ms  (+{(now - last) * 1000:5.1f})  {text!r}")
    last = now
```

> ✅ **Checkpoint:** the first line's time is your TTFT. The `+` gaps after it should be small and steady: that's decode. Post your TTFT and typical gap in `#show-your-work`.

## 6. Tokenizer playground (E02)

Models never see letters. Compare how many tokens the same idea costs in English and in Chinese.

```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
for s in ["How many r's are in strawberry?", "strawberry 裡有幾個 r？", "推論引擎決定了你的帳單。", "The inference engine decides your bill."]:
    ids = tok.encode(s)
    print(len(ids), [tok.decode([i]) for i in ids])
```

> ✅ **Checkpoint:** you can see that "strawberry" is not split into letters, and you can explain why a model might miscount the r's.

## 7. Peek at the metrics

Production engineers live in `/metrics` (Prometheus format). Send a few requests, then look at what the engine reports about running requests, KV usage and prefix caching.

```bash
!curl -s localhost:8000/metrics | grep -E "^vllm:(num_requests|kv_cache_usage|prefix_cache|prompt_tokens|generation_tokens)" | head -20
```

> ✅ **Checkpoint:** you see `vllm:` metrics with non-zero token counters. Find the one that tells you how full the KV cache is.

## 8. Restart warm and compare (E28)

Stop the server and start it again with the same command. The second start reuses the torch.compile cache and probably the OS file cache for the weights.

```bash
!pkill -f "vllm serve"; sleep 5; date +%T
!nohup vllm serve Qwen/Qwen3-0.6B --dtype half --max-model-len 4096 --gpu-memory-utilization 0.85 > server2.log 2>&1 &
!sleep 60; grep -E "startup complete|compile|graph" server2.log | tail -5; date +%T
```

> ✅ **Checkpoint:** the warm start is noticeably faster than step 3. You can say which stages got cheaper and why: the weights came from the local Hugging Face cache instead of a download, and torch.compile reused its cache. CUDA-graph capture is not cached, so it runs again.

## What you learned

- vLLM gives you an OpenAI-compatible server with one command.
- Output arrives one token per step: TTFT is set by prefill, the gaps by decode.
- The startup log tells you how much KV cache you actually got (E07 does the math).
- Startup itself has stages, and they are worth measuring (E28).

**Next:** E03 builds the Transformer you just talked to. Prefer to stay hands-on? Q2 shows what the KV cache looks like inside.
