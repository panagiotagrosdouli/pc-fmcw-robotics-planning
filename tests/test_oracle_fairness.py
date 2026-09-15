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
    """P4 may use truth for connectivity scoring, never for hard safety.

    V5 legitimately falls back to a one-step emergency action when the nominal
    lattice is rejected.  Make that emergency action unsafe under the common
    safety prediction but safe under the oracle trajectory.  A correct P4 must
    therefore still return no candidate.
    """
    candidate = _candidate([[0, 0], [1, 0], [2, 0]])
    emergency = _candidate([[0, 0], [0.5, 0]])
    emergency.controls = np.array([[-4.0, 0.0]])
    emergency.horizon = 0.1
    monkeypatch.setattr(planners_module, "generate_candidates", lambda *args, **kwargs: [candidate])
    monkeypatch.setattr(
        planners_module,
        "generate_emergency_one_step_candidates",
        lambda *args, **kwargs: [emergency],
    )

    planner = OracleConnectivityPlanner(LinkPredictor(), target_clearance=0.5)
    ego = np.array([0.0, 0.0, 0.0, 5.0])
    oracle_target = np.array([[20.0, 20.0], [20.0, 20.0], [20.0, 20.0]])
    # Nominal candidate is unsafe at every aligned state; the V5 emergency next
    # state [0.5, 0] is also unsafe against the first future common-safety state.
    common_safety_target = np.array([[0.5, 0.0], [1.0, 0.0], [2.0, 0.0]])

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
    assert planner.last_emergency_fallback_used is False
