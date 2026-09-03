import numpy as np

from iscai.prediction.link_predictor import LinkPredictor
from iscai.planning.planners import (
    MobilityOnlyPlanner,
    ReactiveConnectivityPlanner,
    PredictiveConnectivityPlanner,
    OracleConnectivityPlanner,
)
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner


def _ego():
    return np.array([0.0, 0.0, 0.0, 8.0])


def _target(h=30):
    t = np.arange(h) * 0.1
    out = np.zeros((h, 4))
    out[:, 0] = 15.0 + 6.0 * t
    out[:, 1] = 0.25
    out[:, 3] = 6.0
    return out


def test_p0_p1_p2_p4_return_feasible_candidate():
    link = LinkPredictor(reference_snr_db=20.0, reference_distance=10.0, min_snr_db=8.0)
    target = _target()
    planners = [
        MobilityOnlyPlanner(link),
        ReactiveConnectivityPlanner(link),
        PredictiveConnectivityPlanner(link),
        OracleConnectivityPlanner(link),
    ]
    for planner in planners:
        result = planner.plan(_ego(), target, obstacles=[], reference_speed=8.0)
        assert result.candidate is not None
        assert np.isfinite(result.score)


def test_p3_returns_candidate_with_seeded_uncertainty():
    link = LinkPredictor(reference_snr_db=20.0, reference_distance=10.0, min_snr_db=8.0)
    target = _target()
    planner = RiskAwarePredictivePlanner(
        link, mc_samples=8, threshold_db=8.0, random_seed=7
    )
    pred = {
        "mean_xy": target[:, :2],
        "sigma_xy": np.full((len(target), 2), 0.25),
    }
    result = planner.plan(_ego(), pred, obstacles=[], reference_speed=8.0)
    assert result.candidate is not None
    assert np.isfinite(result.score)
    assert "risk_cost" in result.forecast
