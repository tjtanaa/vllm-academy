# 08 — Pages, prefixes and ownership

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

Once KV mathematics and scheduling are clear, introduce a new problem: storing differently sized, changing histories efficiently. Logical token order need not equal physical storage order.

## Address a token without contiguous allocation

For block size `B`, token position `t` has logical block `t // B` and within-block offset `t % B`. A block table maps that logical block to a physical slot. With block size 4 and table `[7,2,11]`, token position 5 is physical block 2, offset 1.

The PagedAttention paper motivates flexible persistent KV storage. It is not the same optimization as FlashAttention's IO-aware attention computation. A production kernel may consume a paged representation efficiently; the educational engine may gather pages into dense tensors for clarity. [R23–R24](../REFERENCES.md)

## Reuse requires identity and lifetime

Two requests can share state for a compatible exact prefix, but identical text alone is not a complete cache identity. Model revision, effective tokenization, modality information, adapters or other relevant options can matter. A common complete-block prefix is easier to share safely than a partially written mutable tail.

The originating request finishing does not necessarily make a shared block reusable. Another reader may still depend on it. Keep cached identity, active references, readiness and free-list membership separate.

## Hands-on

Use the existing Academy `BlockPool`, `PagedKV` and `PrefixIndex` tests from its checkout. Inspect one full-block prefix hit and one noncontiguous mapping. Reconstruct the actual number of physical blocks and live references rather than assuming logical tokens equal occupancy.

Then run the independent lifetime lab:

```bash
python -m labs.cache_lifecycle
python -m pytest -q tests/test_mechanisms.py -k 'recycle or reference or cache_stage'
```

The small `Slot` state machine deliberately separates completion from acquisition and recycling. It is not a distributed connector. Its failed early-recycle attempt is the point of the exercise.

## Source detour

The Academy's original pinned block-pool/cache-manager readings remain useful. Keep their v0.29.0 reference distinct from the new frontend/MM source supplement. Do not silently reinterpret historical line numbers as current main.

## Exercise and exit ticket

Calculate physical slots and tail waste for a nine-token request at block size 4. Then add a second request sharing the first two full blocks. State assumptions about whether cached blocks retain a reference and how the implementation accounts for ownership.

Finally, change one earlier prefix token while preserving a later block's content. Explain why context-dependent keys must prevent the later block from being treated as the same prefix state merely because its own tokens match.
