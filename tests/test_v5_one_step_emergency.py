import numpy as np

from iscai.planning.dynamics import VehicleParams
from iscai.planning.planners import MobilityOnlyPlanner
from iscai.planning.trajectory import generate_emergency_one_step_candidates


def test_v5_emergency_candidates_are_exactly_one_control_interval():
    params = VehicleParams(dt=0.1)
    ego = np.array([0.0, 0.0, 0.0, 10.0])
    candidates = generate_emergency_one_step_candidates(ego, params=params)
    assert candidates
    for candidate in candidates:
        assert candidate.controls.shape == (1, 2)
        assert candidate.states.shape == (2, 4)
        assert np.isclose(candidate.horizon, params.dt)
        assert np.isclose(candidate.controls[0, 0], params.min_accel)
        assert abs(candidate.controls[0, 1]) <= params.max_steering


def test_v5_fallback_preserves_dynamic_target_hard_constraint():
    params = VehicleParams(dt=0.1)
    planner = MobilityOnlyPlanner(
        link_predictor=None, connectivity_weight=0.0,
        vehicle_params=params, target_clearance=100.0,
    )
    ego = np.array([0.0, 0.0, 0.0, 10.0])
    target = np.repeat(np.array([[5.0, 0.0]]), 20, axis=0)
    result = planner.plan(ego, target_prediction=target, obstacles=np.empty((0, 3)))
    assert result.candidate is None
    assert planner.last_emergency_fallback_used is False


def test_v5_fallback_does_not_relax_static_constraint():
    params = VehicleParams(dt=0.1)
    planner = MobilityOnlyPlanner(
        link_predictor=None, connectivity_weight=0.0,
        vehicle_params=params, target_clearance=2.0,
    )
    ego = np.array([0.0, 0.0, 0.0, 10.0])
    target = np.repeat(np.array([[100.0, 0.0]]), 20, axis=0)
    obstacles = np.array([[0.0, 0.0, 1000.0]])
    result = planner.plan(ego, target_prediction=target, obstacles=obstacles)
    assert result.candidate is None
    assert planner.last_emergency_fallback_used is False
