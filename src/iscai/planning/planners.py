"""Receding-horizon connectivity-aware planners and baselines."""

from dataclasses import dataclass
import numpy as np

from .costs import mobility_cost, connectivity_cost
from .feasibility import filter_feasible
from .trajectory import generate_candidates


@dataclass
class PlanningResult:
    candidate: object | None
    score: float
    forecast: object | None


class _BasePlanner:
    def __init__(self, link_predictor=None, connectivity_weight=1.0, vehicle_params=None):
        self.link_predictor = link_predictor
        self.connectivity_weight = connectivity_weight
        self.vehicle_params = vehicle_params

    def _candidates(self, ego_state, obstacles=None):
        candidates = generate_candidates(ego_state, params=self.vehicle_params)
        return filter_feasible(candidates, obstacles=obstacles)


class MobilityOnlyPlanner(_BasePlanner):
    """P0: ignores communication when selecting motion."""

    def plan(self, ego_state, target_prediction=None, obstacles=None, reference_speed=None):
        candidates = self._candidates(ego_state, obstacles)
        if not candidates:
            return PlanningResult(None, float("inf"), None)
        best = min(candidates, key=lambda c: mobility_cost(c, reference_speed))
        return PlanningResult(best, mobility_cost(best, reference_speed), None)


class ReactiveConnectivityPlanner(_BasePlanner):
    """P1: uses current/myopic target geometry rather than future target motion."""

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None):
        candidates = self._candidates(ego_state, obstacles)
        if not candidates:
            return PlanningResult(None, float("inf"), None)
        target = np.asarray(target_prediction, dtype=float)
        current = np.repeat(target[:1], max(len(c.states) for c in candidates), axis=0)
        best = None
        for candidate in candidates:
            forecast = self.link_predictor.predict(candidate, current)
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * connectivity_cost(forecast)
            if best is None or score < best.score:
                best = PlanningResult(candidate, score, forecast)
        return best


class PredictiveConnectivityPlanner(_BasePlanner):
    """P2: trajectory-conditioned prediction of future link quality."""

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None):
        candidates = self._candidates(ego_state, obstacles)
        if not candidates:
            return PlanningResult(None, float("inf"), None)

        best = None
        target = np.asarray(target_prediction, dtype=float)
        for candidate in candidates:
            n = min(len(candidate.states), len(target))
            forecast = self.link_predictor.predict(candidate, target[:n])
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * connectivity_cost(forecast)
            if best is None or score < best.score:
                best = PlanningResult(candidate, score, forecast)
        return best


class OracleConnectivityPlanner(PredictiveConnectivityPlanner):
    """P4: upper-bound planner using simulator ground-truth future target motion."""

    pass
