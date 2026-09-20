import numpy as np

from iscai.simulation.pc_fmcw_benchmark import (
    BenchmarkSettings,
    _prediction,
    run_simulated_episode,
)
from iscai.simulation.scenario import following_lateral_offset


def test_damped_lateral_forecast_is_anchored_to_latest_observation():
    history = np.array([[0.0, 1.8], [1.0, 1.6], [2.0, 1.2]])
    pred = _prediction(history, 5, 0.1, damped_lateral=True,
                       endpoint_anchored_lateral=True)
    slope = np.polyfit(np.arange(3) * 0.1, history[:, 1], 1)[0]
    expected = history[-1, 1] + slope * 0.5 * (1.0 - np.exp(-0.1 / 0.5))
    assert np.isclose(pred[0, 1], expected)


def test_v6_confirmatory_failure_is_resolved_without_target_truth():
    settings = BenchmarkSettings(
        planning_safety_margin_m=0.5,
        v4_static_viability=True,
        v5_time_aligned_dynamic=True,
        v5_dynamic_stop_viability=True,
        v5_damped_lateral_prediction=True,
        v6_hierarchical_clearance=True,
        v7_endpoint_anchored_lateral=True,
    )
    for planner in ("P0", "P1", "P3"):
        row = run_simulated_episode(
            planner, following_lateral_offset(), seed=16030, settings=settings
        )
        assert row["no_candidate_steps"] == 0
        assert row["collision_indicator"] == 0
