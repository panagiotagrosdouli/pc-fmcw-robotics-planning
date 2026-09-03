import numpy as np
import pandas as pd

from scripts.plot_pc_fmcw_robustness import _aggregate_episodes, _bootstrap_mean_ci


def test_bootstrap_mean_ci_is_deterministic_and_contains_mean():
    values = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=float)
    first = _bootstrap_mean_ci(values, samples=1000, seed=2026)
    second = _bootstrap_mean_ci(values, samples=1000, seed=2026)
    assert first == second
    mean, low, high = first
    assert low <= mean <= high
    assert np.isclose(mean, values.mean())


def test_bootstrap_mean_ci_handles_singleton_and_nonfinite_values():
    mean, low, high = _bootstrap_mean_ci([np.nan, 0.25, np.inf], samples=100, seed=1)
    assert mean == low == high == 0.25


def test_episode_aggregation_produces_interval_columns_per_planner():
    rows = []
    for planner, offset in [("P0", 0.0), ("P2", 0.05)]:
        for seed in range(6):
            rows.append(
                {
                    "sweep_parameter": "observation_sigma_m",
                    "sweep_value": 0.2,
                    "planner": planner,
                    "mean_outage_probability": 0.1 + offset + 0.01 * seed,
                    "progress_m": 20.0 - seed,
                    "collision_indicator": float(seed == 5),
                }
            )
    summary = _aggregate_episodes(pd.DataFrame(rows), bootstrap_samples=500, seed=2026)
    assert set(summary["planner"]) == {"P0", "P2"}
    for metric in ("outage", "progress_m", "collision_rate"):
        assert f"{metric}_ci_low" in summary.columns
        assert f"{metric}_ci_high" in summary.columns
        assert np.all(summary[f"{metric}_ci_low"] <= summary[metric])
        assert np.all(summary[metric] <= summary[f"{metric}_ci_high"])
