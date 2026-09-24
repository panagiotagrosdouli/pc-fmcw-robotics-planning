"""Closed-loop benchmark for decision-triggered active self-calibration.

Simulator latent parameters are used only to generate realized communication
observations and to compute post-decision oracle-reference metrics. C0--C3 never
receive latent truth. All C0--C4 variants share candidate generation and hard
safety filtering.
"""
from __future__ import annotations

from dataclasses import dataclass
import zlib

import numpy as np

from iscai.planning.dynamics import VehicleParams, step
from iscai.simulation.pc_fmcw_benchmark import _prediction, _realized_ttc

from .belief import GridBelief, normalized_parameter_error
from .link_model import ParameterizedPCFMCWLinkModel
from .planners import CALIBRATION_PLANNERS, ActiveSelfCalibrationPlanner, true_candidate_objective
from .scenarios import CalibrationScenario, make_identifiability_scenarios


@dataclass(frozen=True)
class CalibrationBenchmarkSettings:
    dt: float = 0.1
    history_steps: int = 8
    horizon_steps: int = 16
    target_observation_sigma_m: float = 0.20
    communication_observation_sigma_db: float = 1.0
    connectivity_weight: float = 1.0
    information_weight: float = 0.45
    probe_weight: float = 0.20
    decision_threshold: float = 0.25
    min_expected_regret: float = 0.0
    information_horizon_steps: int = 4
    collision_distance_m: float = 2.0
    planning_safety_margin_m: float = 0.5
    candidate_lateral_offsets: tuple = (-1.0, 0.0, 1.0)
    candidate_horizons: tuple = (2.0, 3.0)
    candidate_speed_offsets: tuple = (-1.5, 0.0, 1.5)
    require_static_stop_viability: bool = True
    bounded_brake_steer: bool = True
    time_aligned_dynamic: bool = True
    require_dynamic_stop_viability: bool = True
    hierarchical_clearance: bool = True
    damped_lateral_prediction: bool = True
    endpoint_anchored_lateral: bool = True

    def __post_init__(self):
        if not np.isfinite(self.dt) or self.dt <= 0.0:
            raise ValueError("dt must be positive and finite")
        if self.history_steps < 2 or self.horizon_steps < 1:
            raise ValueError("history_steps >=2 and horizon_steps >=1 are required")
        for name in (
            "target_observation_sigma_m","communication_observation_sigma_db",
            "connectivity_weight","information_weight","probe_weight",
            "decision_threshold","min_expected_regret","collision_distance_m",
            "planning_safety_margin_m",
        ):
            value=float(getattr(self,name))
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.communication_observation_sigma_db <= 0.0:
            raise ValueError("communication_observation_sigma_db must be positive")
        if self.information_horizon_steps < 1:
            raise ValueError("information_horizon_steps must be >= 1")


def _episode_rng(seed: int, scenario_name: str):
    scenario_code=zlib.crc32(scenario_name.encode("utf-8")) & 0xFFFFFFFF
    return np.random.default_rng(np.random.SeedSequence([int(seed),int(scenario_code)]))


def _make_belief(scenario: CalibrationScenario, settings: CalibrationBenchmarkSettings):
    return GridBelief.from_axes(
        **scenario.prior_axes,
        observation_sigma_db=settings.communication_observation_sigma_db,
    )


def _make_planner(mode, scenario, settings, model, params):
    belief=_make_belief(scenario,settings) if mode in {"C1","C2","C3"} else None
    oracle=scenario.true_parameters if mode=="C4" else None
    return ActiveSelfCalibrationPlanner(
        mode,model,belief=belief,oracle_parameters=oracle,
        connectivity_weight=settings.connectivity_weight,
        information_weight=settings.information_weight,
        probe_weight=settings.probe_weight,
        decision_threshold=settings.decision_threshold,
        min_expected_regret=settings.min_expected_regret,
        information_horizon_steps=settings.information_horizon_steps,
        vehicle_params=params,
        target_clearance=settings.collision_distance_m+settings.planning_safety_margin_m,
        physical_target_clearance=(settings.collision_distance_m if settings.hierarchical_clearance else None),
        require_static_stop_viability=settings.require_static_stop_viability,
        bounded_brake_steer=settings.bounded_brake_steer,
        time_aligned_dynamic=settings.time_aligned_dynamic,
        require_dynamic_stop_viability=settings.require_dynamic_stop_viability,
        lateral_offsets=settings.candidate_lateral_offsets,
        horizons=settings.candidate_horizons,
        speed_offsets=settings.candidate_speed_offsets,
    )


def _first_control(result, params):
    if result.candidate is None or len(result.candidate.controls)==0:
        return np.array([params.min_accel,0.0],dtype=float)
    return np.asarray(result.candidate.controls[0],dtype=float)


def _consistent_match_step(agreements):
    values=[bool(x) for x in agreements]
    for i in range(len(values)):
        if all(values[i:]):
            return i+1
    return -1


