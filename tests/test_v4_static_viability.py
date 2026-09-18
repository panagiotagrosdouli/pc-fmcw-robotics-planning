import numpy as np

from iscai.planning.dynamics import VehicleParams
from iscai.planning.feasibility import check_obstacles, check_road_bounds, filter_with_diagnostics
from iscai.planning.trajectory import generate_candidates
from iscai.simulation.scenario import lane_choice


def test_bounded_brake_steer_reaches_a_valid_static_stop_from_initial_state():
    scenario = lane_choice()
    params = VehicleParams(dt=0.1)
    candidates = generate_candidates(
        scenario.ego_state, horizons=(5.0,), speed_offsets=(0.0,),
        params=params, bounded_brake_steer=True,
    )
    for candidate in candidates:
        speed = candidate.states[:-1, 3]
        lateral_acc = speed**2 * np.tan(candidate.controls[:, 1]) / params.wheelbase
        assert np.max(np.abs(lateral_acc)) <= params.max_lateral_accel + 1e-12
    emergency = [
        c for c in candidates
        if c.target_speed == 0 and np.all(c.controls[:, 0] == params.min_accel)
        and np.any(c.controls[:5, 1] != 0) and np.all(c.controls[5:, 1] == 0)
    ]
    assert {np.sign(c.controls[0, 1]) for c in emergency} == {-1, 1}
    assert any(check_road_bounds(c.states) and check_obstacles(c.states, scenario.obstacles)
               for c in emergency)
    for candidate in emergency:
        speed = candidate.states[:-1, 3]
        lateral_acc = speed**2 * np.tan(candidate.controls[:, 1]) / params.wheelbase
        assert np.max(np.abs(lateral_acc)) <= params.max_lateral_accel + 1e-12


def test_static_stop_viability_rejects_short_horizon_trap():
    scenario = lane_choice()
    params = VehicleParams(dt=0.1)
    candidates = generate_candidates(scenario.ego_state, params=params,
                                     bounded_brake_steer=True)
    feasible, counts = filter_with_diagnostics(
        candidates, obstacles=scenario.obstacles,
        require_static_stop_viability=True, vehicle_params=params,
    )
    assert counts["generated"] == sum(counts[k] for k in ("road", "speed", "static", "dynamic", "feasible"))
    assert feasible
    assert all(check_road_bounds(c.states) and check_obstacles(c.states, scenario.obstacles)
               for c in feasible)
