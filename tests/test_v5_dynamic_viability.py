import numpy as np

from iscai.planning.dynamics import VehicleParams, rollout
from iscai.planning.feasibility import check_dynamic_target, check_dynamic_stop_viability
from iscai.simulation.pc_fmcw_benchmark import _prediction


def test_next_step_prediction_is_compared_to_next_ego_state():
    states = np.array([[0., 0., 0., 0.], [2., 0., 0., 0.], [4., 0., 0., 0.]])
    target_future = np.array([[3., 0.], [5., 0.]])
    assert check_dynamic_target(states, target_future, min_clearance=2.)
    assert not check_dynamic_target(states, target_future, min_clearance=2., time_aligned=True)


def test_terminal_braking_detects_predicted_collision_after_candidate_horizon():
    params = VehicleParams(dt=0.1)
    states = rollout(np.array([0., 0., 0., 8.]), np.tile([0., 0.], (2, 1)), params)
    # The short candidate has clearance, but its straight braking continuation
    # catches the slower predicted target further ahead.
    target = np.array([[6., 0.], [6.1, 0.]])
    assert check_dynamic_target(states, target, min_clearance=2., time_aligned=True)
    assert not check_dynamic_stop_viability(states, target, params, min_clearance=2.)


def test_lateral_damping_is_causal_and_does_not_change_longitudinal_prediction():
    history = np.column_stack((np.arange(8)*0.6, np.arange(8)*0.1))
    baseline = _prediction(history, 20, 0.1)
    damped = _prediction(history, 20, 0.1, damped_lateral=True)
    np.testing.assert_allclose(damped[:, 0], baseline[:, 0])
    assert 0 < damped[0, 1] - history[-1, 1] < baseline[0, 1] - history[-1, 1]
    assert damped[-1, 1] < baseline[-1, 1]
