from datetime import date, timedelta

from academy_bot import kvcalc
from academy_bot.drops import WEEKLY_ROTATION, daily_drop, release_highlights, study_links, take_verdict
from academy_bot.progress import LearnerState, earned_badges, level_for


def test_e07_answer():
    r = kvcalc.compute(kvcalc.MODELS["llama-3.1-70b"], context=131072, gpus=4, gpu_mem_gib=80)
    assert r.kv_per_token == 320 * 1024
    assert round(r.kv_per_seq / kvcalc.GIB, 1) == 40.0
    assert r.max_seqs == 4 and r.fits


def test_mla_is_smaller():
    ds = kvcalc.MODELS["deepseek-v3"].kv_bytes_per_token(2)
    assert ds == 61 * (512 + 64) * 2 < 320 * 1024 / 4


def test_daily_rotation_is_deterministic_and_covers_week(content):
    monday = date(2026, 10, 12)
    kinds = [daily_drop(content, monday + timedelta(days=i))[0] for i in range(7)]
    assert kinds == [WEEKLY_ROTATION[i] for i in range(7)]
    assert daily_drop(content, monday) == daily_drop(content, monday)
    assert kinds[4] == "hottake"  # Friday, newsletter day


def test_study_links():
    body = "- Speculative decoding: EAGLE3 on MRV2\n- NVFP4 KV cache\n- `vllm preload` daemon (#123)\n"
    eps = study_links(body)
    assert eps[:2] == ["E17", "E15"] or eps[0] == "E17"
    assert "E18" in eps and "E28" in study_links(body, limit=6)
    assert release_highlights(body)[2] == "`vllm preload` daemon"


def test_verdict_override():
    take = {"verdict": None}
    assert take_verdict(take, "right|nailed it") == ("right", "nailed it")
    assert take_verdict({"verdict": "wrong", "verdict_note": "x"}) == ("wrong", "x")


def test_new_badges(content):
    seasons = {s.id: [e.id for e in content.season_episodes(s.id)] for s in content.seasons}
    st = LearnerState(completed_episodes={"E27", "E28"}, hot_takes_voted=5)
    assert {"oracle", "frontier"} <= earned_badges(st, seasons)
    assert level_for(0, content.ranks).level == 1
