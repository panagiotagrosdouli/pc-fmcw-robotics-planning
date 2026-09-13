"""Receding-horizon connectivity-aware planners and baselines."""

from dataclasses import dataclass
import numpy as np

from .costs import mobility_cost, connectivity_cost
from .feasibility import filter_with_diagnostics
from .trajectory import generate_candidates


@dataclass
class PlanningResult:
    candidate: object | None
    score: float
    forecast: object | None


def _target_xy(target_prediction):
    if target_prediction is None:
        return None
    if isinstance(target_prediction, dict):
        if "mean_xy" not in target_prediction:
            raise ValueError("target prediction dict must contain mean_xy")
        target = np.asarray(target_prediction["mean_xy"], dtype=float)
    else:
        target = np.asarray(target_prediction, dtype=float)
    if target.ndim != 2 or target.shape[1] < 2:
        raise ValueError("target prediction must have shape (H, >=2)")
    return target[:, :2]


def _minimum_time_aligned_target_distance(candidate, target_xy):
    """Return minimum time-aligned distance to the predicted moving target."""
    if target_xy is None:
        return float("inf")
    target_xy = np.asarray(target_xy, dtype=float)
    n = min(len(candidate.states), len(target_xy))
    if n == 0:
        return float("inf")
    return float(np.min(np.linalg.norm(candidate.states[:n, :2] - target_xy[:n, :2], axis=1)))


class _BasePlanner:
    def __init__(self, link_predictor=None, connectivity_weight=1.0, vehicle_params=None,
                 target_clearance=2.0):
        self.link_predictor = link_predictor
        self.connectivity_weight = connectivity_weight
        self.vehicle_params = vehicle_params
        self.target_clearance = float(target_clearance)
        self.last_feasibility_counts = None
        self.last_emergency_fallback_used = False

    def _candidates(self, ego_state, obstacles=None, safety_target_prediction=None):
        """Return hard-feasible candidates or one common emergency fallback.

        V4 preserves the hard dynamic-target filter for normal operation.  If
        that filter empties the lattice, all planners use the same deterministic
        mobility-only fallback: among maximum-braking candidates that remain
        road/speed/static feasible, choose the one maximizing minimum
        time-aligned distance to the predicted target.  Communication is never
        consulted by this fallback.  The event is explicitly exposed through
        ``last_emergency_fallback_used`` for development and confirmatory audit.
        """
        target_xy = _target_xy(safety_target_prediction)
        candidates = generate_candidates(ego_state, params=self.vehicle_params)
        feasible, counts = filter_with_diagnostics(
            candidates,
            target_xy=target_xy,
            obstacles=obstacles,
            target_clearance=self.target_clearance,
        )
        self.last_feasibility_counts = counts
        self.last_emergency_fallback_used = False
        if feasible:
            return feasible

        # Rebuild because the first filtering pass marks rejected candidates
        # infeasible.  The fallback may relax only the predicted dynamic-target
        # constraint; road, speed and static-obstacle constraints remain hard.
        emergency = [c for c in generate_candidates(ego_state, params=self.vehicle_params)
                     if np.isclose(c.target_speed, 0.0)]
        static_feasible, _ = filter_with_diagnostics(
            emergency,
            target_xy=None,
            obstacles=obstacles,
            target_clearance=self.target_clearance,
        )
        if not static_feasible:
            return []
        best = max(
            static_feasible,
            key=lambda c: (_minimum_time_aligned_target_distance(c, target_xy),
                           -abs(float(c.lateral_offset)), -float(c.horizon)),
        )
        self.last_emergency_fallback_used = True
        return [best]


class MobilityOnlyPlanner(_BasePlanner):
    """P0: ignores communication in the objective but retains common safety filters."""
    def plan(self, ego_state, target_prediction=None, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return PlanningResult(None, float("inf"), None)
        best = min(candidates, key=lambda c: mobility_cost(c, reference_speed))
        return PlanningResult(best, mobility_cost(best, reference_speed), None)


class ReactiveConnectivityPlanner(_BasePlanner):
    """P1: current/myopic connectivity scoring with common predicted safety."""
    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
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
    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
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
    """P4: oracle only for connectivity forecasting; safety can use the common prediction."""
    pass
