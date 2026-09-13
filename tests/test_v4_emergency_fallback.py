import numpy as np

from iscai.planning.dynamics import VehicleParams
from iscai.planning.planners import MobilityOnlyPlanner


def test_v4_fallback_is_mobility_only_and_resolves_empty_dynamic_lattice():
    params = VehicleParams(dt=0.1)
    planner = MobilityOnlyPlanner(link_predictor=None, connectivity_weight=0.0,
                                  vehicle_params=params, target_clearance=100.0)
    ego = np.array([0.0, 0.0, 0.0, 10.0])
    # An intentionally impossible dynamic clearance empties the nominal hard
    # lattice.  V4 must return a shared max-braking fallback rather than None.
    target = np.repeat(np.array([[5.0, 0.0]]), 20, axis=0)
    result = planner.plan(ego, target_prediction=target, obstacles=np.empty((0, 3)))
    assert result.candidate is not None
    assert planner.last_emergency_fallback_used is True
    assert np.isclose(result.candidate.target_speed, 0.0)
    assert np.all(result.candidate.controls[:, 0] <= 0.0)


def test_v4_fallback_does_not_relax_static_obstacle_constraint():
    params = VehicleParams(dt=0.1)
    planner = MobilityOnlyPlanner(link_predictor=None, connectivity_weight=0.0,
                                  vehicle_params=params, target_clearance=100.0)
    ego = np.array([0.0, 0.0, 0.0, 10.0])
    target = np.repeat(np.array([[5.0, 0.0]]), 20, axis=0)
    # Huge-radius obstacle makes every trajectory statically infeasible.  V4
    # must not manufacture a fallback by weakening road/static hard safety.
    obstacles = np.array([[0.0, 0.0, 1000.0]])
    result = planner.plan(ego, target_prediction=target, obstacles=obstacles)
    assert result.candidate is None
    assert planner.last_emergency_fallback_used is False
