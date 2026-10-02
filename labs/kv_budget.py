"""Dense MHA/GQA KV estimate. NOT MLA, recurrent-state, sliding-window, or TP replication accounting."""
import argparse
import json


def estimate(layers: int, kv_heads: int, head_dim: int, bytes_per_element: float,
             tokens: int, requests: int, block_size: int) -> dict:
    if min(layers, kv_heads, head_dim, bytes_per_element, tokens, requests, block_size) <= 0:
        raise ValueError('All parameters must be positive')
    per_token = 2 * layers * kv_heads * head_dim * bytes_per_element
    slots = ((tokens + block_size - 1) // block_size) * block_size
    return {'kv_bytes_per_token':per_token, 'logical_gib':per_token * tokens * requests / 2**30,
            'allocated_gib_without_sharing':per_token * slots * requests / 2**30,
            'wasted_token_slots_per_request':slots - tokens,
            'assumptions':'Single full-attention cache group; no scales, allocator metadata, sharing, or rank partitioning'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name, default in [('layers',32), ('kv-heads',8), ('head-dim',128), ('tokens',8192), ('requests',1), ('block-size',16)]:
        p.add_argument('--' + name, type=int, default=default)
    p.add_argument('--bytes-per-element', type=float, default=2)
    a = p.parse_args()
    try:
        print(json.dumps(estimate(a.layers,a.kv_heads,a.head_dim,a.bytes_per_element,a.tokens,a.requests,a.block_size),indent=2))
    except ValueError as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()
