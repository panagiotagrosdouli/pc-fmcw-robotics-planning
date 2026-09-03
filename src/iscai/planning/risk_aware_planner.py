"""P3 uncertainty-aware predictive connectivity planner."""
from __future__ import annotations
import numpy as np
from .costs import mobility_cost
from .planners import PlanningResult, _BasePlanner
from .risk_cost import risk_cost


class RiskAwarePredictivePlanner(_BasePlanner):
    """P3: mobility + uncertainty-aware outage risk with common mean safety."""
    def __init__(self, link_predictor, connectivity_weight=1.0,
                 vehicle_params=None, mc_samples=128, threshold_db=8.0,
                 risk_power=2.0, random_seed=0, target_clearance=2.0):
        if link_predictor is None:
            raise ValueError("P3 requires the same link predictor used by P1/P2")
        super().__init__(link_predictor, connectivity_weight, vehicle_params, target_clearance)
        self.mc_samples = int(mc_samples)
        self.threshold_db = float(threshold_db)
        self.risk_power = float(risk_power)
        self.random_seed = random_seed

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        mean_xy = np.asarray(target_prediction["mean_xy"], dtype=float)
        sigma_xy = np.asarray(target_prediction["sigma_xy"], dtype=float)
        if mean_xy.shape != sigma_xy.shape or mean_xy.ndim != 2 or mean_xy.shape[1] != 2:
            raise ValueError("mean_xy and sigma_xy must have identical shape (H, 2)")
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return PlanningResult(None, float("inf"), None)
        best = None
        base_rng = np.random.default_rng(self.random_seed)
        candidate_seeds = base_rng.integers(0, np.iinfo(np.uint32).max, size=len(candidates), dtype=np.uint32)
        for idx, candidate in enumerate(candidates):
            n = min(len(candidate.states), len(mean_xy))
            rng = np.random.default_rng(int(candidate_seeds[idx]))
            target_samples = mean_xy[None, :n, :] + rng.normal(size=(self.mc_samples, n, 2)) * sigma_xy[None, :n, :]
            snr_samples = []
            for target_xy in target_samples:
                target = np.zeros((n, 4), dtype=float)
                target[:, :2] = target_xy
                forecast = self.link_predictor.predict(candidate, target)
                snr_samples.append(np.asarray(forecast.snr_db, dtype=float))
            snr_samples = np.stack(snr_samples)
            conn = risk_cost(snr_samples, self.threshold_db, self.risk_power)
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * conn
            forecast = {"snr_samples": snr_samples, "risk_cost": conn,
                        "mean_outage_probability": float(np.mean(snr_samples < self.threshold_db))}
            if best is None or score < best.score:
                best = PlanningResult(candidate, score, forecast)
        return best
