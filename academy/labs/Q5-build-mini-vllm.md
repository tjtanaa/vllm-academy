# Q5 · Build mini-vLLM: the boss fight

**Needs:** CPU + PyTorch (no GPU) · **Time:** 4–8 h spread over a week · **Episodes:** E06, E08, E09, E10, E12 · **XP:** +75
**[繁體中文](Q5-build-mini-vllm.zh-TW.md)**

You'll rebuild a small inference engine (incremental KV, paged blocks, a scheduler with a token budget, prefix reuse, cancellation) and let 30 tests decide whether it's real. The repository's `mini_vllm/` is the reference solution. The rules: **predict before you peek**, and never delete a test to make the run green.

> mini_vllm uses random weights and runs serially on the CPU. It teaches the *mechanisms* behind vLLM, not its speed. The detailed milestone table lives in [labs/MILESTONES.md](../../labs/MILESTONES.md).

## 1. Set up and run the reference

Create an isolated environment, install CPU PyTorch, and confirm the reference engine passes before you change anything.

```bash
git clone https://github.com/tjtanaa/vllm-academy.git && cd vllm-academy
python3 -m venv .venv && source .venv/bin/activate
python -m pip install 'torch==2.10.0' --index-url https://download.pytorch.org/whl/cpu
python -m pip install 'pytest>=8,<10'
python -m pytest -q && python -m mini_vllm.demo
```

> ✅ **Checkpoint:** all tests pass and the demo prints a trace of requests being scheduled. Make a scratch branch: `git switch -c my-mini-vllm`.

## 2. M1–M2: decoder and incremental KV

Write down, before reading `model.py`, the shape of Q, K and V for a prompt of length T, and what the KV cache must store so that step T+1 doesn't recompute steps 1..T. Then implement or rewrite `DecoderLayer.step` and `TinyDecoder.cached` in your branch.

```bash
python -m pytest -q tests/test_engine.py -k 'dense or chunking'
```

> ✅ **Checkpoint:** cached and dense logits match within tolerance for every tested prompt length. You can explain why chunked prefill gives the same answer as one-shot prefill.

## 3. M3: physical pages and block tables

Now replace the private per-request cache with a shared `BlockPool` and per-request block tables. This is Q2's playground made real. Invariants to write first: a page has exactly one owner unless it's shared, and a page is never freed while referenced.

```bash
python -m pytest -q tests/test_engine.py -k 'noncontiguous or commit or pool_lifetime'
```

> ✅ **Checkpoint:** noncontiguous pages produce identical logits, and the pool returns to fully free after every request finishes.

## 4. M4: the scheduler

Implement waiting/running queues and a per-step token budget in `Engine.step`. Requests must be able to arrive mid-run and be cancelled at any time. This is Q3's continuous batching.

```bash
python -m pytest -q tests/test_engine.py -k 'cancel or dynamic'
```

> ✅ **Checkpoint:** a trace shows a late arrival joining a running batch, and cancelling a running request frees its pages immediately.

## 5. M5: prefix reuse

Give each full block a chained key (parent key + tokens + namespace) and reuse matching blocks across requests. Only full blocks are shareable. Never write into a shared block.

```bash
python -m pytest -q tests/test_engine.py -k 'prefix'
```

> ✅ **Checkpoint:** cold and warm runs of the same prompt give identical outputs, and two prompts that differ in their *first* token share nothing.

## 6. M6: survive the stress tests

Finish the lifecycle: finish, cancel, close, eviction and block exhaustion. An evicted page must never be one an active request still uses.

```bash
python -m pytest -q
```

> ✅ **Checkpoint:** the full suite is green on your branch, with no leaked references after `close()`. Post a screenshot in `#show-your-work` to claim the ⚙️ Engine Builder badge (finish S2 in Discord too).

## 7. Mutation challenge

Break one invariant on purpose, predict which test fails, then run the suite. Try these: reuse a freed active page; omit the parent hash; overwrite a shared full block; forget to release on cancel.

```bash
python -m pytest -q -x
```

> ✅ **Checkpoint:** each mutation fails the test you predicted. If one survives, you found a coverage gap. Add a focused test, and that test is a perfectly good first PR to this repo.

## What you learned

- Incremental KV turns O(T²) recomputation into O(T) work per sequence.
- Paging, reference counts and chained prefix keys are a few dozen lines each, and the tests explain why every line exists.
- A scheduler is a loop over queues with a budget; the hard part is cleanup when things go wrong.
- You now know which questions to ask when you open vLLM's real `scheduler.py` and `kv_cache_manager.py` in S3.
