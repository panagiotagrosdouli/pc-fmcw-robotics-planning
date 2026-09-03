"""P3 uncertainty-aware predictive connectivity planner."""

from __future__ import annotations

import numpy as np

from .costs import mobility_cost
from .planners import PlanningResult, _BasePlanner
from .risk_cost import snr_samples_from_prediction, risk_cost


class RiskAwarePredictivePlanner(_BasePlanner):
    """P3: choose motion by mobility cost + uncertainty-aware outage risk.

    target_prediction must be a dict with keys:
      - mean_xy: (H, 2) future target mean positions
      - sigma_xy: (H, 2) future target standard deviations

    This planner propagates trajectory uncertainty through the current
    geometry-based link surrogate. Final paper claims require replacing or
    calibrating that surrogate with the frozen PC-FMCW link predictor.
    """

    def __init__(self, link_predictor=None, connectivity_weight=1.0,
                 vehicle_params=None, mc_samples=128, threshold_db=8.0,
                 risk_power=2.0, random_seed=0):
        super().__init__(link_predictor, connectivity_weight, vehicle_params)
        self.mc_samples = int(mc_samples)
        self.threshold_db = float(threshold_db)
        self.risk_power = float(risk_power)
        self.random_seed = random_seed

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None):
        candidates = self._candidates(ego_state, obstacles)
        if not candidates:
            return PlanningResult(None, float("inf"), None)

        mean_xy = np.asarray(target_prediction["mean_xy"], dtype=float)
        sigma_xy = np.asarray(target_prediction["sigma_xy"], dtype=float)
        if mean_xy.shape != sigma_xy.shape:
            raise ValueError("mean_xy and sigma_xy must have identical shape")

        best = None
        for idx, candidate in enumerate(candidates):
            n = min(len(candidate.states), len(mean_xy))
            ego_xy = candidate.states[:n, :2]
            snr_samples = snr_samples_from_prediction(
                mean_xy[:n], sigma_xy[:n], ego_xy,
                samples=self.mc_samples,
                rng=None if self.random_seed is None else self.random_seed + idx,
            )
            conn = risk_cost(snr_samples, self.threshold_db, self.risk_power)
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * conn
            forecast = {
                "snr_samples": snr_samples,
                "risk_cost": conn,
                "mean_outage_probability": float(np.mean(snr_samples < self.threshold_db)),
            }
            if best is None or score < best.score:
                best = PlanningResult(candidate, score, forecast)
        return best
