import numpy as np
from iscai.planning.feasibility import check_dynamic_target, filter_dynamic_target
from iscai.planning.trajectory import CandidateTrajectory
from iscai.prediction.link_predictor import LinkPredictor
from iscai.planning.planners import MobilityOnlyPlanner


def _candidate(points):
    states = np.zeros((len(points), 4), dtype=float)
    states[:, :2] = np.asarray(points, dtype=float)
    states[:, 3] = 5.0
    controls = np.zeros((max(0, len(points) - 1), 2), dtype=float)
    return CandidateTrajectory(states, controls, 1.0, 0.0, 5.0)


def test_dynamic_target_is_time_aligned_not_static_cloud():
    candidate = _candidate([[0, 0], [1, 0], [2, 0]])
    target = np.array([[10, 0], [1, 0], [10, 0]], dtype=float)
    assert check_dynamic_target(candidate.states, target, min_clearance=0.5) is False
    shifted = np.array([[1, 0], [10, 0], [10, 0]], dtype=float)
    assert check_dynamic_target(candidate.states, shifted, min_clearance=0.5) is True


def test_dynamic_filter_removes_collision_candidate():
    safe = _candidate([[0, 0], [1, 0], [2, 0]])
    unsafe = _candidate([[0, 1], [1, 1], [2, 1]])
    target = np.array([[10, 1], [1, 1], [10, 1]], dtype=float)
    kept = filter_dynamic_target([safe, unsafe], target, min_clearance=0.4)
    # CandidateTrajectory contains NumPy arrays, so dataclass equality is not a
    # valid membership test. Identity is the intended contract of this filter.
    assert any(candidate is safe for candidate in kept)
    assert all(candidate is not unsafe for candidate in kept)
    assert safe.feasible is True
    assert unsafe.feasible is False


def test_p0_uses_target_prediction_for_safety_not_connectivity_objective():
    planner = MobilityOnlyPlanner(LinkPredictor(), target_clearance=2.0)
    ego = np.array([0.0, 0.0, 0.0, 8.0])
    target = np.zeros((30, 4), dtype=float)
    target[:, 0] = np.linspace(1.0, 25.0, 30)
    result = planner.plan(ego, target, obstacles=[], reference_speed=8.0)
    if result.candidate is not None:
        n = min(len(result.candidate.states), len(target))
        d = np.linalg.norm(result.candidate.states[:n, :2] - target[:n, :2], axis=1)
        assert np.all(d >= 2.0)
