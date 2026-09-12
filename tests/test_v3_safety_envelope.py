import numpy as np

from iscai.planning.dynamics import VehicleParams
from iscai.planning.trajectory import generate_candidates
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings


def test_emergency_family_combines_braking_with_lateral_offsets():
    params = VehicleParams(dt=0.1, min_accel=-4.0)
    state = np.array([0.0, 0.0, 0.0, 10.0])
    offsets = (-1.5, 0.0, 1.5)
    candidates = generate_candidates(
        state,
        lateral_offsets=offsets,
        horizons=(3.0,),
        speed_offsets=(0.0,),
        params=params,
    )
    emergency = [
        c for c in candidates
        if np.allclose(c.controls[:, 0], params.min_accel) and c.target_speed == 0.0
    ]
    assert {c.lateral_offset for c in emergency} == set(offsets)
    assert all(np.all(c.states[:, 3] >= 0.0) for c in emergency)


def test_planning_margin_is_separate_from_physical_collision_distance():
    settings = BenchmarkSettings(
        collision_distance_m=2.0,
        planning_safety_margin_m=1.5,
    )
    assert settings.collision_distance_m == 2.0
    assert settings.planning_safety_margin_m == 1.5


def test_negative_planning_margin_is_rejected():
    try:
        BenchmarkSettings(planning_safety_margin_m=-0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative planning safety margin must be rejected")
