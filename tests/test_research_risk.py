import numpy as np
import pytest

from pc_fmcw_robustness.risk import adaptive_connectivity_weight, chance_violation_probability, cvar


def test_cvar_uses_adverse_tail():
    samples = np.array([0.0, 1.0, 2.0, 10.0])
    assert cvar(samples, alpha=0.75) == pytest.approx(10.0)


def test_chance_violation_probability():
    samples = np.array([5.0, 10.0, 15.0, 20.0])
    assert chance_violation_probability(samples, threshold_db=12.0) == pytest.approx(0.5)


def test_adaptive_connectivity_weight_is_monotone():
    low = adaptive_connectivity_weight(0.05, 0.5, 2.0, 0.1)
    medium = adaptive_connectivity_weight(0.5, 0.5, 2.0, 0.1)
    high = adaptive_connectivity_weight(0.9, 0.5, 2.0, 0.1)
    assert low == pytest.approx(0.5)
    assert low < medium < high <= 2.0
