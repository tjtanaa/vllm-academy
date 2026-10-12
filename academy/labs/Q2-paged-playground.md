# Q2 · Paged Playground: see PagedAttention's memory trick with your own eyes

**Needs:** Python 3.10+ only (no GPU, no PyTorch, no pip install) · **Time:** 15 min · **Episodes:** E08, E10, E21, E27 · **XP:** +75
**[繁體中文](Q2-paged-playground.zh-TW.md)**

vLLM's founding idea is to store the KV cache in small fixed-size **blocks** (pages) instead of one big contiguous slab per request. That idea gives you less waste, sharing between requests, prefix caching and offloading. This lab animates all four.

> The playground is a teaching model of vLLM's KV cache manager. It uses 4-token blocks so you can see every slot; vLLM's default is 16. Every number below comes from the default run, so yours should match exactly.

## 1. Run the basic scenario

From the repo root:

```bash
python academy/labs/paged_playground.py
```

> ✅ **Checkpoint:** the Result section shows **24 paged slots** for 22 stored tokens (8% waste) versus **64 slots** (66% waste) for contiguous reservation at max length 32.

## 2. Read a block table

Scroll up to the frame after both requests decoded. A has block table `[0, 1, 4]`: its logical blocks 0, 1, 2 live in physical blocks 0, 1 and 4. Physical memory isn't contiguous, and it doesn't need to be. Attention kernels follow the table, just as an OS follows a page table.

```text
A block table → [0, 1, 4]  (12 tokens, last block 4/4 full)
B block table → [2, 3, 5]  (10 tokens, last block 2/4 full)
```

> ✅ **Checkpoint:** you can explain why the most a request can waste is one partly-filled block (`block_size - 1` slots).

## 3. Share a system prompt

Two chats start with the same 12-token system prompt, which is 3 full blocks.

```bash
python academy/labs/paged_playground.py --scenario prefix
```

> ✅ **Checkpoint:** B arrives with `3 block(s) HIT on GPU`, the grid shows `[A2]` (ref count 2), and the Result says **24 prompt tokens reused**. C reuses the blocks even after A and B have finished.

## 4. Break the cache like a rookie

A classic production mistake is putting a timestamp or request ID at the **start** of the prompt. Block hashes are chained (each block's hash includes its parent's), so one different first token changes every hash after it.

```bash
python academy/labs/paged_playground.py --scenario prefix --break-prefix
```

> ✅ **Checkpoint:** **0 tokens reused** and 54 computed. Write one sentence for `#show-your-work` on where dynamic content should go in a prompt.

## 5. Offload under memory pressure

The GPU has only 8 blocks. New requests evict cached blocks in LRU order, and with a CPU tier the evicted blocks are copied out instead of thrown away.

```bash
python academy/labs/paged_playground.py --scenario offload
```

> ✅ **Checkpoint:** A2 arrives with `1 block(s) HIT on GPU, 3 block(s) LOADED from CPU`. The Result shows **6 blocks offloaded** and **12 tokens loaded back** instead of being recomputed.

## 6. Replay an agent session (E27)

Agents re-send their whole history every turn. Between turns, other users churn the cache. Compare offload on and off for the same session:

```bash
python academy/labs/paged_playground.py --scenario agent
```

> ✅ **Checkpoint:** the final table shows **74** prefill tokens computed with offload ON vs **214** with it OFF. Turn 4 recomputes 9 tokens instead of 73.

## 7. Turn the knobs

Real vLLM uses 16-token blocks. Re-run the basic scenario with bigger blocks and see how waste changes. Then give the agent scenario more GPU memory.

```bash
python academy/labs/paged_playground.py --block-size 16
python academy/labs/paged_playground.py --scenario agent --gpu-blocks 40
```

> ✅ **Checkpoint:** with 16-token blocks the paged waste rises to **31%**. You can explain the trade-off: bigger blocks mean less metadata and better kernel efficiency, but more internal waste and coarser prefix matching.

## 8. Find it in real vLLM

In Discord, run `/code` and open the KV cache area: `kv_cache_manager`, `block_pool`, `free_queue` and `prefix_hash`. Each entry is a permalink into the pinned vLLM commit. Then try hunts H3–H5 with `/hunt`.

```text
/code entry:block_pool
/hunt hunt:H5
```

> ✅ **Checkpoint:** you can name the vLLM class that plays the role of `PagedKV.free` in this playground (that's hunt H5).

## What you learned

- Paging cuts KV waste to under one block per request, so more requests fit.
- Full blocks get a chained hash; identical prefixes share physical blocks through reference counts.
- Freed blocks stay cached until evicted (LRU), which is why prefix caching is "free speed".
- Offloading turns an eviction into a cheap copy instead of an expensive recompute, and agents benefit most.
