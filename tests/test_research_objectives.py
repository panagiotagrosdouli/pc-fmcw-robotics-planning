import numpy as np
import pytest

from pc_fmcw_robustness.objectives import (
    AdaptiveWeightConfig,
    ChanceConstraintConfig,
    RiskObjectiveConfig,
    adaptive_weighted_cost,
    chance_constrained_cost,
    risk_aware_connectivity_cost,
)


def test_risk_objective_penalizes_adverse_tail():
    samples = np.array([1.0, 1.0, 1.0, 10.0])
    mean_only = risk_aware_connectivity_cost(samples, RiskObjectiveConfig(risk_weight=0.0))
    risk_aware = risk_aware_connectivity_cost(samples, RiskObjectiveConfig(risk_weight=1.0, cvar_alpha=0.75))
    assert risk_aware > mean_only


def test_chance_constraint_marks_infeasible_candidate():
    config = ChanceConstraintConfig(snr_threshold_db=10.0, max_violation_probability=0.25, penalty=100.0)
    cost, probability, feasible = chance_constrained_cost(3.0, [5.0, 8.0, 15.0, 20.0], config)
    assert probability == pytest.approx(0.5)
    assert feasible is False
    assert cost == pytest.approx(103.0)


def test_adaptive_weighted_cost_reports_applied_weight():
    cost, weight = adaptive_weighted_cost(2.0, 0.8, AdaptiveWeightConfig(0.5, 2.0, 0.1))
    assert 0.5 < weight <= 2.0
    assert cost == pytest.approx(2.0 * weight)
