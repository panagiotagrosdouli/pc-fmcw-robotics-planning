import numpy as np

import iscai.planning.risk_aware_planner as p3_module
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner


class _DummyLink:
    pass


def test_p3_uses_explicit_common_safety_prediction(monkeypatch):
    planner = RiskAwarePredictivePlanner(_DummyLink(), mc_samples=1)
    recorded = {}

    def fake_candidates(ego_state, obstacles=None, safety_target_prediction=None):
        del ego_state, obstacles
        recorded["safety"] = safety_target_prediction
        return []

    monkeypatch.setattr(planner, "_candidates", fake_candidates)

    mean = np.array([[10.0, 0.0], [11.0, 0.0]])
    stochastic_target = {
        "mean_xy": mean,
        "sigma_xy": np.ones_like(mean),
    }
    common_safety = np.array(
        [
            [20.0, 1.0, 0.0, 0.0],
            [21.0, 1.0, 0.0, 0.0],
        ]
    )

    result = planner.plan(
        np.array([0.0, 0.0, 0.0, 5.0]),
        stochastic_target,
        safety_target_prediction=common_safety,
    )

    np.testing.assert_allclose(recorded["safety"], common_safety)
    assert result.candidate is None
    assert np.isinf(result.score)


def test_p3_defaults_safety_to_its_mean_prediction_container(monkeypatch):
    planner = RiskAwarePredictivePlanner(_DummyLink(), mc_samples=1)
    recorded = {}

    def fake_candidates(ego_state, obstacles=None, safety_target_prediction=None):
        del ego_state, obstacles
        recorded["safety"] = safety_target_prediction
        return []

    monkeypatch.setattr(planner, "_candidates", fake_candidates)

    mean = np.array([[10.0, 0.0], [11.0, 0.0]])
    target = {"mean_xy": mean, "sigma_xy": np.ones_like(mean)}
    planner.plan(np.array([0.0, 0.0, 0.0, 5.0]), target)

    assert recorded["safety"] is target
