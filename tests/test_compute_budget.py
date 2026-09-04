import pytest

from pc_fmcw_robustness.compute import ComputeBudget


def test_compute_budget_validates_positive_mc_samples():
    with pytest.raises(ValueError):
        ComputeBudget(horizon_steps=10, mc_samples=0)


def test_compute_budget_accepts_matched_budget():
    budget = ComputeBudget(horizon_steps=20, mc_samples=32, candidate_budget=81)
    assert budget.mc_samples == 32
