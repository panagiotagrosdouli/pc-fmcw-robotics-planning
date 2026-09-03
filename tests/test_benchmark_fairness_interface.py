import numpy as np

import iscai.simulation.pc_fmcw_benchmark as benchmark
from iscai.planning.planners import PlanningResult
from iscai.simulation.scenario import Scenario


class _RecordingPlanner:
    def __init__(self, name, records):
        self.name = name
        self.records = records

    def plan(self, ego, target_prediction, **kwargs):
        self.records.append(
            {
                "planner": self.name,
                "target_prediction": target_prediction,
                "safety_target_prediction": kwargs.get("safety_target_prediction"),
            }
        )
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
    target = np.array(
        [
            [10.0, 0.0, 0.0, 2.0],
            [10.2, 0.0, 0.0, 2.0],
            [10.4, 0.0, 0.0, 2.0],
        ]
    )
    return Scenario(
        name="fairness-interface",
        ego_state=np.array([0.0, 0.0, 0.0, 2.0]),
        target_states=target,
        obstacles=[],
        reference_speed=2.0,
    )


def test_benchmark_passes_common_safety_prediction_explicitly_to_all_planners(monkeypatch):
    records = []

    monkeypatch.setattr(
        benchmark,
        "MobilityOnlyPlanner",
        lambda *args, **kwargs: _RecordingPlanner("P0", records),
    )
    monkeypatch.setattr(
        benchmark,
        "ReactiveConnectivityPlanner",
        lambda *args, **kwargs: _RecordingPlanner("P1", records),
    )
    monkeypatch.setattr(
        benchmark,
        "PredictiveConnectivityPlanner",
        lambda *args, **kwargs: _RecordingPlanner("P2", records),
    )
    monkeypatch.setattr(
        benchmark,
        "RiskAwarePredictivePlanner",
        lambda *args, **kwargs: _RecordingPlanner("P3", records),
    )
    monkeypatch.setattr(
        benchmark,
        "OracleConnectivityPlanner",
        lambda *args, **kwargs: _RecordingPlanner("P4", records),
    )

    settings = benchmark.BenchmarkSettings(
        horizon_steps=3,
        observation_sigma_m=0.0,
        p3_mc_samples=1,
    )
    link = _DummyLink()

    for planner in benchmark.PLANNERS:
        benchmark.run_simulated_episode(
            planner,
            _scenario(),
            seed=0,
            settings=settings,
            link=link,
        )

    first_call = {name: next(r for r in records if r["planner"] == name) for name in benchmark.PLANNERS}
    common = first_call["P0"]["safety_target_prediction"]
    assert common is not None
    for name in benchmark.PLANNERS:
        safety = first_call[name]["safety_target_prediction"]
        assert safety is not None
        np.testing.assert_allclose(safety, common)

    # P4 may differ only in the connectivity/forecast target input.
    assert not np.array_equal(first_call["P4"]["target_prediction"], common)
    np.testing.assert_allclose(first_call["P2"]["target_prediction"], common)
