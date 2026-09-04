import numpy as np
import pytest

from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor
from iscai.planning.risk_cost import (
    adaptive_connectivity_weight,
    chance_violation_probability,
    empirical_cvar,
)
from iscai.planning.uncertainty_planners import (
    AdaptiveConnectivityPlanner,
    CVaRPredictiveConnectivityPlanner,
    ChanceConstrainedPredictivePlanner,
    WorstCasePredictiveConnectivityPlanner,
)


def _prediction(horizon=20):
    x = np.linspace(15.0, 25.0, horizon)
    mean = np.column_stack([x, np.zeros(horizon)])
    sigma = np.full_like(mean, 0.25)
    deterministic = np.zeros((horizon, 4), dtype=float)
    deterministic[:, :2] = mean
    deterministic[:, 3] = 6.0
    return deterministic, {"mean_xy": mean, "sigma_xy": sigma}


def test_empirical_cvar_uses_adverse_tail():
    assert empirical_cvar([0.0, 1.0, 2.0, 10.0], alpha=0.75) == pytest.approx(10.0)


def test_chance_probability_uses_worst_horizon_step():
    snr = np.array([[5.0, 20.0], [15.0, 20.0], [5.0, 20.0], [15.0, 20.0]])
    assert chance_violation_probability(snr, threshold_db=8.0) == pytest.approx(0.5)


def test_adaptive_weight_increases_with_risk():
    low = adaptive_connectivity_weight(0.05, 0.5, 2.0, 0.1)
    high = adaptive_connectivity_weight(0.8, 0.5, 2.0, 0.1)
    assert low == pytest.approx(0.5)
    assert high > low


def test_new_planners_return_candidates_under_nominal_prediction():
    link = PCFMCWPlanningLinkPredictor()
    ego = np.array([0.0, 0.0, 0.0, 10.0])
    deterministic, uncertain = _prediction()

    adaptive = AdaptiveConnectivityPlanner(link, connectivity_weight=0.5, max_connectivity_weight=2.0)
    result = adaptive.plan(ego, deterministic, safety_target_prediction=deterministic)
    assert result.candidate is not None
    assert result.forecast["applied_connectivity_weight"] >= 0.5

    for planner in (
        CVaRPredictiveConnectivityPlanner(link, mc_samples=2, random_seed=1),
        ChanceConstrainedPredictivePlanner(
            link,
            mc_samples=2,
            hard_constraint=False,
            max_violation_probability=0.5,
            random_seed=1,
        ),
        WorstCasePredictiveConnectivityPlanner(link, mc_samples=2, random_seed=1),
    ):
        result = planner.plan(ego, uncertain, safety_target_prediction=deterministic)
        assert result.candidate is not None
        assert np.isfinite(result.score)
