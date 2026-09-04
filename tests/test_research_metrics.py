import pytest

from pc_fmcw_robustness.metrics import compute_efficiency, relative_improvement


def test_relative_improvement_lower_is_better():
    assert relative_improvement(0.1, 0.08) == pytest.approx(0.2)


def test_compute_efficiency():
    assert compute_efficiency(0.2, 0.1) == pytest.approx(2.0)
