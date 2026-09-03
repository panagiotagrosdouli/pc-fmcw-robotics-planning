import numpy as np
import pytest

from iscai.simulation.pc_fmcw_benchmark import _realized_ttc


def _state(x, y, yaw, speed):
    return np.array([x, y, yaw, speed], dtype=float)


def test_realized_ttc_hits_clearance_boundary_for_closing_motion():
    ego = _state(0.0, 0.0, 0.0, 10.0)
    target = _state(12.0, 0.0, 0.0, 5.0)
    # Initial separation 12 m, clearance boundary 2 m, closing speed 5 m/s.
    assert _realized_ttc(ego, target, 2.0) == pytest.approx(2.0)


def test_realized_ttc_is_zero_inside_clearance_boundary():
    ego = _state(0.0, 0.0, 0.0, 4.0)
    target = _state(1.5, 0.0, 0.0, 4.0)
    assert _realized_ttc(ego, target, 2.0) == 0.0


def test_realized_ttc_is_infinite_for_non_intersecting_motion():
    ego = _state(0.0, 0.0, 0.0, 5.0)
    target = _state(0.0, 10.0, 0.0, 5.0)
    assert np.isinf(_realized_ttc(ego, target, 2.0))


def test_realized_ttc_rejects_negative_clearance():
    ego = _state(0.0, 0.0, 0.0, 5.0)
    target = _state(10.0, 0.0, 0.0, 5.0)
    with pytest.raises(ValueError, match="collision_distance_m"):
        _realized_ttc(ego, target, -1.0)
