import pandas as pd
import pytest

from scripts.merge_research_framework_shards import EPISODE_KEY, TRACE_KEY, _validate_unique


def test_episode_shard_key_accepts_distinct_settings_and_seeds():
    frame = pd.DataFrame([
        {"experiment": "shift", "setting_id": "a", "scenario": "s", "planner": "P2", "seed": 0},
        {"experiment": "shift", "setting_id": "b", "scenario": "s", "planner": "P2", "seed": 0},
        {"experiment": "shift", "setting_id": "a", "scenario": "s", "planner": "P2", "seed": 1},
    ])
    _validate_unique(frame, EPISODE_KEY, "episode")


def test_episode_shard_key_rejects_duplicate_experimental_unit():
    row = {"experiment": "core", "setting_id": "nominal", "scenario": "s", "planner": "P2", "seed": 0}
    frame = pd.DataFrame([row, row])
    with pytest.raises(ValueError, match="duplicate episode experimental units"):
        _validate_unique(frame, EPISODE_KEY, "episode")


def test_trace_key_distinguishes_time_steps_but_rejects_duplicate_step():
    base = {"experiment": "core", "setting_id": "nominal", "scenario": "s", "planner": "P2", "seed": 0}
    frame = pd.DataFrame([{**base, "step": 1}, {**base, "step": 2}])
    _validate_unique(frame, TRACE_KEY, "trajectory")
    with pytest.raises(ValueError):
        _validate_unique(pd.concat([frame, frame.iloc[[0]]], ignore_index=True), TRACE_KEY, "trajectory")
