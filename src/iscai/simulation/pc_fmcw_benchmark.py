"""Dataset-free closed-loop benchmark for the PC-FMCW robotics extension.

Target motion is simulated. P0-P3 never receive future target truth; P2 and P3
share the same constant-velocity mean prediction. P4 receives future simulator
truth only for connectivity forecasting, while all planners use the same mean
target prediction for dynamic safety filtering. Realized connectivity is then
evaluated with the same PC-FMCW-informed link model for every planner.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor
from iscai.planning.dynamics import VehicleParams, step
from iscai.planning.planners import MobilityOnlyPlanner, ReactiveConnectivityPlanner, PredictiveConnectivityPlanner, OracleConnectivityPlanner
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner
from iscai.prediction.trajectory_predictor import constant_velocity
from iscai.simulation.scenario import make_primary_scenarios

PLANNERS=("P0","P1","P2","P3","P4")

@dataclass(frozen=True)
class BenchmarkSettings:
    dt: float=0.1
    history_steps: int=8
    horizon_steps: int=20
    observation_sigma_m: float=0.20
    prediction_sigma_m: float=0.75
    connectivity_weight: float=1.0
    p3_mc_samples: int=32
    collision_distance_m: float=2.0

    def __post_init__(self):
        if not np.isfinite(self.dt) or self.dt <= 0.0: raise ValueError("dt must be positive and finite")
        if self.history_steps < 2: raise ValueError("history_steps must be >= 2")
        if self.horizon_steps < 1: raise ValueError("horizon_steps must be >= 1")
        if not np.isfinite(self.observation_sigma_m) or self.observation_sigma_m < 0.0: raise ValueError("observation_sigma_m must be non-negative and finite")
        if not np.isfinite(self.prediction_sigma_m) or self.prediction_sigma_m < 0.0: raise ValueError("prediction_sigma_m must be non-negative and finite")
        if not np.isfinite(self.connectivity_weight) or self.connectivity_weight < 0.0: raise ValueError("connectivity_weight must be non-negative and finite")
        if self.p3_mc_samples < 1: raise ValueError("p3_mc_samples must be >= 1")
        if not np.isfinite(self.collision_distance_m) or self.collision_distance_m < 0.0: raise ValueError("collision_distance_m must be non-negative and finite")


def _prediction(history,horizon,dt):
    history=np.asarray(history,float)
    if history.ndim != 2 or history.shape[1] != 2 or len(history) < 1: raise ValueError("history must have shape (N, 2) with N >= 1")
    mean=np.repeat(history[-1:, :], horizon, axis=0) if len(history)==1 else constant_velocity(history,horizon,dt)
    target=np.zeros((horizon,4),float);target[:,:2]=mean
    if horizon>1:
        velocity=np.gradient(mean,dt,axis=0);target[:,3]=np.linalg.norm(velocity,axis=1)
    return target


def _truth_horizon(target,k,horizon):
    part=np.asarray(target[k:k+horizon],float)
    if len(part)==0:return np.empty((0,4),float)
    if len(part)<horizon:part=np.vstack([part,np.repeat(part[-1:],horizon-len(part),axis=0)])
    return part


def _first_control(result):
    if result.candidate is None or len(result.candidate.controls)==0:return np.zeros(2)
    return np.asarray(result.candidate.controls[0],float)


def _velocity_xy(state):
    state=np.asarray(state,float);return state[3]*np.array([np.cos(state[2]),np.sin(state[2])])


def _realized_ttc(ego,target_state,collision_distance_m=2.0):
    clearance=float(collision_distance_m)
    if clearance<0.0:raise ValueError("collision_distance_m must be non-negative")
    rel_pos=np.asarray(target_state[:2],float)-np.asarray(ego[:2],float);distance=float(np.linalg.norm(rel_pos))
    if distance<=clearance:return 0.0
    rel_vel=_velocity_xy(target_state)-_velocity_xy(ego);a=float(np.dot(rel_vel,rel_vel))
    if a<=1e-12:return np.inf
    b=2.0*float(np.dot(rel_pos,rel_vel));c=float(np.dot(rel_pos,rel_pos)-clearance**2);disc=b*b-4.0*a*c
    if disc<0.0:return np.inf
    root=np.sqrt(max(0.0,disc));candidates=[t for t in ((-b-root)/(2.0*a),(-b+root)/(2.0*a)) if t>=0.0]
    return min(candidates) if candidates else np.inf


def _simulate_episode(scenario,planner_name,seed,settings,link_predictor):
    rng=np.random.default_rng(seed);params=VehicleParams(dt=settings.dt);ego=np.asarray(scenario.ego_state,float).copy();target=np.asarray(scenario.target_states,float)
    planner_common=dict(vehicle_params=params,target_clearance=settings.collision_distance_m)
    planners={"P0":MobilityOnlyPlanner(link_predictor,connectivity_weight=0.0,**planner_common),"P1":ReactiveConnectivityPlanner(link_predictor,connectivity_weight=settings.connectivity_weight,**planner_common),"P2":PredictiveConnectivityPlanner(link_predictor,connectivity_weight=settings.connectivity_weight,**planner_common),"P3":RiskAwarePredictivePlanner(link_predictor,connectivity_weight=settings.connectivity_weight,mc_samples=settings.p3_mc_samples,**planner_common),"P4":OracleConnectivityPlanner(link_predictor,connectivity_weight=settings.connectivity_weight,**planner_common)}
    observations=[];snr=[];outage=[];ber=[];goodput=[];target_distance=[];realized_ttc=[];obstacle_clearance=[];path_length=0.0;no_candidate=0;collision=False;previous=ego[:2].copy();steps=max(0,len(target)-1)
    for k in range(steps):
        observations.append(target[k,:2]+rng.normal(0.0,settings.observation_sigma_m,2));hist=observations[-settings.history_steps:];pred=_prediction(hist,settings.horizon_steps,settings.dt);truth=_truth_horizon(target,k+1,settings.horizon_steps);planner_target=pred
        if planner_name=="P3":planner_target={"mean_xy":pred[:,:2],"sigma_xy":np.full_like(pred[:,:2],settings.prediction_sigma_m)}
        elif planner_name=="P4":planner_target=truth
        result=planners[planner_name].plan(ego,planner_target,obstacles=scenario.obstacles,reference_speed=scenario.reference_speed,safety_target_prediction=pred)
        if result.candidate is None:no_candidate+=1
        ego=step(ego,_first_control(result),params);path_length+=float(np.linalg.norm(ego[:2]-previous));previous=ego[:2].copy();truth_now=target[k+1]
        forecast=link_predictor.predict(np.repeat(ego[None,:],2,axis=0),np.repeat(truth_now[None,:],2,axis=0));snr.append(float(forecast.snr_db[0]));outage.append(float(forecast.outage_probability[0]));ber.append(float(forecast.ber[0]));goodput.append(float(forecast.goodput[0]));d=float(np.linalg.norm(ego[:2]-truth_now[:2]));target_distance.append(d);collision=collision or d<settings.collision_distance_m;realized_ttc.append(_realized_ttc(ego,truth_now,settings.collision_distance_m))
        if len(scenario.obstacles):
            obs_xy=np.asarray([o[:2] for o in scenario.obstacles],float);obstacle_clearance.append(float(np.min(np.linalg.norm(obs_xy-ego[:2],axis=1))))
    return {"scenario":scenario.name,"planner":planner_name,"seed":seed,"steps":steps,"duration_s":steps*settings.dt,"mean_snr_db":float(np.mean(snr)),"mean_outage_probability":float(np.mean(outage)),"mean_ber_model":float(np.mean(ber)),"mean_goodput_bps_model":float(np.mean(goodput)),"path_length_m":path_length,"progress_m":float(ego[0]-scenario.ego_state[0]),"min_target_distance_m":float(np.min(target_distance)),"min_realized_ttc_s":float(np.min(realized_ttc)),"min_static_obstacle_clearance_m":float(np.min(obstacle_clearance)) if obstacle_clearance else np.inf,"collision_indicator":int(collision),"no_candidate_steps":no_candidate,"measured_optical_link":False}


def run_simulated_episode(planner_name,scenario,seed=0,settings=BenchmarkSettings(),link=None,link_predictor=None):
    """Run one reproducible simulated episode; ``link`` is the stable public injection hook."""
    if planner_name not in PLANNERS:raise ValueError(f"unknown planner: {planner_name}")
    if link is not None and link_predictor is not None:raise ValueError("provide only one of link or link_predictor")
    predictor=link if link is not None else link_predictor
    if predictor is None:predictor=PCFMCWPlanningLinkPredictor()
    return _simulate_episode(scenario,planner_name,int(seed),settings,predictor)


def run_benchmark(seeds=range(10),settings=BenchmarkSettings(),scenarios=None,link_predictor=None):
    if scenarios is None:scenarios=make_primary_scenarios()
    if link_predictor is None:link_predictor=PCFMCWPlanningLinkPredictor()
    rows=[]
    for scenario in scenarios:
        for seed in seeds:
            for planner in PLANNERS:rows.append(run_simulated_episode(planner,scenario,int(seed),settings,link_predictor=link_predictor))
    return rows
