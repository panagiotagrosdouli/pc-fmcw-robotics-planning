import numpy as np

import iscai.planning.planners as planners_module
from iscai.planning.planners import OracleConnectivityPlanner
from iscai.planning.trajectory import CandidateTrajectory
from iscai.prediction.link_predictor import LinkPredictor


def _candidate(points):
    states = np.zeros((len(points), 4), dtype=float)
    states[:, :2] = np.asarray(points, dtype=float)
    states[:, 3] = 5.0
    controls = np.zeros((max(0, len(points) - 1), 2), dtype=float)
    return CandidateTrajectory(states, controls, 1.0, 0.0, 5.0)


def test_p4_oracle_forecast_cannot_bypass_common_safety_prediction(monkeypatch):
    candidate = _candidate([[0, 0], [1, 0], [2, 0]])
    monkeypatch.setattr(planners_module, "generate_candidates", lambda *args, **kwargs: [candidate])

    planner = OracleConnectivityPlanner(LinkPredictor(), target_clearance=0.5)
    ego = np.array([0.0, 0.0, 0.0, 5.0])
    oracle_target = np.array([[20.0, 20.0], [20.0, 20.0], [20.0, 20.0]])
    common_safety_target = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])

    result = planner.plan(
        ego,
        oracle_target,
        obstacles=[],
        reference_speed=5.0,
        safety_target_prediction=common_safety_target,
    )

    assert result.candidate is None
    assert np.isinf(result.score)
    assert result.forecast is None
