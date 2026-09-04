"""Research planners for communication uncertainty.

These planners are deliberately separate from the frozen P0-P4 benchmark so
new hypotheses can be evaluated without changing historical baseline semantics.
All variants inherit the same candidate generation and safety filtering from
``_BasePlanner``.
"""

from __future__ import annotations

import numpy as np

from .costs import connectivity_cost, mobility_cost
from .planners import PlanningResult, _BasePlanner
from .risk_cost import (
    adaptive_connectivity_weight,
    chance_violation_probability,
    cvar_connectivity_cost,
    sample_outage_costs,
    snr_samples_from_prediction,
)


def _prediction_arrays(target_prediction):
    if not isinstance(target_prediction, dict):
        raise ValueError("uncertainty-aware planners require a prediction dict")
    if "mean_xy" not in target_prediction or "sigma_xy" not in target_prediction:
        raise ValueError("prediction dict must contain mean_xy and sigma_xy")
    mean_xy = np.asarray(target_prediction["mean_xy"], dtype=float)
    sigma_xy = np.asarray(target_prediction["sigma_xy"], dtype=float)
    if mean_xy.shape != sigma_xy.shape or mean_xy.ndim != 2 or mean_xy.shape[1] != 2:
        raise ValueError("mean_xy and sigma_xy must have identical shape (H, 2)")
    return mean_xy, sigma_xy


def _candidate_snr_samples(candidate, mean_xy, sigma_xy, link_predictor, mc_samples, rng):
    n = min(len(candidate.states), len(mean_xy))
    if n < 1:
        raise ValueError("candidate and target prediction must overlap in time")
    return snr_samples_from_prediction(
        mean_xy[:n],
        sigma_xy[:n],
        np.asarray(candidate.states[:n], dtype=float),
        samples=int(mc_samples),
        rng=rng,
        link_predictor=link_predictor,
    )


class CVaRPredictiveConnectivityPlanner(_BasePlanner):
    """Predictive planner minimizing expected outage loss plus CVaR tail risk."""

    def __init__(
        self,
        link_predictor,
        connectivity_weight=1.0,
        vehicle_params=None,
        mc_samples=32,
        threshold_db=8.0,
        cvar_alpha=0.9,
        cvar_weight=1.0,
        expected_weight=1.0,
        random_seed=0,
        target_clearance=2.0,
    ):
        if link_predictor is None:
            raise ValueError("CVaR planner requires a link predictor")
        super().__init__(link_predictor, connectivity_weight, vehicle_params, target_clearance)
        self.mc_samples = int(mc_samples)
        self.threshold_db = float(threshold_db)
        self.cvar_alpha = float(cvar_alpha)
        self.cvar_weight = float(cvar_weight)
        self.expected_weight = float(expected_weight)
        self.random_seed = int(random_seed)
        if self.mc_samples < 1:
            raise ValueError("mc_samples must be >= 1")
        if not 0.0 <= self.cvar_alpha < 1.0:
            raise ValueError("cvar_alpha must satisfy 0 <= alpha < 1")
        if self.cvar_weight < 0.0 or self.expected_weight < 0.0:
            raise ValueError("risk weights must be non-negative")

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        mean_xy, sigma_xy = _prediction_arrays(target_prediction)
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return PlanningResult(None, float("inf"), None)

        base_rng = np.random.default_rng(self.random_seed)
        candidate_seeds = base_rng.integers(0, np.iinfo(np.uint32).max, size=len(candidates), dtype=np.uint32)
        best = None
        for idx, candidate in enumerate(candidates):
            samples = _candidate_snr_samples(
                candidate, mean_xy, sigma_xy, self.link_predictor, self.mc_samples,
                np.random.default_rng(int(candidate_seeds[idx])),
            )
            conn = cvar_connectivity_cost(
                samples,
                threshold_db=self.threshold_db,
                alpha=self.cvar_alpha,
                expected_weight=self.expected_weight,
                cvar_weight=self.cvar_weight,
            )
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * conn
            losses = sample_outage_costs(samples, self.threshold_db)
            forecast = {
                "snr_samples": samples,
                "connectivity_cost": conn,
                "expected_outage_loss": float(np.mean(losses)),
                "cvar_alpha": self.cvar_alpha,
                "cvar_weight": self.cvar_weight,
            }
            if best is None or score < best.score:
                best = PlanningResult(candidate, float(score), forecast)
        return best


