# Rebuild the engine in six milestones

The repository supplies a reference implementation, not a blank exercise skeleton. Work in a separate scratch branch or directory. Write your proposed invariants before reading each corresponding method. Do not delete the reference tests to obtain a green run. There are no pre-created Git checkpoint tags in this archive.

| Milestone | Build first | Read only after attempting | Tests to inspect | Completion evidence |
|---|---|---|---|---|
| M1 | Causal decoder and greedy dense generation | `model.py`: `DecoderLayer.dense`, `TinyDecoder.forward` | `test_dense_cached_equivalence` for the later contract | Q/K/V shape table and manual causal-mask check |
| M2 | Private incremental KV state | `model.py`: `DecoderLayer.step`, `TinyDecoder.cached` | `test_dense_cached_equivalence`, `test_chunking_equivalence` | All tested prompt lengths match dense logits within tolerance |
| M3 | Physical pages and per-request tables | `cache.py`: `BlockPool`, `PagedKV` | `test_noncontiguous_pages`, `test_commit_requires_all_layers`, `test_pool_lifetime` | Noncontiguous address mapping, initialized-state and release proofs |
| M4 | Waiting/running queues and bounded token work | `engine.py`: `Request`, `Engine.step` | `test_cancel_and_dynamic_arrival`, `test_cancel_running` | Trace with a late arrival and changing membership |
| M5 | Full-block prefix identity and reuse | `cache.py`: `prefix_keys`, `PrefixIndex` | `test_key_chain_and_namespace`, `test_prefix_reuse_matches_dense` | Cold/warm equality, tail boundaries and divergent-context controls |
| M6 | Lifecycle stress and explicit failure behavior | `engine.py`: finish/cancel/close paths | `test_eviction_never_frees_active_pages`, `test_block_exhaustion_cleanup`, `test_divergent_prefixes_and_eviction_stress` | Full suite passes with no leaked references after close |

## Useful commands

```bash
python -m pytest -q tests/test_engine.py -k 'dense or chunking'
python -m pytest -q tests/test_engine.py -k 'noncontiguous or commit or pool_lifetime'
python -m pytest -q tests/test_engine.py -k 'cancel or dynamic'
python -m pytest -q tests/test_engine.py -k 'prefix or evict or exhaustion'
python -m pytest -q
python -m mini_vllm.demo --output results/my-trace.json
```

## Mutation challenges

Make one change at a time on a disposable branch, predict a failing assertion, run the tests, and restore the correct code. Suggested mutations: reuse a freed active page; omit a parent hash; increment cache length before all layers write; sample before a prefill chunk reaches the known-token frontier; overwrite a shared full block; forget to release on cancellation.

A mutation that survives all tests identifies a coverage gap. Add a focused regression test and explain the missing invariant. Do not count an unrelated exception or syntax error as a successful correctness test.

## Stretch work, not implemented

The next educational milestones could add vectorized prefill, a packed multi-request forward, a real tokenizer/checkpoint loader, or a controlled streaming transport. Each needs a separate specification and tests. Do not advertise the existing serial reference as a performant GPU serving engine.