def _simulate_episode(calibration_scenario, planner_name, seed, settings, model):
    if planner_name not in CALIBRATION_PLANNERS:
        raise ValueError(f"unknown planner: {planner_name}")
    base=calibration_scenario.scenario
    target=np.asarray(base.target_states,dtype=float)
    ego=np.asarray(base.ego_state,dtype=float).copy()
    params=VehicleParams(dt=settings.dt)
    planner=_make_planner(planner_name,calibration_scenario,settings,model,params)

    rng=_episode_rng(seed,calibration_scenario.name)
    target_noise=rng.normal(0.0,settings.target_observation_sigma_m,size=(len(target),2))
    comm_noise=rng.normal(0.0,settings.communication_observation_sigma_db,size=len(target))
    observed_target=target[:,:2]+target_noise

    history=[];step_rows=[];path_length=0.0;previous=ego[:2].copy()
    collision=False;no_candidate_steps=0;min_target_distance=np.inf
    min_realized_ttc=np.inf;min_static_clearance=np.inf;static_violation_steps=0
    margin_relaxation_steps=0;probe_count=0;information_active_count=0
    unnecessary_probe_count=0;cumulative_probe_cost=0.0;cumulative_information_gain=0.0
    cumulative_decision_regret=0.0;oracle_agreements=[];parameter_errors=[]
    snrs=[];outages=[];bers=[];goodputs=[]
    initial_entropy=planner.belief.entropy if planner.belief is not None else np.nan

    steps=max(0,len(target)-1)
    for k in range(steps):
        history.append(observed_target[k])
        hist=np.asarray(history[-settings.history_steps:],dtype=float)
        pred=_prediction(
            hist,settings.horizon_steps,settings.dt,
            settings.damped_lateral_prediction,settings.endpoint_anchored_lateral,
        )

        # No future target truth or latent link truth is passed to C0-C3 planning.
        result=planner.plan(
            ego,pred,obstacles=base.obstacles,reference_speed=base.reference_speed,
            safety_target_prediction=pred,
        )
        if planner.last_margin_relaxed: margin_relaxation_steps+=1
        if result.candidate is None: no_candidate_steps+=1

        # True-parameter regret is evaluation-only and is computed after selection.
        oracle_regret=np.nan;oracle_agreement=False;oracle_index=-1
        if result.candidate is not None and result.candidate_pool:
            oracle_costs=np.array([
                true_candidate_objective(
                    model,candidate,pred,calibration_scenario.true_parameters,
                    base.reference_speed,settings.connectivity_weight,
                ) for candidate in result.candidate_pool
            ],dtype=float)
            oracle_index=int(np.argmin(oracle_costs))
            oracle_regret=float(oracle_costs[result.candidate_index]-oracle_costs[oracle_index])
            cumulative_decision_regret+=max(0.0,oracle_regret)
            oracle_agreement=result.candidate_index==oracle_index
        oracle_agreements.append(oracle_agreement)

        information_active_count+=int(result.information_active)
        probe_count+=int(result.probe_selected)
        cumulative_probe_cost+=float(result.probe_cost)
        cumulative_information_gain+=float(result.information_gain)
        unnecessary=bool(
            result.probe_selected and (
                result.decision_uncertainty<=settings.decision_threshold
                or result.expected_decision_regret<=settings.min_expected_regret
            )
        )
        unnecessary_probe_count+=int(unnecessary)

        control=_first_control(result,params)
        ego=step(ego,control,params)
        path_length+=float(np.linalg.norm(ego[:2]-previous));previous=ego[:2].copy()

        truth_now=target[k+1]
        realized=model.predict(
            ego.reshape(1,-1),truth_now.reshape(1,-1),calibration_scenario.true_parameters
        )
        true_snr=float(realized.snr_db[0])
        observed_snr=true_snr+float(comm_noise[k+1])
        snrs.append(true_snr);outages.append(float(realized.outage_probability[0]))
        bers.append(float(realized.ber[0]));goodputs.append(float(realized.goodput[0]))

        # Causal update after action execution, using only just-realized measurement.
        planner.observe(ego,observed_target[k+1],observed_snr)
        estimate=planner.current_parameter_estimate()
        error=normalized_parameter_error(estimate,calibration_scenario.true_parameters)
        parameter_errors.append(error)
        entropy=planner.belief.entropy if planner.belief is not None else np.nan

        distance=float(np.linalg.norm(ego[:2]-truth_now[:2]))
        min_target_distance=min(min_target_distance,distance)
        collision=collision or distance<settings.collision_distance_m
        min_realized_ttc=min(
            min_realized_ttc,float(_realized_ttc(ego,truth_now,settings.collision_distance_m))
        )
        if len(base.obstacles):
            obs=np.asarray(base.obstacles,dtype=float)
            radii=obs[:,2] if obs.shape[1]>=3 else np.zeros(len(obs))
            static_clearance=float(np.min(np.linalg.norm(obs[:,:2]-ego[:2],axis=1)-radii))
            min_static_clearance=min(min_static_clearance,static_clearance)
            static_violation_steps+=int(static_clearance<1.5)

        step_rows.append({
            "scenario":calibration_scenario.name,"planner":planner_name,"seed":int(seed),"step":k+1,
            "decision_uncertainty":float(result.decision_uncertainty),
            "expected_decision_regret":float(result.expected_decision_regret),
            "information_active":int(result.information_active),
            "probe_selected":int(result.probe_selected),"unnecessary_probe":int(unnecessary),
            "selected_information_gain":float(result.information_gain),
            "selected_probe_cost":float(result.probe_cost),
            "oracle_parameter_regret":oracle_regret,
            "oracle_parameter_agreement":int(oracle_agreement),
            "parameter_error_normalized":float(error),
            "belief_entropy":float(entropy) if np.isfinite(entropy) else np.nan,
            "true_snr_db":true_snr,"observed_snr_db":float(observed_snr),
        })

    estimate=planner.current_parameter_estimate();truth=calibration_scenario.true_parameters
    final_error=normalized_parameter_error(estimate,truth)
    convergence_slope=np.nan
    if len(parameter_errors)>=2:
        convergence_slope=float(np.polyfit(np.arange(len(parameter_errors))*settings.dt,parameter_errors,1)[0])
    consistent_step=_consistent_match_step(oracle_agreements)
    final_entropy=planner.belief.entropy if planner.belief is not None else np.nan
    entropy_reduction=(
        float(initial_entropy-final_entropy)
        if np.isfinite(initial_entropy) and np.isfinite(final_entropy) else np.nan
    )

    episode={
        "scenario":calibration_scenario.name,"mechanism":calibration_scenario.mechanism,
        "planner":planner_name,"seed":int(seed),"steps":steps,
        "duration_s":float(steps*settings.dt),"collision_indicator":int(collision),
        "no_candidate_steps":int(no_candidate_steps),
        "min_target_distance_m":float(min_target_distance),
        "min_realized_ttc_s":float(min_realized_ttc),
        "min_static_obstacle_clearance_m":float(min_static_clearance),
        "static_clearance_violation_steps":int(static_violation_steps),
        "margin_relaxation_steps":int(margin_relaxation_steps),
        "path_length_m":float(path_length),"progress_m":float(ego[0]-base.ego_state[0]),
        "mean_snr_db":float(np.mean(snrs)) if snrs else np.nan,
        "mean_outage_probability":float(np.mean(outages)) if outages else np.nan,
        "mean_ber_model":float(np.mean(bers)) if bers else np.nan,
        "mean_goodput_bps_model":float(np.mean(goodputs)) if goodputs else np.nan,
        "calibration_updates":int(planner.calibration_updates),
        "final_parameter_error_normalized":float(final_error),
        "final_alpha_loss_abs_error":float(abs(estimate.alpha_loss-truth.alpha_loss)),
        "final_delta_beam_abs_error_rad":float(abs(estimate.delta_beam_rad-truth.delta_beam_rad)),
        "final_k_angular_abs_error":float(abs(estimate.k_angular-truth.k_angular)),
        "initial_belief_entropy":float(initial_entropy) if np.isfinite(initial_entropy) else np.nan,
        "final_belief_entropy":float(final_entropy) if np.isfinite(final_entropy) else np.nan,
        "belief_entropy_reduction":entropy_reduction,
        "parameter_error_slope_per_s":convergence_slope,
        "information_active_steps":int(information_active_count),"probe_steps":int(probe_count),
        "probe_fraction":float(probe_count/steps) if steps else 0.0,
        "unnecessary_probe_steps":int(unnecessary_probe_count),
        "unnecessary_probe_rate":float(unnecessary_probe_count/probe_count) if probe_count else 0.0,
        "cumulative_probe_cost":float(cumulative_probe_cost),
        "mean_information_gain_per_probe":float(cumulative_information_gain/probe_count) if probe_count else 0.0,
        "cumulative_decision_regret":float(cumulative_decision_regret),
        "oracle_parameter_agreement_fraction":float(np.mean(oracle_agreements)) if oracle_agreements else np.nan,
        "consistent_oracle_match_step":int(consistent_step),
        "consistent_oracle_match_time_s":float(consistent_step*settings.dt) if consistent_step>0 else np.inf,
        "true_alpha_loss":float(truth.alpha_loss),"true_delta_beam_rad":float(truth.delta_beam_rad),
        "true_k_angular":float(truth.k_angular),"measured_optical_calibration":False,
    }
    return episode,step_rows


def run_study(
    seeds=range(1),*,settings: CalibrationBenchmarkSettings=CalibrationBenchmarkSettings(),
    scenarios=None,planners=CALIBRATION_PLANNERS,link_model=None,
):
    scenarios=make_identifiability_scenarios(dt=settings.dt) if scenarios is None else list(scenarios)
    model=link_model or ParameterizedPCFMCWLinkModel()
    episodes=[];steps=[]
    for scenario in scenarios:
        for seed in seeds:
            for planner in planners:
                episode,rows=_simulate_episode(scenario,planner,int(seed),settings,model)
                episodes.append(episode);steps.extend(rows)
    return {"episodes":episodes,"steps":steps}
