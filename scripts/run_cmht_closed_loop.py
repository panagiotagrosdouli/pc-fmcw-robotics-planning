"""Receding-horizon Stage-9 replay with measured CMHT target motion.

At every target frame: observe target history -> predict -> plan -> execute only
the first ego transition -> advance to the next measured target state -> replan.
This is a hybrid data-driven closed-loop simulation, not a real vehicle trial:
target motion is measured CMHT annotation data, ego motion is simulated, and
connectivity is modeled by the selected link predictor.
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_predictor import constant_velocity
from iscai.prediction.link_predictor import LinkPredictor
from iscai.connectivity.calibrated_predictor import CalibratedGeometryLinkPredictor
from iscai.planning.planners import MobilityOnlyPlanner, ReactiveConnectivityPlanner, PredictiveConnectivityPlanner, OracleConnectivityPlanner
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner

class _ExecutedStep:
    def __init__(self, states): self.states=np.asarray(states,float)

def states_from_xy(xy,dt):
    xy=np.asarray(xy,float); out=np.zeros((len(xy),4)); out[:,:2]=xy
    if len(xy)>1:
        v=np.gradient(xy,dt,axis=0); out[:,2]=np.arctan2(v[:,1],v[:,0]); out[:,3]=np.linalg.norm(v,axis=1)
    return out

def initial_ego(hist,dt,gap=12.):
    v=(hist[-1]-hist[-2])/dt; s=float(np.linalg.norm(v)); yaw=float(np.arctan2(v[1],v[0])) if s>1e-6 else 0.
    return np.array([hist[-1,0]-gap*np.cos(yaw),hist[-1,1]-gap*np.sin(yaw),yaw,max(s,1.)])

def tracks(rows):
    df=pd.DataFrame(rows,columns=['frame','x','y','z','object_id','class']).sort_values(['object_id','frame'])
    for oid,g in df.groupby('object_id',sort=False):
        g=g.sort_values('frame'); f=g.frame.to_numpy(int); xy=g[['x','y']].to_numpy(float)
        # Split gaps so prediction history never bridges missing annotation frames.
        cuts=np.r_[0,np.where(np.diff(f)!=1)[0]+1,len(f)]
        for a,b in zip(cuts[:-1],cuts[1:]):
            if b-a>=3: yield oid,f[a:b],xy[a:b]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--labels',type=Path,required=True); p.add_argument('--history',type=int,default=10)
    p.add_argument('--horizon',type=int,default=20); p.add_argument('--dt',type=float,default=.1); p.add_argument('--sigma-m',type=float,default=.75)
    p.add_argument('--max-tracks',type=int,default=100); p.add_argument('--link-calibration',type=Path); p.add_argument('--output',type=Path,default=Path('results/cmht_closed_loop.csv'))
    a=p.parse_args(); rows=extract_object_positions(a.labels)
    if a.link_calibration:
        link=CalibratedGeometryLinkPredictor.from_json(a.link_calibration); threshold=link.outage_threshold_db; link_name='frozen_calibrated'
    else:
        link=LinkPredictor(reference_snr_db=20.,reference_distance=10.,min_snr_db=8.); threshold=link.min_snr_db; link_name='geometry_surrogate'
    planner_builders={
      'P0':lambda:MobilityOnlyPlanner(link),'P1':lambda:ReactiveConnectivityPlanner(link),'P2':lambda:PredictiveConnectivityPlanner(link),
      'P3':lambda:RiskAwarePredictivePlanner(link,mc_samples=128,threshold_db=threshold,random_seed=0),'P4':lambda:OracleConnectivityPlanner(link)}
    rec=[]; used=0
    for oid,frames,xy in tracks(rows):
        if len(xy)<a.history+2: continue
        used+=1
        if used>a.max_tracks: break
        for name,build in planner_builders.items():
            planner=build(); ego=initial_ego(xy[:a.history],a.dt); path=[ego.copy()]; snrs=[]; runtimes=[]; distances=[]; feasible=True; decisions=0
            for t in range(a.history,len(xy)-1):
                available=min(a.horizon,len(xy)-t); hist=xy[max(0,t-a.history):t]
                pred_xy=constant_velocity(hist,available,a.dt); truth_xy=xy[t:t+available]
                pred=states_from_xy(pred_xy,a.dt); truth=states_from_xy(truth_xy,a.dt)
                target={'mean_xy':pred_xy,'sigma_xy':np.full_like(pred_xy,a.sigma_m)} if name=='P3' else (truth if name=='P4' else pred)
                tic=time.perf_counter(); result=planner.plan(ego,target,obstacles=[],reference_speed=ego[3]); runtimes.append(1e3*(time.perf_counter()-tic)); decisions+=1
                if result.candidate is None or len(result.candidate.states)<2: feasible=False; break
                # MPC/receding horizon: execute exactly the first predicted ego transition.
                next_ego=np.asarray(result.candidate.states[1],float); executed=_ExecutedStep(np.vstack([ego,next_ego]))
                target_exec=states_from_xy(xy[t:t+2],a.dt); realized=link.predict(executed,target_exec)
                snrs.append(float(np.asarray(realized.snr_db)[-1])); distances.append(float(np.linalg.norm(next_ego[:2]-xy[t+1]))); ego=next_ego; path.append(ego.copy())
            path=np.asarray(path); plen=float(np.linalg.norm(np.diff(path[:,:2],axis=0),axis=1).sum()) if len(path)>1 else 0.
            rec.append({'object_id':oid,'planner':name,'link_model':link_name,'feasible':feasible,'decisions':decisions,'duration_s':decisions*a.dt,
                        'path_length_m':plen,'mean_speed_mps':float(path[:,3].mean()),'min_target_distance_m':float(min(distances)) if distances else np.nan,
                        'mean_snr_db':float(np.mean(snrs)) if snrs else np.nan,'p05_snr_db':float(np.percentile(snrs,5)) if snrs else np.nan,
                        'outage_rate':float(np.mean(np.asarray(snrs)<threshold)) if snrs else np.nan,'mean_runtime_ms':float(np.mean(runtimes)) if runtimes else np.nan})
    df=pd.DataFrame(rec); a.output.parent.mkdir(parents=True,exist_ok=True); df.to_csv(a.output,index=False)
    summary=df.groupby(['planner','link_model'],as_index=False).agg(tracks=('object_id','count'),feasible_rate=('feasible','mean'),outage_rate=('outage_rate','mean'),mean_snr_db=('mean_snr_db','mean'),path_length_m=('path_length_m','mean'),min_target_distance_m=('min_target_distance_m','mean'),mean_runtime_ms=('mean_runtime_ms','mean'))
    summary.to_csv(a.output.with_name(a.output.stem+'_summary.csv'),index=False); print(summary.to_string(index=False))
    print('Scientific status: measured CMHT target motion + simulated receding-horizon ego + modeled connectivity.')
if __name__=='__main__': main()
