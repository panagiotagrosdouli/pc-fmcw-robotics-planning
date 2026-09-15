"""Receding-horizon connectivity-aware planners and baselines."""

from dataclasses import dataclass
import numpy as np

from .costs import mobility_cost, connectivity_cost
from .feasibility import filter_with_diagnostics, filter_emergency_one_step_with_diagnostics
from .trajectory import generate_candidates, generate_emergency_one_step_candidates


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


class _BasePlanner:
    def __init__(self, link_predictor=None, connectivity_weight=1.0, vehicle_params=None,
                 target_clearance=2.0):
        self.link_predictor = link_predictor
        self.connectivity_weight = connectivity_weight
        self.vehicle_params = vehicle_params
        self.target_clearance = float(target_clearance)
        self.last_feasibility_counts = None
        self.last_emergency_feasibility_counts = None
        self.last_emergency_fallback_used = False

    def _candidates(self, ego_state, obstacles=None, safety_target_prediction=None):
        self.last_emergency_fallback_used = False
        self.last_emergency_feasibility_counts = None
        target_xy = _target_xy(safety_target_prediction)
        candidates = generate_candidates(ego_state, params=self.vehicle_params)
        candidates, counts = filter_with_diagnostics(
            candidates,
            target_xy=target_xy,
            obstacles=obstacles,
            target_clearance=self.target_clearance,
        )
        self.last_feasibility_counts = counts
        if candidates:
            return candidates

        # V5 structural remediation: evaluate only the physically bounded next
        # action when the nominal long-horizon lattice is empty. The dedicated
        # emergency filter compares the executed next ego state to the first
        # future target state; no hard constraint is relaxed.
        emergency = generate_emergency_one_step_candidates(
            ego_state, params=self.vehicle_params
        )
        emergency_target = None if target_xy is None else target_xy[:1]
        emergency, emergency_counts = filter_emergency_one_step_with_diagnostics(
            emergency,
            target_xy=emergency_target,
            obstacles=obstacles,
            target_clearance=self.target_clearance,
        )
        self.last_emergency_feasibility_counts = emergency_counts
        if emergency:
            self.last_emergency_fallback_used = True
            # Communication-independent deterministic tie break. Maximum braking
            # is common to all candidates; prefer the smallest steering magnitude.
            emergency.sort(key=lambda c: abs(float(c.controls[0, 1])))
            return [emergency[0]]
        return []


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
        if self.last_emergency_fallback_used:
            candidate = candidates[0]
            return PlanningResult(candidate, mobility_cost(candidate, reference_speed), None)
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
        if self.last_emergency_fallback_used:
            candidate = candidates[0]
            return PlanningResult(candidate, mobility_cost(candidate, reference_speed), None)
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
