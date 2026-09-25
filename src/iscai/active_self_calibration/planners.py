"""C0--C4 planner family for decision-triggered active self-calibration."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from iscai.planning.costs import connectivity_cost, mobility_cost
from iscai.planning.dynamics import VehicleParams
from iscai.planning.feasibility import filter_with_diagnostics
from iscai.planning.trajectory import generate_candidates

from .belief import GridBelief
from .link_model import (
    LatentLinkParameters,
    NOMINAL_LATENT_PARAMETERS,
    ParameterizedPCFMCWLinkModel,
)

CALIBRATION_PLANNERS = ("C0", "C1", "C2", "C3", "C4")


@dataclass
class CalibrationPlanningResult:
    candidate: object | None
    score: float
    forecast: object | None
    candidate_index: int = -1
    nominal_candidate_index: int = -1
    decision_uncertainty: float = 0.0
    expected_decision_regret: float = 0.0
    information_active: bool = False
    probe_selected: bool = False
    information_gain: float = 0.0
    probe_cost: float = 0.0
    candidate_pool: tuple = ()


def decision_diagnostics(cost_matrix, weights):
    """Return belief-optimal index, ranking-disagreement probability and regret."""
    costs = np.asarray(cost_matrix, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if costs.ndim != 2 or costs.shape[1] != len(weights) or costs.shape[0] == 0:
        raise ValueError("cost_matrix must have shape (K, M) matching weights")
    if np.any(~np.isfinite(costs)) or np.any(weights < 0.0) or not np.isfinite(weights).all():
        raise ValueError("costs and weights must be finite; weights non-negative")
    total = float(weights.sum())
    if total <= 0.0:
        raise ValueError("weights must have positive mass")
    weights = weights / total
    expected = costs @ weights
    baseline_idx = int(np.argmin(expected))
    per_hypothesis_best = np.argmin(costs, axis=0)
    disagreement = float(np.sum(weights[per_hypothesis_best != baseline_idx]))
    regret = float(np.sum(weights * (costs[baseline_idx, :] - np.min(costs, axis=0))))
    return baseline_idx, disagreement, max(0.0, regret), expected


def true_candidate_objective(
    model,
    candidate,
    target_prediction,
    parameters: LatentLinkParameters,
    reference_speed,
    connectivity_weight: float,
) -> float:
    """Oracle-parameter objective for evaluation only."""
    target = np.asarray(target_prediction, dtype=float)
    n = min(len(candidate.states), len(target))
    forecast = model.predict(candidate, target[:n], parameters)
    return float(
        mobility_cost(candidate, reference_speed)
        + connectivity_weight * connectivity_cost(forecast)
    )


class ActiveSelfCalibrationPlanner:
    """One implementation covering C0--C4 with a strict oracle boundary."""

    def __init__(
        self,
        mode: str,
        link_model: ParameterizedPCFMCWLinkModel,
        *,
        belief: GridBelief | None = None,
        nominal_parameters: LatentLinkParameters = NOMINAL_LATENT_PARAMETERS,
        oracle_parameters: LatentLinkParameters | None = None,
        connectivity_weight: float = 1.0,
        information_weight: float = 0.45,
        probe_weight: float = 0.20,
        decision_threshold: float = 0.25,
        min_expected_regret: float = 0.0,
        information_horizon_steps: int = 4,
        vehicle_params: VehicleParams | None = None,
        target_clearance: float = 2.5,
        physical_target_clearance: float | None = 2.0,
        require_static_stop_viability: bool = True,
        bounded_brake_steer: bool = True,
        time_aligned_dynamic: bool = True,
        require_dynamic_stop_viability: bool = True,
        lateral_offsets=(-1.0, 0.0, 1.0),
        horizons=(2.0, 3.0),
        speed_offsets=(-1.5, 0.0, 1.5),
    ) -> None:
        if mode not in CALIBRATION_PLANNERS:
            raise ValueError(f"unknown calibration planner mode: {mode}")
        if mode != "C4" and oracle_parameters is not None:
            raise ValueError("deployable planners C0-C3 cannot receive latent true parameters")
        if mode == "C4" and oracle_parameters is None:
            raise ValueError("C4 requires oracle_parameters")
        if mode in {"C1", "C2", "C3"} and belief is None:
            raise ValueError(f"{mode} requires an uncertainty belief")
        self.mode = mode
        self.link_model = link_model
        self.belief = belief
        self.nominal_parameters = nominal_parameters
        self._oracle_parameters = oracle_parameters if mode == "C4" else None
        self.connectivity_weight = float(connectivity_weight)
        self.information_weight = float(information_weight)
        self.probe_weight = float(probe_weight)
        self.decision_threshold = float(decision_threshold)
        self.min_expected_regret = float(min_expected_regret)
        self.information_horizon_steps = int(information_horizon_steps)
        self.vehicle_params = vehicle_params or VehicleParams()
        self.target_clearance = float(target_clearance)
        self.physical_target_clearance = (
            None if physical_target_clearance is None else float(physical_target_clearance)
        )
        if self.physical_target_clearance is not None and self.physical_target_clearance > self.target_clearance:
            raise ValueError("physical_target_clearance cannot exceed target_clearance")
        self.require_static_stop_viability = bool(require_static_stop_viability)
        self.bounded_brake_steer = bool(bounded_brake_steer)
        self.time_aligned_dynamic = bool(time_aligned_dynamic)
        self.require_dynamic_stop_viability = bool(require_dynamic_stop_viability)
        self.lateral_offsets = tuple(float(x) for x in lateral_offsets)
        self.horizons = tuple(float(x) for x in horizons)
        self.speed_offsets = tuple(float(x) for x in speed_offsets)
        self.last_feasibility_counts = None
        self.last_buffered_feasibility_counts = None
        self.last_margin_relaxed = False
        self.calibration_updates = 0

    @staticmethod
    def _target_array(target_prediction) -> np.ndarray:
        if isinstance(target_prediction, dict):
            target_prediction = target_prediction.get("mean_xy")
        target = np.asarray(target_prediction, dtype=float)
        if target.ndim != 2 or target.shape[1] < 2:
            raise ValueError("target prediction must have shape (H, >=2)")
        return target

    def _safe_candidates(self, ego_state, obstacles, safety_target_prediction):
        target_xy = self._target_array(safety_target_prediction)[:, :2]

        def filtered(clearance):
            generated = generate_candidates(
                ego_state,
                lateral_offsets=self.lateral_offsets,
                horizons=self.horizons,
                speed_offsets=self.speed_offsets,
                params=self.vehicle_params,
                bounded_brake_steer=self.bounded_brake_steer,
            )
            return filter_with_diagnostics(
                generated,
                target_xy=target_xy,
                obstacles=obstacles,
                target_clearance=clearance,
                require_static_stop_viability=self.require_static_stop_viability,
                vehicle_params=self.vehicle_params,
                time_aligned_dynamic=self.time_aligned_dynamic,
                require_dynamic_stop_viability=self.require_dynamic_stop_viability,
            )

        candidates, counts = filtered(self.target_clearance)
        self.last_buffered_feasibility_counts = counts
        self.last_margin_relaxed = False
        if (
            not candidates
            and self.physical_target_clearance is not None
            and self.physical_target_clearance < self.target_clearance
        ):
            candidates, counts = filtered(self.physical_target_clearance)
            self.last_margin_relaxed = bool(candidates)
        self.last_feasibility_counts = counts
        return candidates

    def _fixed_costs(self, candidates, target, reference_speed, parameters):
        values = np.empty(len(candidates), dtype=float)
        for i, candidate in enumerate(candidates):
            values[i] = true_candidate_objective(
                self.link_model,
                candidate,
                target,
                parameters,
                reference_speed,
                self.connectivity_weight,
            )
        return values

    def _belief_cost_matrix(self, candidates, target, reference_speed):
        matrix=np.empty((len(candidates),len(self.belief.support)),dtype=float)
        fast=hasattr(self.link_model,"connectivity_costs_hypotheses")
        for i,candidate in enumerate(candidates):
            if fast:
                n=min(len(candidate.states),len(target))
                connectivity=self.link_model.connectivity_costs_hypotheses(
                    candidate,np.asarray(target,dtype=float)[:n],self.belief.support
                )
                matrix[i,:]=(
                    mobility_cost(candidate,reference_speed)
                    +self.connectivity_weight*connectivity
                )
            else:
                for j,parameters in enumerate(self.belief.support):
                    matrix[i,j]=true_candidate_objective(
                        self.link_model,candidate,target,parameters,
                        reference_speed,self.connectivity_weight,
                    )
        return matrix

    def _probe_cost(self, candidate, baseline, reference_speed):
        u = np.asarray(candidate.controls[0] if len(candidate.controls) else [0.0, 0.0], dtype=float)
        u0 = np.asarray(baseline.controls[0] if len(baseline.controls) else [0.0, 0.0], dtype=float)
        accel_span = max(self.vehicle_params.max_accel - self.vehicle_params.min_accel, 1e-12)
        steer_span = max(2.0 * self.vehicle_params.max_steering, 1e-12)
        control_deviation = ((u[0] - u0[0]) / accel_span) ** 2 + ((u[1] - u0[1]) / steer_span) ** 2
        mobility_excess = max(0.0, mobility_cost(candidate, reference_speed) - mobility_cost(baseline, reference_speed))
        return float(control_deviation + 0.05 * mobility_excess)

    def _information_gain(self, candidate, target):
        if self.belief is None or len(candidate.states) <= 1:
            return 0.0
        n = min(len(candidate.states) - 1, len(target), self.information_horizon_steps)
        if n <= 0:
            return 0.0
        return self.belief.expected_information_gain(
            self.link_model,
            np.asarray(candidate.states[1 : n + 1], dtype=float),
            np.asarray(target[:n], dtype=float),
            max_measurements=n,
        )

    def plan(
        self,
        ego_state,
        target_prediction,
        *,
        obstacles=None,
        reference_speed=None,
        safety_target_prediction=None,
    ) -> CalibrationPlanningResult:
        target = self._target_array(target_prediction)
        safety_target = target if safety_target_prediction is None else safety_target_prediction
        candidates = self._safe_candidates(ego_state, obstacles, safety_target)
        if not candidates:
            return CalibrationPlanningResult(None, float("inf"), None)

        candidate_pool = tuple(candidates)
        if self.mode == "C0":
            costs = self._fixed_costs(candidates, target, reference_speed, self.nominal_parameters)
            selected = int(np.argmin(costs))
            forecast = self.link_model.predict(candidates[selected], target, self.nominal_parameters)
            return CalibrationPlanningResult(
                candidates[selected], float(costs[selected]), forecast,
                selected, selected, candidate_pool=candidate_pool,
            )
        if self.mode == "C4":
            costs = self._fixed_costs(candidates, target, reference_speed, self._oracle_parameters)
            selected = int(np.argmin(costs))
            forecast = self.link_model.predict(candidates[selected], target, self._oracle_parameters)
            return CalibrationPlanningResult(
                candidates[selected], float(costs[selected]), forecast,
                selected, selected, candidate_pool=candidate_pool,
            )

        matrix = self._belief_cost_matrix(candidates, target, reference_speed)
        baseline_idx, uncertainty, expected_regret, expected_costs = decision_diagnostics(
            matrix, self.belief.weights
        )
        information_active = self.mode == "C2" or (
            self.mode == "C3"
            and uncertainty > self.decision_threshold
            and expected_regret > self.min_expected_regret
        )
        scores = expected_costs.copy()
        information = np.zeros(len(candidates), dtype=float)
        probe_costs = np.zeros(len(candidates), dtype=float)
        if information_active:
            baseline = candidates[baseline_idx]
            for i, candidate in enumerate(candidates):
                information[i] = self._information_gain(candidate, target)
                probe_costs[i] = self._probe_cost(candidate, baseline, reference_speed)
            relevance = 1.0 if self.mode == "C2" else uncertainty
            scores = (
                scores
                + self.probe_weight * probe_costs
                - self.information_weight * relevance * information
            )
        selected = int(np.argmin(scores))
        estimate = self.belief.mean_parameters()
        forecast = self.link_model.predict(candidates[selected], target, estimate)
        return CalibrationPlanningResult(
            candidate=candidates[selected],
            score=float(scores[selected]),
            forecast=forecast,
            candidate_index=selected,
            nominal_candidate_index=baseline_idx,
            decision_uncertainty=float(uncertainty),
            expected_decision_regret=float(expected_regret),
            information_active=bool(information_active),
            probe_selected=bool(information_active and selected != baseline_idx),
            information_gain=float(information[selected]),
            probe_cost=float(probe_costs[selected]),
            candidate_pool=candidate_pool,
        )

    def observe(self, ego_state, target_state, observed_snr_db: float) -> None:
        """Apply one causal communication-model update after an action is executed."""
        if self.mode in {"C1", "C2", "C3"}:
            self.belief.update_snr(self.link_model, ego_state, target_state, observed_snr_db)
            self.calibration_updates += 1

    def current_parameter_estimate(self) -> LatentLinkParameters:
        if self.mode == "C0":
            return self.nominal_parameters
        if self.mode == "C4":
            return self._oracle_parameters
        return self.belief.mean_parameters()
