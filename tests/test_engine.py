import pytest
import torch
from mini_vllm.cache import BlockPool, CacheFull, PagedKV, PrefixIndex, prefix_keys
from mini_vllm.engine import Engine
from mini_vllm.model import ModelConfig, TinyDecoder


torch.set_num_threads(1)


def pool(blocks=32, size=4):
    return BlockPool(blocks, size, 2, 4, 8)


def test_pool_lifetime():
    p = pool(2)
    a, b = p.allocate(), p.allocate()
    p.retain(a)
    p.release(a)
    with pytest.raises(CacheFull):
        p.allocate()
    p.release(a)
    assert p.allocate() == a
    p.release(a)
    with pytest.raises(RuntimeError):
        p.release(a)
    p.release(b)
    p.validate()


@pytest.mark.parametrize('length', [1, 3, 4, 5, 8, 9, 17])
def test_dense_cached_equivalence(length):
    model = TinyDecoder()
    tokens = [(i * 7 + 1) % 64 for i in range(length)]
    p = pool()
    cache = PagedKV(p)
    try:
        cached = model.cached(tokens, cache)
        torch.testing.assert_close(cached, model(tokens), atol=2e-6, rtol=2e-5)
        assert cache.length == length
        assert len(cache.pages) == (length + 3) // 4
    finally:
        cache.close()
    assert len(p.free) == p.num_blocks


def test_chunking_equivalence():
    model, p = TinyDecoder(), pool()
    cache = PagedKV(p)
    try:
        a = model.cached([1, 2, 3], cache)
        b = model.cached([4, 5], cache)
        torch.testing.assert_close(torch.cat([a, b]), model([1, 2, 3, 4, 5]), atol=2e-6, rtol=2e-5)
    finally:
        cache.close()


def test_noncontiguous_pages():
    model, p = TinyDecoder(), pool(4)
    a, b = p.allocate(), p.allocate()
    p.release(a)  # Free list is [2,3,0], forcing a noncontiguous third page.
    cache = PagedKV(p)
    try:
        tokens = list(range(1, 10))
        out = model.cached(tokens, cache)
        assert cache.pages == [2, 3, 0]
        torch.testing.assert_close(out, model(tokens), atol=2e-6, rtol=2e-5)
    finally:
        cache.close()
        p.release(b)


def test_commit_requires_all_layers():
    cache = PagedKV(pool())
    cache.reserve_token()
    with pytest.raises(RuntimeError):
        cache.commit_token()
    cache.close()


def test_key_chain_and_namespace():
    a = prefix_keys([1, 2, 3, 4], 2, 'model-a')
    b = prefix_keys([9, 8, 3, 4], 2, 'model-a')
    assert a[1] != b[1]
    assert a != prefix_keys([1, 2, 3, 4], 2, 'model-b')
    assert len(prefix_keys([1, 2, 3], 2, 'x')) == 1


