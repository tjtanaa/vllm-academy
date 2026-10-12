# Q3 · Batching Arena: why one GPU can serve a thousand users

**Needs:** Python 3.10+ only (no GPU, no PyTorch) · **Time:** 15 min · **Episodes:** E05, E09, E11 · **XP:** +75
**[繁體中文](Q3-batching-arena.zh-TW.md)**

Two questions decide most of LLM serving. Why is decode memory-bound? What should the scheduler run next step? This lab answers both with a roofline cost model and a race between three schedulers on the same workload.

> The arena models an 8B BF16 model on an H100-class GPU. Each step costs `overhead + max(bytes / bandwidth, FLOPs / peak)`. Absolute numbers are illustrative; the shape of the results is what carries over to real vLLM (Q7 measures the real thing). The default run is deterministic, so your numbers should match.

## 1. Draw the roofline (E05)

Decode reads all 16 GB of weights every step, however many users are in the batch.

```bash
python academy/labs/batching_arena.py --roofline
```

> ✅ **Checkpoint:** batch 1 takes about **7.5 ms** per step (about 133 tokens/s). Batch 8 takes about **7.9 ms** for 8× the tokens. Every row says `memory`.

## 2. Read the trade-off

Look at the `per-user tok/s` column as the batch grows: total throughput climbs, but each user gets slower, because KV reads grow with batch × context. At 512 sequences the KV no longer even fits in 80 GB.

```text
batch  step ms  total tok/s  per-user tok/s
   64     10.7        5,983            93.5
  256     20.3       12,603            49.2
```

> ✅ **Checkpoint:** you can answer the interview classic "why does batching help decode so much?" in two sentences, using the words *bandwidth* and *weights*.

## 3. Run the race (E09)

The same workload runs under three schedulers: 24 chats, plus a 🐋 16,000-token paste arriving at 0.8 s.

```bash
python academy/labs/batching_arena.py
```

> ✅ **Checkpoint:** the scoreboard shows static batching at about **468 tok/s** and continuous batching at about **1,192 tok/s** on the same GPU. Static's TTFT p50 is about **4.9 s**; continuous's is about **0.15 s**.

## 4. Read the timelines

`·` means waiting, `▒` prefill, `█` decoding. In static batching, finished requests leave idle slots until the slowest one in the batch is done, and newcomers queue behind the whole batch. Continuous batching admits and retires requests every step (iteration-level scheduling, from the Orca paper).

```text
Legend: · waiting   ▒ prefill   █ decoding   🐋 = the 16k-token paste
```

> ✅ **Checkpoint:** you can point at the row in the static timeline where a request waits a long time even though the GPU had room.

## 5. Find the whale stall (E11)

Look at the `decode gap` line under continuous batching: one huge spike of about **401 ms**. That's the whale's whole 16k-token prefill running as a single step while every chatting user freezes. Now compare with chunking turned off explicitly:

```bash
python academy/labs/batching_arena.py --chunk 0
```

> ✅ **Checkpoint:** with `--chunk 0` the third row matches continuous (worst gap ~401 ms). With the default `--chunk 512` the worst gap is about **14 ms**. Chunked prefill costs a little TTFT (p50 0.15 s → 0.25 s).

## 6. Tune it yourself

Try different budgets and workloads, and write down what changes. Smaller chunks protect decode better but add steps; no whale means chunking barely matters.

```bash
python academy/labs/batching_arena.py --chunk 2048
python academy/labs/batching_arena.py --chunk 128
python academy/labs/batching_arena.py --no-whale
python academy/labs/batching_arena.py --batch 32
```

> ✅ **Checkpoint:** you found a chunk size where the worst gap and TTFT p99 are both acceptable to you, and you can say why you picked it.

## 7. Map it to real vLLM knobs

The arena's knobs have real names. In vLLM, chunked prefill is on by default, `--max-num-batched-tokens` is the per-step token budget (the arena's `--chunk`), and `--max-num-seqs` caps how many requests run at once.

```bash
vllm serve Qwen/Qwen3-8B --max-num-batched-tokens 2048 --max-num-seqs 128
```

> ✅ **Checkpoint:** you can explain to a teammate what raising `--max-num-batched-tokens` does to TTFT and to inter-token latency. Post it in `#show-your-work`.

## What you learned

- Decode is memory-bound: batching shares one weight read across many users.
- Continuous batching schedules per step, so nobody waits for the slowest request.
- Big prefills stall decode; a per-step token budget (chunked prefill) turns one long freeze into a few slightly slower steps.
- Every knob trades TTFT, inter-token latency and throughput against each other. There's no free lunch, only informed choices.
