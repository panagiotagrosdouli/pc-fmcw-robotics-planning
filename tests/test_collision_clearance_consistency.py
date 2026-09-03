import numpy as np
import pytest

import iscai.simulation.pc_fmcw_benchmark as benchmark
from iscai.planning.planners import PlanningResult
from iscai.simulation.scenario import Scenario


class _RecordingPlanner:
    def __init__(self, name, records, *args, **kwargs):
        del args
        self.name = name
        self.records = records
        self.target_clearance = kwargs.get("target_clearance")

    def plan(self, ego, target_prediction, **kwargs):
        del ego, target_prediction, kwargs
        self.records.append((self.name, self.target_clearance))
        return PlanningResult(None, np.inf, None)


class _DummyLink:
    class _Geometry:
        outage_threshold_db = 8.0

    geometry = _Geometry()

    def predict(self, ego_trajectory, target_prediction, link_history=None):
        del ego_trajectory, target_prediction, link_history
        from iscai.prediction.link_predictor import LinkForecast

        value = np.array([0.0])
        return LinkForecast(value, value, value, value, 1.0)


def _scenario():
    return Scenario(
        name="clearance-consistency",
        ego_state=np.array([0.0, 0.0, 0.0, 2.0]),
        target_states=np.array(
            [
                [10.0, 0.0, 0.0, 2.0],
                [10.2, 0.0, 0.0, 2.0],
                [10.4, 0.0, 0.0, 2.0],
            ]
        ),
        obstacles=[],
        reference_speed=2.0,
    )


def test_custom_collision_radius_is_used_by_every_planner(monkeypatch):
    records = []

    for name, attr in (
        ("P0", "MobilityOnlyPlanner"),
        ("P1", "ReactiveConnectivityPlanner"),
        ("P2", "PredictiveConnectivityPlanner"),
        ("P3", "RiskAwarePredictivePlanner"),
        ("P4", "OracleConnectivityPlanner"),
    ):
        monkeypatch.setattr(
            benchmark,
            attr,
            lambda *args, _name=name, **kwargs: _RecordingPlanner(_name, records, *args, **kwargs),
        )

    clearance = 3.25
    settings = benchmark.BenchmarkSettings(
        horizon_steps=3,
        observation_sigma_m=0.0,
        p3_mc_samples=1,
        collision_distance_m=clearance,
    )

    for planner_name in benchmark.PLANNERS:
        benchmark.run_simulated_episode(
            planner_name,
            _scenario(),
            seed=0,
            settings=settings,
            link=_DummyLink(),
        )

    first = {name: next(value for planner, value in records if planner == name) for name in benchmark.PLANNERS}
    assert set(first) == set(benchmark.PLANNERS)
    for planner_name in benchmark.PLANNERS:
        assert first[planner_name] == pytest.approx(clearance)


def test_negative_collision_radius_is_rejected_before_planning():
    settings = benchmark.BenchmarkSettings(collision_distance_m=-0.1)
    with pytest.raises(ValueError, match="collision_distance_m must be non-negative"):
        benchmark.run_simulated_episode(
            "P0",
            _scenario(),
            seed=0,
            settings=settings,
            link=_DummyLink(),
        )
