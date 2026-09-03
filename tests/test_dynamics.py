import numpy as np

from iscai.planning.dynamics import VehicleParams, rollout, step


def test_step_preserves_state_shape():
    state = np.array([0.0, 0.0, 0.0, 10.0])
    out = step(state, np.array([0.0, 0.0]), VehicleParams())
    assert out.shape == (4,)
    assert out[0] > state[0]


def test_rollout_length():
    params = VehicleParams(dt=0.1)
    states = rollout(np.array([0.0, 0.0, 0.0, 5.0]), np.zeros((10, 2)), params)
    assert states.shape == (11, 4)
