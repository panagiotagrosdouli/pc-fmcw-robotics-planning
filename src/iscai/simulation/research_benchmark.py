"""Closed-loop research benchmark for robotics under communication uncertainty.

This module extends, rather than replaces, the frozen P0-P4 benchmark.  It keeps
common motion dynamics, candidate generation, safety filtering, scenario seeds,
and realized-link evaluation while allowing explicitly versioned information and
risk formulations to be compared under prediction error and link-model shift.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
import numpy as np

from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor
from iscai.connectivity.stress import (
    LinkStressProfile,
    TimeIndexedStressedLinkPredictor,
    make_mismatched_pc_fmcw_predictor,
)
from iscai.planning.dynamics import VehicleParams, step
from iscai.planning.planners import (
    MobilityOnlyPlanner,
    OracleConnectivityPlanner,
    PredictiveConnectivityPlanner,
    ReactiveConnectivityPlanner,
)
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner
from iscai.planning.uncertainty_planners import (
    AdaptiveConnectivityPlanner,
    CVaRPredictiveConnectivityPlanner,
    ChanceConstrainedPredictivePlanner,
    WorstCasePredictiveConnectivityPlanner,
)
from iscai.simulation.pc_fmcw_benchmark import (
    _candidate_feasibility_counts,
    _first_control,
    _prediction,
    _realized_ttc,
    _truth_horizon,
)
from iscai.simulation.scenario import make_primary_scenarios


RESEARCH_PLANNERS = (
    "P0",
    "P1",
    "P2",
    "P3",
    "P4",
    "P2-CVaR",
    "P2-Chance",
    "P2-Adaptive",
    "P2-Worst",
)


@dataclass(frozen=True)
class ResearchBenchmarkSettings:
    protocol_version: str = "research-framework-v1"
    dt: float = 0.1
    history_steps: int = 8
    horizon_steps: int = 20
    observation_sigma_m: float = 0.20
    prediction_sigma_m: float = 0.75
    connectivity_weight: float = 1.0
    mc_samples: int = 32
    collision_distance_m: float = 2.0

    # Risk formulations.
    cvar_alpha: float = 0.9
    cvar_weight: float = 1.0
    chance_max_violation_probability: float = 0.1
    chance_hard_constraint: bool = True
    chance_violation_penalty: float = 100.0
    adaptive_max_connectivity_weight: float = 4.0
    adaptive_activation_threshold: float = 0.1

    # Prediction-channel shift.  These affect connectivity planning only unless
    # stress_safety_prediction is explicitly enabled.
    prediction_bias_x_m: float = 0.0
    prediction_bias_y_m: float = 0.0
    prediction_noise_scale: float = 1.0
    reported_uncertainty_scale: float = 1.0
    observation_delay_steps: int = 0
    stress_safety_prediction: bool = False

    # Planner-only link-model mismatch; realized evaluation uses the reference.
    reference_snr_bias_db: float = 0.0
    pathloss_scale: float = 1.0
    beam_sigma_scale: float = 1.0
    outage_threshold_bias_db: float = 0.0

    # Time-indexed channel stress.  If visible_to_planner=False it is an
    # unmodeled distribution shift; otherwise predictive planners can foresee it.
    blackout_kind: str = "none"
    blackout_attenuation_db: float = 20.0
    blackout_visible_to_planner: bool = False

    def __post_init__(self):
        if self.protocol_version != "research-framework-v1":
            raise ValueError("unknown research protocol version")
        if not np.isfinite(self.dt) or self.dt <= 0.0:
            raise ValueError("dt must be positive and finite")
        if self.history_steps < 2 or self.horizon_steps < 1:
            raise ValueError("history_steps >= 2 and horizon_steps >= 1 are required")
        for name in ("observation_sigma_m", "prediction_sigma_m", "connectivity_weight", "collision_distance_m"):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.mc_samples < 1:
            raise ValueError("mc_samples must be >= 1")
        if not 0.0 <= self.cvar_alpha < 1.0:
            raise ValueError("cvar_alpha must satisfy 0 <= alpha < 1")
        if self.cvar_weight < 0.0:
            raise ValueError("cvar_weight must be non-negative")
        if not 0.0 <= self.chance_max_violation_probability <= 1.0:
            raise ValueError("chance_max_violation_probability must be in [0,1]")
        if self.chance_violation_penalty < 0.0:
            raise ValueError("chance_violation_penalty must be non-negative")
        if self.adaptive_max_connectivity_weight < self.connectivity_weight:
            raise ValueError("adaptive max weight must be >= base connectivity weight")
        if not 0.0 <= self.adaptive_activation_threshold < 1.0:
            raise ValueError("adaptive_activation_threshold must be in [0,1)")
        if self.prediction_noise_scale < 0.0 or self.reported_uncertainty_scale < 0.0:
            raise ValueError("prediction noise/uncertainty scales must be non-negative")
        if self.observation_delay_steps < 0:
            raise ValueError("observation_delay_steps must be non-negative")
        if self.pathloss_scale <= 0.0 or self.beam_sigma_scale <= 0.0:
            raise ValueError("link mismatch scales must be positive")
        LinkStressProfile(kind=self.blackout_kind, attenuation_db=self.blackout_attenuation_db)


def _velocity_xy(state):
    state = np.asarray(state, dtype=float)
    return state[3] * np.array([np.cos(state[2]), np.sin(state[2])])


def _planner_prediction(observations, settings, rng):
    available_end = max(1, len(observations) - int(settings.observation_delay_steps))
    history = observations[:available_end][-settings.history_steps :]
    base = _prediction(history, settings.horizon_steps, settings.dt)
    stressed = base.copy()
    stressed[:, 0] += float(settings.prediction_bias_x_m)
    stressed[:, 1] += float(settings.prediction_bias_y_m)
    extra_sigma = max(0.0, float(settings.prediction_noise_scale) - 1.0) * float(settings.prediction_sigma_m)
    if extra_sigma > 0.0:
        stressed[:, :2] += rng.normal(0.0, extra_sigma, size=stressed[:, :2].shape)
    return base, stressed


def _make_link_models(settings, episode_steps):
    truth = PCFMCWPlanningLinkPredictor()
    planning = make_mismatched_pc_fmcw_predictor(
        truth,
        reference_snr_bias_db=settings.reference_snr_bias_db,
        pathloss_scale=settings.pathloss_scale,
        beam_sigma_scale=settings.beam_sigma_scale,
        outage_threshold_bias_db=settings.outage_threshold_bias_db,
    )
    profile = LinkStressProfile(
        kind=settings.blackout_kind,
        attenuation_db=settings.blackout_attenuation_db,
    )
    realized = TimeIndexedStressedLinkPredictor(truth, profile, episode_steps=episode_steps)
    if settings.blackout_visible_to_planner:
        planning = TimeIndexedStressedLinkPredictor(planning, profile, episode_steps=episode_steps)
    return planning, realized


def _make_planner(planner_name, settings, params, planning_link, seed):
    common = dict(vehicle_params=params, target_clearance=settings.collision_distance_m)
    if planner_name == "P0":
        return MobilityOnlyPlanner(planning_link, connectivity_weight=0.0, **common)
    if planner_name == "P1":
        return ReactiveConnectivityPlanner(planning_link, connectivity_weight=settings.connectivity_weight, **common)
    if planner_name == "P2":
        return PredictiveConnectivityPlanner(planning_link, connectivity_weight=settings.connectivity_weight, **common)
    if planner_name == "P3":
        return RiskAwarePredictivePlanner(
            planning_link,
            connectivity_weight=settings.connectivity_weight,
            mc_samples=settings.mc_samples,
            random_seed=seed,
            **common,
        )
    if planner_name == "P4":
        return OracleConnectivityPlanner(planning_link, connectivity_weight=settings.connectivity_weight, **common)
    if planner_name == "P2-CVaR":
        return CVaRPredictiveConnectivityPlanner(
            planning_link,
            connectivity_weight=settings.connectivity_weight,
            mc_samples=settings.mc_samples,
            cvar_alpha=settings.cvar_alpha,
            cvar_weight=settings.cvar_weight,
            random_seed=seed,
            **common,
        )
    if planner_name == "P2-Chance":
        return ChanceConstrainedPredictivePlanner(
            planning_link,
            connectivity_weight=settings.connectivity_weight,
            mc_samples=settings.mc_samples,
            max_violation_probability=settings.chance_max_violation_probability,
            hard_constraint=settings.chance_hard_constraint,
            violation_penalty=settings.chance_violation_penalty,
            random_seed=seed,
            **common,
        )
    if planner_name == "P2-Adaptive":
        return AdaptiveConnectivityPlanner(
            planning_link,
            connectivity_weight=settings.connectivity_weight,
            max_connectivity_weight=settings.adaptive_max_connectivity_weight,
            activation_threshold=settings.adaptive_activation_threshold,
            **common,
        )
    if planner_name == "P2-Worst":
        return WorstCasePredictiveConnectivityPlanner(
            planning_link,
            connectivity_weight=settings.connectivity_weight,
            mc_samples=settings.mc_samples,
            random_seed=seed,
            **common,
        )
    raise ValueError(f"unknown research planner: {planner_name}")


def _set_model_step(model, step_index):
    if hasattr(model, "set_step"):
        model.set_step(step_index)


def _extract_planner_metadata(result):
    metadata = result.forecast if isinstance(result.forecast, dict) else {}
    return {
        "applied_connectivity_weight": float(metadata.get("applied_connectivity_weight", np.nan)),
        "chance_violation_probability": float(metadata.get("chance_violation_probability", np.nan)),
        "constraint_satisfied": metadata.get("constraint_satisfied", np.nan),
        "expected_outage_loss": float(metadata.get("expected_outage_loss", np.nan)),
        "worst_outage_loss": float(metadata.get("worst_outage_loss", np.nan)),
        "research_connectivity_cost": float(metadata.get("connectivity_cost", metadata.get("risk_cost", np.nan))),
    }


def run_research_episode(
    planner_name,
    scenario,
    seed=0,
    settings=ResearchBenchmarkSettings(),
):
    """Run one matched closed-loop episode and return summary plus step trace."""
    if planner_name not in RESEARCH_PLANNERS:
        raise ValueError(f"unknown research planner: {planner_name}")
    rng = np.random.default_rng(int(seed))
    params = VehicleParams(dt=settings.dt)
    ego = np.asarray(scenario.ego_state, dtype=float).copy()
    target = np.asarray(scenario.target_states, dtype=float)
    steps = max(0, len(target) - 1)
    planning_link, realized_link = _make_link_models(settings, steps)
    planner = _make_planner(planner_name, settings, params, planning_link, int(seed))

    observations = []
    snr = []
    outage = []
    ber = []
    goodput = []
    target_distance = []
    realized_ttc = []
    obstacle_clearance = []
    prediction_ade = []
    prediction_fde = []
    planning_times = []
    applied_weights = []
    chance_violations = []
    chance_unsatisfied_steps = 0
    path_length = 0.0
    no_candidate = 0
    collision = False
    collision_steps = 0
    first_collision_step = -1
    candidate_counts = {"generated": 0, "road": 0, "speed": 0, "static": 0, "dynamic": 0, "feasible": 0}
    zero_after_static = 0
    zero_after_dynamic = 0
    previous = ego[:2].copy()
    trace = []

    for k in range(steps):
        observations.append(target[k, :2] + rng.normal(0.0, settings.observation_sigma_m, 2))
        safety_pred, connectivity_pred = _planner_prediction(observations, settings, rng)
        if settings.stress_safety_prediction:
            safety_pred = connectivity_pred
        truth = _truth_horizon(target, k + 1, settings.horizon_steps)

        n_prediction = min(len(connectivity_pred), len(truth))
        error = np.linalg.norm(connectivity_pred[:n_prediction, :2] - truth[:n_prediction, :2], axis=1)
        prediction_ade.append(float(np.mean(error)))
        prediction_fde.append(float(error[-1]))

        planner_target = connectivity_pred
        if planner_name in {"P3", "P2-CVaR", "P2-Chance", "P2-Worst"}:
            planner_target = {
                "mean_xy": connectivity_pred[:, :2],
                "sigma_xy": np.full_like(
                    connectivity_pred[:, :2],
                    settings.prediction_sigma_m * settings.reported_uncertainty_scale,
                ),
            }
        elif planner_name == "P4":
            planner_target = truth

        _set_model_step(planning_link, k + 1)
        start = perf_counter()
        result = planner.plan(
            ego,
            planner_target,
            obstacles=scenario.obstacles,
            reference_speed=scenario.reference_speed,
            safety_target_prediction=safety_pred,
        )
        planning_time = perf_counter() - start
        planning_times.append(float(planning_time))

        feasibility = getattr(planner, "last_feasibility_counts", None)
        if feasibility is None:
            feasibility = _candidate_feasibility_counts(
                ego,
                scenario.obstacles,
                safety_pred,
                params,
                settings.collision_distance_m,
            )
        for key, value in feasibility.items():
            candidate_counts[key] += int(value)
        if feasibility["generated"] - feasibility["road"] - feasibility["speed"] - feasibility["static"] == 0:
            zero_after_static += 1
        if feasibility["feasible"] == 0:
            zero_after_dynamic += 1
        if result.candidate is None:
            no_candidate += 1

        metadata = _extract_planner_metadata(result)
        if np.isfinite(metadata["applied_connectivity_weight"]):
            applied_weights.append(metadata["applied_connectivity_weight"])
        if np.isfinite(metadata["chance_violation_probability"]):
            chance_violations.append(metadata["chance_violation_probability"])
            if metadata["constraint_satisfied"] is False:
                chance_unsatisfied_steps += 1

        ego = step(ego, _first_control(result), params)
        path_length += float(np.linalg.norm(ego[:2] - previous))
        previous = ego[:2].copy()
        truth_now = target[k + 1]

        _set_model_step(realized_link, k + 1)
        realized = realized_link.predict(
            np.repeat(ego[None, :], 2, axis=0),
            np.repeat(truth_now[None, :], 2, axis=0),
        )
        snr_now = float(realized.snr_db[0])
        outage_now = float(realized.outage_probability[0])
        ber_now = float(realized.ber[0])
        goodput_now = float(realized.goodput[0])
        snr.append(snr_now)
        outage.append(outage_now)
        ber.append(ber_now)
        goodput.append(goodput_now)

        distance = float(np.linalg.norm(ego[:2] - truth_now[:2]))
        target_distance.append(distance)
        is_collision = distance < settings.collision_distance_m
        collision = collision or is_collision
        realized_ttc.append(_realized_ttc(ego, truth_now, settings.collision_distance_m))
        if is_collision:
            collision_steps += 1
            if first_collision_step < 0:
                first_collision_step = k + 1
        if len(scenario.obstacles):
            obs_xy = np.asarray([o[:2] for o in scenario.obstacles], dtype=float)
            obstacle_clearance.append(float(np.min(np.linalg.norm(obs_xy - ego[:2], axis=1))))

        trace.append({
            "scenario": scenario.name,
            "planner": planner_name,
            "seed": int(seed),
            "step": k + 1,
            "time_s": float((k + 1) * settings.dt),
            "ego_x_m": float(ego[0]),
            "ego_y_m": float(ego[1]),
            "ego_yaw_rad": float(ego[2]),
            "ego_speed_mps": float(ego[3]),
            "target_x_m": float(truth_now[0]),
            "target_y_m": float(truth_now[1]),
            "realized_snr_db": snr_now,
            "realized_outage_probability": outage_now,
            "planner_score": float(result.score),
            "planning_time_s": float(planning_time),
            "no_candidate": int(result.candidate is None),
            **metadata,
        })

    planning_array = np.asarray(planning_times, dtype=float)
    summary = {
        "protocol_version": settings.protocol_version,
        "scenario": scenario.name,
        "planner": planner_name,
        "seed": int(seed),
        "steps": steps,
        "duration_s": steps * settings.dt,
        "mean_snr_db": float(np.mean(snr)),
        "mean_outage_probability": float(np.mean(outage)),
        "mean_ber_model": float(np.mean(ber)),
        "mean_goodput_bps_model": float(np.mean(goodput)),
        "path_length_m": float(path_length),
        "progress_m": float(ego[0] - scenario.ego_state[0]),
        "min_target_distance_m": float(np.min(target_distance)),
        "min_realized_ttc_s": float(np.min(realized_ttc)),
        "min_static_obstacle_clearance_m": float(np.min(obstacle_clearance)) if obstacle_clearance else np.inf,
        "collision_indicator": int(collision),
        "collision_steps": int(collision_steps),
        "first_collision_step": int(first_collision_step),
        "first_collision_time_s": float(first_collision_step * settings.dt) if first_collision_step >= 0 else np.inf,
        "no_candidate_steps": int(no_candidate),
        "zero_candidate_after_static_steps": int(zero_after_static),
        "zero_candidate_after_dynamic_steps": int(zero_after_dynamic),
        "candidate_evaluations": int(candidate_counts["generated"]),
        "candidate_road_rejections": int(candidate_counts["road"]),
        "candidate_speed_rejections": int(candidate_counts["speed"]),
        "candidate_static_rejections": int(candidate_counts["static"]),
        "candidate_dynamic_rejections": int(candidate_counts["dynamic"]),
        "candidate_feasible": int(candidate_counts["feasible"]),
        "prediction_ade_m": float(np.mean(prediction_ade)),
        "prediction_fde_m": float(np.mean(prediction_fde)),
        "mean_planning_time_s": float(np.mean(planning_array)),
        "p95_planning_time_s": float(np.quantile(planning_array, 0.95)),
        "max_planning_time_s": float(np.max(planning_array)),
        "mean_applied_connectivity_weight": float(np.mean(applied_weights)) if applied_weights else np.nan,
        "mean_chance_violation_probability": float(np.mean(chance_violations)) if chance_violations else np.nan,
        "chance_unsatisfied_steps": int(chance_unsatisfied_steps),
        "horizon_s": float(settings.horizon_steps * settings.dt),
        "connectivity_weight": float(settings.connectivity_weight),
        "mc_samples": int(settings.mc_samples),
        "cvar_alpha": float(settings.cvar_alpha),
        "cvar_weight": float(settings.cvar_weight),
        "chance_max_violation_probability": float(settings.chance_max_violation_probability),
        "prediction_noise_scale": float(settings.prediction_noise_scale),
        "reported_uncertainty_scale": float(settings.reported_uncertainty_scale),
        "observation_delay_steps": int(settings.observation_delay_steps),
        "reference_snr_bias_db": float(settings.reference_snr_bias_db),
        "pathloss_scale": float(settings.pathloss_scale),
        "beam_sigma_scale": float(settings.beam_sigma_scale),
        "blackout_kind": settings.blackout_kind,
        "blackout_visible_to_planner": bool(settings.blackout_visible_to_planner),
        "measured_optical_link": False,
    }
    return summary, trace


def run_research_benchmark(
    seeds=range(10),
    settings=ResearchBenchmarkSettings(),
    scenarios=None,
    planners=RESEARCH_PLANNERS,
):
    """Run a matched planner/scenario/seed matrix and return episodes and traces."""
    if scenarios is None:
        scenarios = make_primary_scenarios()
    planners = tuple(planners)
    unknown = set(planners) - set(RESEARCH_PLANNERS)
    if unknown:
        raise ValueError(f"unknown research planners: {sorted(unknown)}")
    episodes = []
    traces = []
    for scenario in scenarios:
        for seed in seeds:
            for planner in planners:
                summary, trace = run_research_episode(planner, scenario, int(seed), settings)
                episodes.append(summary)
                traces.extend(trace)
    return episodes, traces
