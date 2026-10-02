import pytest
from labs.kv_budget import estimate


def test_kv_example():
    r = estimate(32, 8, 128, 2, 8192, 1, 16)
    assert r['kv_bytes_per_token'] == 131072
    assert r['logical_gib'] == 1


def test_tail_fragmentation():
    r = estimate(32, 8, 128, 2, 8193, 2, 16)
    assert r['wasted_token_slots_per_request'] == 15
    assert r['allocated_gib_without_sharing'] > r['logical_gib']


def test_budget_invalid():
    with pytest.raises(ValueError):
        estimate(0,8,128,2,8192,1,16)
