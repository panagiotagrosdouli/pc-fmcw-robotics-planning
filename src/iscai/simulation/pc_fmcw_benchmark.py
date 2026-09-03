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


def _prediction(history,horizon,dt):
    mean=constant_velocity(np.asarray(history,float),horizon,dt)
    target=np.zeros((horizon,4),float); target[:,:2]=mean
    if horizon>1:
        velocity=np.gradient(mean,dt,axis=0); target[:,3]=np.linalg.norm(velocity,axis=1)
    return target


def _truth_horizon(target,k,horizon):
    part=np.asarray(target[k:k+horizon],float)
    if len(part)==0: return np.empty((0,4),float)
    if len(part)<horizon: part=np.vstack([part,np.repeat(part[-1:],horizon-len(part),axis=0)])
    return part


def _first_control(result):
    if result.candidate is None or len(result.candidate.controls)==0:return np.zeros(2)
    return np.asarray(result.candidate.controls[0],float)


def _velocity_xy(state):
    """Convert [x,y,yaw,speed] into Cartesian planar velocity."""
    state=np.asarray(state,float)
    return state[3]*np.array([np.cos(state[2]),np.sin(state[2])])


def _realized_ttc(ego,target_state):
    """Constant-relative-velocity TTC for the realized ego/target states.

    TTC is the time to closest approach when the relative motion is closing.
    Infinite TTC denotes non-closing or degenerate relative motion. This is a
    diagnostic safety metric, not an oracle signal exposed to any planner.
    """
    rel_pos=np.asarray(target_state[:2],float)-np.asarray(ego[:2],float)
    rel_vel=_velocity_xy(target_state)-_velocity_xy(ego)
    speed2=float(np.dot(rel_vel,rel_vel))
    if speed2<=1e-12:return np.inf
    t_closest=-float(np.dot(rel_pos,rel_vel))/speed2
    return t_closest if t_closest>0.0 else np.inf


def run_simulated_episode(planner_name,scenario,*,seed=0,settings=None,link=None):
    """Run one seeded receding-horizon simulation episode."""
    if planner_name not in PLANNERS: raise ValueError(f"unknown planner {planner_name}")
    settings=settings or BenchmarkSettings(); link=link or PCFMCWPlanningLinkPredictor()
    params=VehicleParams(dt=settings.dt); rng=np.random.default_rng(seed)
    target=np.asarray(scenario.target_states,float); ego=np.asarray(scenario.ego_state,float).copy()
    planners={
      "P0":MobilityOnlyPlanner(link,vehicle_params=params),
      "P1":ReactiveConnectivityPlanner(link,settings.connectivity_weight,params),
      "P2":PredictiveConnectivityPlanner(link,settings.connectivity_weight,params),
      "P3":RiskAwarePredictivePlanner(link,settings.connectivity_weight,params,mc_samples=settings.p3_mc_samples,threshold_db=link.geometry.outage_threshold_db,random_seed=seed),
      "P4":OracleConnectivityPlanner(link,settings.connectivity_weight,params),
    }
    history=[]; positions=[ego[:2].copy()]; outages=[]; snrs=[]; bers=[]; goodputs=[]; target_dist=[]; realized_ttc=[]; obstacle_clear=[]; no_candidate=0
    for k in range(len(target)-1):
        observed=target[k,:2]+rng.normal(0.0,settings.observation_sigma_m,2); history.append(observed)
        hist=history[-settings.history_steps:]
        if len(hist)<2:
            mean=np.repeat(observed[None,:],settings.horizon_steps,axis=0)
        else: mean=_prediction(hist,settings.horizon_steps,settings.dt)[:,:2]
        pred=np.zeros((settings.horizon_steps,4),float); pred[:,:2]=mean
        truth=_truth_horizon(target,k,settings.horizon_steps)
        if planner_name=="P3":
            planner_target={"mean_xy":mean,"sigma_xy":np.full_like(mean,settings.prediction_sigma_m)}
        elif planner_name=="P4":
            planner_target=truth
        else:
            planner_target=pred
        plan_kwargs=dict(obstacles=scenario.obstacles,reference_speed=scenario.reference_speed)
        if planner_name=="P4":
            plan_kwargs["safety_target_prediction"]=pred
        result=planners[planner_name].plan(ego,planner_target,**plan_kwargs)
        if result.candidate is None:no_candidate+=1
        ego=step(ego,_first_control(result),params); positions.append(ego[:2].copy())
        realized=link.predict(ego[None,:],target[k+1:k+2])
        outages.append(float(realized.outage_probability[0])); snrs.append(float(realized.snr_db[0])); bers.append(float(realized.ber[0])); goodputs.append(float(realized.goodput[0]))
        target_dist.append(float(np.linalg.norm(ego[:2]-target[k+1,:2])))
        realized_ttc.append(float(_realized_ttc(ego,target[k+1])))
        for obs in scenario.obstacles:
            ox,oy,*r=obs; obstacle_clear.append(float(np.hypot(ego[0]-ox,ego[1]-oy)-(r[0] if r else 0.0)))
    pos=np.asarray(positions); min_target=min(target_dist) if target_dist else np.inf; min_obs=min(obstacle_clear) if obstacle_clear else np.inf
    finite_ttc=[value for value in realized_ttc if np.isfinite(value)]
    min_ttc=min(finite_ttc) if finite_ttc else np.inf
    return {"planner":planner_name,"scenario":scenario.name,"seed":int(seed),"duration_s":float((len(target)-1)*settings.dt),"path_length_m":float(np.linalg.norm(np.diff(pos,axis=0),axis=1).sum()),"progress_m":float(pos[-1,0]-pos[0,0]),"mean_outage_probability":float(np.mean(outages)),"mean_snr_db":float(np.mean(snrs)),"mean_ber_model":float(np.mean(bers)),"mean_goodput_bps_model":float(np.mean(goodputs)),"min_target_distance_m":float(min_target),"min_realized_ttc_s":float(min_ttc),"min_static_obstacle_clearance_m":float(min_obs),"collision_indicator":int(min_target<settings.collision_distance_m or min_obs<0.0),"no_candidate_steps":int(no_candidate),"connectivity_model":"PC-FMCW-informed simulation model","measured_optical_link":False}


def run_benchmark(*,seeds=(0,),settings=None):
    rows=[]
    for seed in seeds:
        for scenario in make_primary_scenarios():
            for planner in PLANNERS: rows.append(run_simulated_episode(planner,scenario,seed=int(seed),settings=settings))
    return rows
