"""Communication-independent one-step emergency control for V5."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .dynamics import VehicleParams, step
from .trajectory import CandidateTrajectory
from .feasibility import check_road_bounds, check_speed, check_obstacles, check_dynamic_target

@dataclass(frozen=True)
class EmergencyDiagnostics:
    generated: int
    physical_rejections: int
    road_rejections: int
    speed_rejections: int
    static_rejections: int
    dynamic_rejections: int
    feasible: int


def generate_one_step_emergency_controls(params: VehicleParams):
    """Deterministic shared family; contains no communication information."""
    accelerations=(params.min_accel, 0.5*params.min_accel, 0.0)
    steerings=(-params.max_steering, -0.5*params.max_steering, 0.0, 0.5*params.max_steering, params.max_steering)
    return [np.array([a,s],float) for a in accelerations for s in steerings]


def _physically_admissible(state, control, params):
    a,s=np.asarray(control,float)
    if a < params.min_accel-1e-12 or a > params.max_accel+1e-12:return False
    if abs(s) > params.max_steering+1e-12:return False
    v=float(np.asarray(state,float)[3])
    lateral_acc=abs(v*v*np.tan(s)/params.wheelbase)
    return lateral_acc <= params.max_lateral_accel+1e-12


def select_one_step_emergency(ego_state, obstacles, target_next_xy, params, target_clearance=2.0,
                              lane_half_width=1.75, static_clearance=1.5):
    """Return a safe action for the actually executed interval, or None honestly."""
    controls=generate_one_step_emergency_controls(params)
    counts=dict(generated=len(controls),physical_rejections=0,road_rejections=0,speed_rejections=0,
                static_rejections=0,dynamic_rejections=0,feasible=0)
    safe=[]
    obstacles=np.empty((0,3)) if obstacles is None else np.asarray(obstacles,float)
    target=None if target_next_xy is None else np.asarray(target_next_xy,float).reshape(1,-1)[:,:2]
    for control in controls:
        if not _physically_admissible(ego_state,control,params):counts['physical_rejections']+=1;continue
        nxt=step(np.asarray(ego_state,float),control,params);executed=nxt.reshape(1,4)
        if not check_road_bounds(executed,lane_half_width):counts['road_rejections']+=1;continue
        if not check_speed(executed):counts['speed_rejections']+=1;continue
        if not check_obstacles(executed,obstacles,static_clearance):counts['static_rejections']+=1;continue
        if target is not None and not check_dynamic_target(executed,target,target_clearance):counts['dynamic_rejections']+=1;continue
        counts['feasible']+=1;safe.append((control,nxt))
    diag=EmergencyDiagnostics(**counts)
    if not safe:return None,diag
    # Communication-independent deterministic policy: strongest braking, then smallest |steering|, then steering value.
    control,nxt=min(safe,key=lambda item:(item[0][0],abs(item[0][1]),item[0][1]))
    candidate=CandidateTrajectory(states=np.vstack([np.asarray(ego_state,float),nxt]),controls=control.reshape(1,2),
                                  horizon=params.dt,lateral_offset=0.0,target_speed=float(nxt[3]))
    return candidate,diag