@pytest.mark.parametrize('length', [1, 4, 5, 8, 9])
def test_prefix_reuse_matches_dense(length):
    model = TinyDecoder()
    tokens = list(range(1, length + 1))
    with Engine(model) as e:
        e.add('cold', tokens, 4)
        e.run()
        e.add('warm', tokens, 4)
        result = e.run()
        assert result['cold'] == result['warm'] == model.generate_dense(tokens, 4)
        assert e.requests['warm'].reused_tokens == ((length - 1) // 4) * 4
    assert len(e.pool.free) == e.pool.num_blocks


def test_cache_disabled():
    with Engine(TinyDecoder(), prefix_caching=False) as e:
        e.add('one', [1, 2, 3, 4, 5], 2)
        e.run()
        e.add('two', [1, 2, 3, 4, 5], 2)
        assert e.run()['one'] == e.requests['two'].output
        assert e.requests['two'].reused_tokens == 0


def test_eviction_never_frees_active_pages():
    model, p = TinyDecoder(), pool(1)
    index = PrefixIndex(p, 'a')
    cache = PagedKV(p, evict=index.evict_one)
    model.cached([1, 2, 3, 4], cache)
    index.publish([1, 2, 3, 4], cache)
    assert not index.evict_one()
    with pytest.raises(CacheFull):
        p.allocate(index.evict_one)
    cache.close()
    assert index.evict_one()
    assert len(p.free) == 1
    assert not index.entries


def test_cancel_and_dynamic_arrival():
    model = TinyDecoder()
    with Engine(model, token_budget=3, max_active=2, prefill_chunk=2) as e:
        e.add('a', [1, 2, 3, 4, 5], 4)
        e.step()
        e.add('b', [6, 7], 3)
        e.add('cancel-waiting', [8], 3)
        e.cancel('cancel-waiting')
        result = e.run()
        assert result['a'] == model.generate_dense([1, 2, 3, 4, 5], 4)
        assert result['b'] == model.generate_dense([6, 7], 3)
        assert 'cancel-waiting' not in result
        assert all(t['scheduled_tokens'] <= 3 for t in e.trace)


def test_cancel_running():
    with Engine(TinyDecoder(), prefix_caching=False, token_budget=2) as e:
        e.add('a', [1, 2, 3, 4, 5], 4)
        e.step()
        e.cancel('a')
        assert e.requests['a'].status == 'cancelled'
        assert len(e.pool.free) == e.pool.num_blocks
        assert not e.step()


def test_lifetime_idempotent_close():
    with Engine(TinyDecoder()) as e:
        e.add('x', [1, 2, 3], 2)
        e.step()
    e.close()
    assert len(e.pool.free) == e.pool.num_blocks


def test_invalid_inputs():
    with pytest.raises(ValueError):
        ModelConfig(hidden_size=31)
    e = Engine(TinyDecoder())
    for prompt in ([], [-1], [64], [1.5]):
        with pytest.raises(ValueError):
            e.add('bad', prompt)
    e.add('a', [1], 1)
    with pytest.raises(ValueError):
        e.add('a', [2], 1)
    with pytest.raises(ValueError):
        e.add('too-long', [1] * 128, 2)
    e.close()


def test_block_exhaustion_cleanup():
    e = Engine(TinyDecoder(), num_blocks=1, block_size=2)
    with pytest.raises(CacheFull):
        with e:
            e.add('a', [1, 2, 3, 4, 5], 2)
            e.run()
    assert len(e.pool.free) == e.pool.num_blocks


def test_divergent_prefixes_and_eviction_stress():
    model = TinyDecoder()
    with Engine(model, num_blocks=8, max_active=1, block_size=2, token_budget=4) as e:
        for i in range(20):
            prompt = [1, 2, 3 + i % 10, 4 + i % 10, 5]
            e.add(str(i), prompt, 3)
            assert e.run()[str(i)] == model.generate_dense(prompt, 3)
            e.pool.validate()
    assert len(e.pool.free) == 8


def test_close_cancels_waiting_and_running():
    e = Engine(TinyDecoder(), max_active=1, token_budget=1)
    active = e.add('active', [1, 2, 3, 4], 3)
    waiting = e.add('waiting', [5, 6], 3)
    e.step()
    assert active.status == 'running' and waiting.status == 'waiting'
    e.close()
    assert active.status == waiting.status == 'cancelled'
    assert not e.active and not e.waiting
    assert len(e.pool.free) == e.pool.num_blocks


def test_namespace_includes_model_configuration():
    # Same parameter shapes and seed, but a different head decomposition.
    a = TinyDecoder(ModelConfig(num_heads=4))
    b = TinyDecoder(ModelConfig(num_heads=2))
    for key in a.state_dict():
        torch.testing.assert_close(a.state_dict()[key], b.state_dict()[key])
    with Engine(a) as one, Engine(b) as two:
        assert one.prefix.namespace != two.prefix.namespace
