import numpy as np

from iscai.planning.feasibility import filter_dynamic_target
from iscai.planning.planners import PredictiveConnectivityPlanner
from iscai.planning.trajectory import CandidateTrajectory
from iscai.prediction.link_predictor import LinkForecast


def _candidate():
    # states[0] is the current ego state at k; states[1:] are k+1, k+2.
    states = np.array([
        [0.0, 0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0, 1.0],
        [2.0, 0.0, 0.0, 1.0],
    ])
    controls = np.zeros((2, 2))
    return CandidateTrajectory(states, controls, 0.2, 0.0, 1.0)


def test_dynamic_target_filter_aligns_prediction_with_k_plus_1_state():
    candidate = _candidate()
    target_xy = np.array([
        [1.0, 0.0],
        [10.0, 0.0],
    ])

    # The target collides with ego at k+1. An off-by-one comparison against
    # states[0] would incorrectly keep this candidate feasible.
    feasible = filter_dynamic_target([candidate], target_xy, min_clearance=0.5)
    assert feasible == []


class _RecordingLink:
    def __init__(self):
        self.ego = None
        self.target = None

    def predict(self, ego_trajectory, target_prediction, link_history=None):
        del link_history
        self.ego = np.asarray(ego_trajectory, dtype=float).copy()
        self.target = np.asarray(target_prediction, dtype=float).copy()
        n = min(len(self.ego), len(self.target))
        z = np.zeros(n)
        return LinkForecast(z, z, z, z, 1.0)


def test_predictive_connectivity_uses_future_candidate_states_only(monkeypatch):
    candidate = _candidate()
    link = _RecordingLink()
    planner = PredictiveConnectivityPlanner(link, connectivity_weight=1.0)
    monkeypatch.setattr(planner, "_candidates", lambda *args, **kwargs: [candidate])

    target = np.array([
        [5.0, 0.0, 0.0, 1.0],
        [6.0, 0.0, 0.0, 1.0],
    ])
    planner.plan(
        np.array([0.0, 0.0, 0.0, 1.0]),
        target,
        obstacles=[],
        reference_speed=1.0,
        safety_target_prediction=target,
    )

    assert np.array_equal(link.ego, candidate.states[1:])
    assert np.array_equal(link.target, target)
