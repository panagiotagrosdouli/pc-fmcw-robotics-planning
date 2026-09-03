import numpy as np
from iscai.planning.trajectory import generate_candidates
from iscai.planning.dynamics import VehicleParams


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
    # Steering also changes the bicycle rollout, so the dominant endpoint
    # displacement need not be exactly one metre; its lateral sign must agree.
    normal = np.array([-1.0, 0.0])
    assert np.dot(delta, normal) > 0.0


def test_zero_offset_is_unchanged_by_frame_fix():
    candidate = _single([2.0, -3.0, 0.7, 4.0], lateral=0.0)
    assert np.all(np.isfinite(candidate.states))
    assert np.allclose(candidate.states[0, :2], [2.0, -3.0])
