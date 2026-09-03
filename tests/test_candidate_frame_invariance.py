import numpy as np
from iscai.planning.trajectory import generate_candidates
from iscai.planning.dynamics import VehicleParams, rollout


def _single(state, lateral=1.0):
    return generate_candidates(
        np.asarray(state, float),
        lateral_offsets=(lateral,),
        horizons=(2.0,),
        speed_offsets=(0.0,),
        params=VehicleParams(dt=0.1),
    )[0]


def test_lateral_offset_follows_ego_heading_normal():
    # Heading +90 deg: the left normal points toward global -x, not +y.
    base = _single([0.0, 0.0, np.pi / 2, 5.0], lateral=0.0)
    left = _single([0.0, 0.0, np.pi / 2, 5.0], lateral=1.0)
    delta = left.states[-1, :2] - base.states[-1, :2]
    normal = np.array([-1.0, 0.0])
    assert np.dot(delta, normal) > 0.0


def test_candidate_states_are_exact_control_rollout():
    """Candidate geometry must be exactly what its executable controls produce."""
    params = VehicleParams(dt=0.1)
    initial = np.array([1.2, -0.7, 0.45, 6.0])
    candidate = generate_candidates(
        initial,
        lateral_offsets=(1.0,),
        horizons=(3.0,),
        speed_offsets=(2.0,),
        params=params,
    )[0]
    reproduced = rollout(initial, candidate.controls, params)
    assert np.allclose(candidate.states, reproduced, rtol=1e-12, atol=1e-12)


def test_rotation_translation_equivariance():
    """Rigidly transforming the initial pose must rigidly transform the path."""
    theta = 0.8
    translation = np.array([4.0, -2.0])
    base_state = np.array([0.3, -0.2, 0.25, 5.0])
    base = _single(base_state, lateral=1.0)
    rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    transformed_state = base_state.copy()
    transformed_state[:2] = rotation @ base_state[:2] + translation
    transformed_state[2] += theta
    transformed = _single(transformed_state, lateral=1.0)
    expected_xy = base.states[:, :2] @ rotation.T + translation
    assert np.allclose(transformed.states[:, :2], expected_xy, rtol=1e-10, atol=1e-10)
    heading_delta = np.unwrap(transformed.states[:, 2]) - np.unwrap(base.states[:, 2])
    assert np.allclose(heading_delta, theta, rtol=1e-10, atol=1e-10)
    assert np.allclose(transformed.controls, base.controls, rtol=1e-12, atol=1e-12)


def test_zero_offset_remains_finite_and_starts_at_initial_pose():
    candidate = _single([2.0, -3.0, 0.7, 4.0], lateral=0.0)
    assert np.all(np.isfinite(candidate.states))
    assert np.allclose(candidate.states[0, :2], [2.0, -3.0])
