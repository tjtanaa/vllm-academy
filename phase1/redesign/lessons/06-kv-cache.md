# 06 — Remember computation: KV and token work

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

The inference loop repeats work on an expanding history. KV caching preserves earlier key/value representations so a new query can use them without recomputing every preceding hidden state. It does not make dense attention to a long history free.

## Computed and sampled are different counters

For prompt `[11,22,33]`, execute three positions and obtain logits predicting `44`. The cache covers 11, 22 and 33. It does not yet cover 44. The next forward processes 44 and can predict another token.

This is the most important off-by-one exercise in the course. Ask learners to write **known history**, **computed positions**, **newly sampled output**, and **allocated capacity** in separate columns. Allocating a slot does not mean that slot contains valid state.

Prefill processes known prompt inputs. Decode advances generated history. Production prefill may be parallelized and chunked, whereas the original mini engine intentionally processes prefill serially. A teaching algorithm is not a claim about production efficiency.

## Run exact mechanism checks

```bash
python -m pytest -q tests/test_mechanisms.py -k 'cached or greedy'
python -m labs.naive_transformer
```

The new lab's attention supports multi-token cached chunks. For a chunk beginning at offset 4, its first query is absolute position 4 and may attend to keys 0 through 4. A naive top-left triangular mask over a two-query/six-key matrix would be wrong.

Open `Block.forward`. Locate `query_pos = offset + ...` and compare the mask with the square full-forward mask. Test several split positions instead of trusting a single-token decode test.

The private cache here stores full K/V pairs per layer and concatenates tensors. It is intentionally not a paged allocator. Paging comes after the numerical invariant is clear.

## Memory and work reasoning

For dense full-attention state, a simplified per-sequence estimate is `2 × layers × tokens × KV_heads × head_dim × bytes_per_scalar`. State all assumptions: no quantization metadata, replication, hybrid state, allocator overhead or sharing. Use KV-head count, not query-head count. [R15, R23](../REFERENCES.md)

A new dense-attention query still reads a history whose length grows. Claims such as “caching turns O(n²) into O(n)” must specify whether they discuss one forward, one new query, or total generation work.

## Source detour and exit ticket

Use the scheduler source entry to locate request progress and work-budget concepts. Do not memorize a simplistic global switch that divides every iteration into exactly one prefill or decode phase.

Submit a six-token prompt with a two-chunk prefill trace, then three generated tokens. Explain precisely which state exists after each sample. [Production reading](../SOURCE_MAP.md)