class ChanceConstrainedPredictivePlanner(_BasePlanner):
    """Predictive planner with an explicit empirical outage chance constraint.

    The constraint is ``max_t P(SNR_t < threshold_db) <= max_violation_probability``.
    With ``hard_constraint=True`` infeasible candidates are rejected.  The soft
    mode is useful for sensitivity analysis and adds a quadratic violation penalty.
    """

    def __init__(
        self,
        link_predictor,
        connectivity_weight=1.0,
        vehicle_params=None,
        mc_samples=32,
        threshold_db=8.0,
        max_violation_probability=0.1,
        hard_constraint=True,
        violation_penalty=100.0,
        random_seed=0,
        target_clearance=2.0,
    ):
        if link_predictor is None:
            raise ValueError("chance-constrained planner requires a link predictor")
        super().__init__(link_predictor, connectivity_weight, vehicle_params, target_clearance)
        self.mc_samples = int(mc_samples)
        self.threshold_db = float(threshold_db)
        self.max_violation_probability = float(max_violation_probability)
        self.hard_constraint = bool(hard_constraint)
        self.violation_penalty = float(violation_penalty)
        self.random_seed = int(random_seed)
        if self.mc_samples < 1:
            raise ValueError("mc_samples must be >= 1")
        if not 0.0 <= self.max_violation_probability <= 1.0:
            raise ValueError("max_violation_probability must be in [0,1]")
        if self.violation_penalty < 0.0:
            raise ValueError("violation_penalty must be non-negative")

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        mean_xy, sigma_xy = _prediction_arrays(target_prediction)
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return PlanningResult(None, float("inf"), None)

        base_rng = np.random.default_rng(self.random_seed)
        candidate_seeds = base_rng.integers(0, np.iinfo(np.uint32).max, size=len(candidates), dtype=np.uint32)
        best = None
        best_infeasible = None
        for idx, candidate in enumerate(candidates):
            samples = _candidate_snr_samples(
                candidate, mean_xy, sigma_xy, self.link_predictor, self.mc_samples,
                np.random.default_rng(int(candidate_seeds[idx])),
            )
            violation = chance_violation_probability(samples, self.threshold_db)
            feasible = violation <= self.max_violation_probability
            expected_outage = float(np.mean(sample_outage_costs(samples, self.threshold_db)))
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * expected_outage
            excess = max(0.0, violation - self.max_violation_probability)
            if not self.hard_constraint:
                score += self.violation_penalty * excess * excess
            forecast = {
                "snr_samples": samples,
                "chance_violation_probability": violation,
                "constraint_satisfied": bool(feasible),
                "expected_outage_loss": expected_outage,
            }
            result = PlanningResult(candidate, float(score), forecast)
            if feasible:
                if best is None or result.score < best.score:
                    best = result
            elif best_infeasible is None or violation < best_infeasible.forecast["chance_violation_probability"]:
                best_infeasible = result

        if best is not None:
            return best
        if self.hard_constraint:
            forecast = None if best_infeasible is None else {
                **best_infeasible.forecast,
                "all_candidates_infeasible": True,
            }
            return PlanningResult(None, float("inf"), forecast)
        return best_infeasible


class AdaptiveConnectivityPlanner(_BasePlanner):
    """P2-style predictive planner with state-dependent connectivity weight."""

    def __init__(
        self,
        link_predictor,
        connectivity_weight=1.0,
        vehicle_params=None,
        max_connectivity_weight=4.0,
        activation_threshold=0.1,
        target_clearance=2.0,
    ):
        if link_predictor is None:
            raise ValueError("adaptive planner requires a link predictor")
        super().__init__(link_predictor, connectivity_weight, vehicle_params, target_clearance)
        self.max_connectivity_weight = float(max_connectivity_weight)
        self.activation_threshold = float(activation_threshold)
        if self.max_connectivity_weight < float(connectivity_weight):
            raise ValueError("max_connectivity_weight must be >= connectivity_weight")

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return PlanningResult(None, float("inf"), None)
        target = np.asarray(target_prediction, dtype=float)
        best = None
        for candidate in candidates:
            n = min(len(candidate.states), len(target))
            forecast = self.link_predictor.predict(candidate, target[:n])
            predicted_risk = float(np.max(np.asarray(forecast.outage_probability, dtype=float)))
            applied_weight = adaptive_connectivity_weight(
                predicted_risk,
                base_weight=float(self.connectivity_weight),
                max_weight=self.max_connectivity_weight,
                activation_threshold=self.activation_threshold,
            )
            conn = connectivity_cost(forecast)
            score = mobility_cost(candidate, reference_speed) + applied_weight * conn
            metadata = {
                "forecast": forecast,
                "predicted_outage_risk": predicted_risk,
                "applied_connectivity_weight": applied_weight,
                "connectivity_cost": conn,
            }
            if best is None or score < best.score:
                best = PlanningResult(candidate, float(score), metadata)
        return best


class WorstCasePredictiveConnectivityPlanner(_BasePlanner):
    """Distributionally conservative baseline using worst sampled outage loss."""

    def __init__(
        self,
        link_predictor,
        connectivity_weight=1.0,
        vehicle_params=None,
        mc_samples=32,
        threshold_db=8.0,
        random_seed=0,
        target_clearance=2.0,
    ):
        if link_predictor is None:
            raise ValueError("worst-case planner requires a link predictor")
        super().__init__(link_predictor, connectivity_weight, vehicle_params, target_clearance)
        self.mc_samples = int(mc_samples)
        self.threshold_db = float(threshold_db)
        self.random_seed = int(random_seed)
        if self.mc_samples < 1:
            raise ValueError("mc_samples must be >= 1")

    def plan(self, ego_state, target_prediction, obstacles=None, reference_speed=None,
             safety_target_prediction=None):
        mean_xy, sigma_xy = _prediction_arrays(target_prediction)
        safety_target = target_prediction if safety_target_prediction is None else safety_target_prediction
        candidates = self._candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return PlanningResult(None, float("inf"), None)
        base_rng = np.random.default_rng(self.random_seed)
        candidate_seeds = base_rng.integers(0, np.iinfo(np.uint32).max, size=len(candidates), dtype=np.uint32)
        best = None
        for idx, candidate in enumerate(candidates):
            samples = _candidate_snr_samples(
                candidate, mean_xy, sigma_xy, self.link_predictor, self.mc_samples,
                np.random.default_rng(int(candidate_seeds[idx])),
            )
            losses = sample_outage_costs(samples, self.threshold_db)
            worst = float(np.max(losses))
            score = mobility_cost(candidate, reference_speed) + self.connectivity_weight * worst
            forecast = {
                "snr_samples": samples,
                "worst_outage_loss": worst,
                "expected_outage_loss": float(np.mean(losses)),
            }
            if best is None or score < best.score:
                best = PlanningResult(candidate, float(score), forecast)
        return best
