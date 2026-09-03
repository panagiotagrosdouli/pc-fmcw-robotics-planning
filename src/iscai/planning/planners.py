"""Receding-horizon connectivity-aware planners."""

from dataclasses import dataclass
from .costs import mobility_cost, connectivity_cost
from .feasibility import filter_feasible
from .trajectory import generate_candidates


@dataclass
class PlanningResult:
    candidate: object | None
    score: float
    forecast: object | None


class PredictiveConnectivityPlanner:
    def __init__(self, link_predictor, connectivity_weight=1.0, vehicle_params=None):
        self.link_predictor = link_predictor
        self.connectivity_weight = connectivity_weight
        self.vehicle_params = vehicle_params

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None):
        candidates = generate_candidates(ego_state, params=self.vehicle_params)
        candidates = filter_feasible(candidates, obstacles=obstacles)
        if not candidates:
            return PlanningResult(None, float("inf"), None)

        best = None
        for candidate in candidates:
            forecast = self.link_predictor.predict(candidate, target_prediction)
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * connectivity_cost(forecast)
            if best is None or score < best.score:
                best = PlanningResult(candidate, score, forecast)
        return best
