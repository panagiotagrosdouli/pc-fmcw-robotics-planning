import numpy as np

from iscai.planning.dynamics import VehicleParams
from iscai.planning.trajectory import generate_candidates


def test_generate_candidates_contains_max_braking_for_every_horizon():
    params = VehicleParams(dt=0.1, min_accel=-4.0)
    state = np.array([0.0, 0.0, 0.0, 10.0])
    horizons = (2.0, 3.0, 4.0, 5.0)

    candidates = generate_candidates(state, horizons=horizons, params=params)

    for horizon in horizons:
        braking = [
            c for c in candidates
            if c.horizon == horizon
            and c.lateral_offset == 0.0
            and c.target_speed == 0.0
            and np.allclose(c.controls[:, 0], params.min_accel)
            and np.allclose(c.controls[:, 1], 0.0)
        ]
        assert braking, f"missing shared max-braking candidate for horizon={horizon}"
        assert braking[0].states[-1, 3] <= state[3]
        assert np.all(braking[0].states[:, 3] >= 0.0)


def test_emergency_braking_family_is_communication_agnostic():
    params = VehicleParams()
    state = np.array([1.0, -0.5, 0.1, 8.0])
    candidates = generate_candidates(state, horizons=(2.0,), params=params)
    braking = [
        c for c in candidates
        if c.horizon == 2.0
        and np.allclose(c.controls[:, 0], params.min_accel)
        and np.allclose(c.controls[:, 1], 0.0)
    ]
    assert len(braking) == 1
