import pytest

from pc_fmcw_robustness.safety import safety_feasible


def test_safety_bound():
    assert safety_feasible(0.01, 0.05)
    assert not safety_feasible(0.1, 0.05)


def test_safety_probability_validation():
    with pytest.raises(ValueError):
        safety_feasible(1.1, 0.05)
