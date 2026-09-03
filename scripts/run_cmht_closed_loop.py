"""Receding-horizon Stage-9 replay with measured CMHT target motion.
Target motion is measured; ego is simulated; connectivity is modeled. Measured
timestamps are supported by the CV path. A frame-step Transformer is rejected
with measured-time replay unless the user explicitly selects fixed-step replay;
this prevents silently mixing incompatible temporal semantics.
"""
from __future__ import annotations
import argparse,sys,time
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from iscai.data.cmht_loader import extract_object_positions,timestamp_map,read_timestamp_file
from iscai.prediction.trajectory_predictor import constant_velocity
from iscai.prediction.link_predictor import LinkPredictor
from iscai.connectivity.calibrated_predictor import CalibratedGeometryLinkPredictor
from iscai.planning.planners import MobilityOnlyPlanner,ReactiveConnectivityPlanner,PredictiveConnectivityPlanner,OracleConnectivityPlanner
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner
class _ExecutedStep:
 def __init__(self,states):self.states=np.asarray(states,float)
def states_from_xy(xy,dt=None,times=None):
 xy=np.asarray(xy,float);out=np.zeros((len(xy),4));out[:,:2]=xy
 if len(xy)>1:
  if times is None:
   if dt is None or dt<=0:raise ValueError('positive dt required when times are omitted')
   times=np.arange(len(xy),dtype=float)*dt
  times=np.asarray(times,float)
  if times.shape!=(len(xy),) or np.any(np.diff(times)<=0):raise ValueError('times must be strictly increasing and match xy')
  v=np.gradient(xy,times,axis=0);out[:,2]=np.arctan2(v[:,1],v[:,0]);out[:,3]=np.linalg.norm(v,axis=1)
 return out
def initial_ego(hist,dt=None,times=None,gap=12.):
 elapsed=dt if times is None else float(times[-1]-times[-2])
 if elapsed is None or elapsed<=0:raise ValueError('positive elapsed time required for ego initialization')
 v=(hist[-1]-hist[-2])/elapsed;s=float(np.linalg.norm(v));yaw=float(np.arctan2(v[1],v[0])) if s>1e-6 else 0.;return np.array([hist[-1,0]-gap*np.cos(yaw),hist[-1,1]-gap*np.sin(yaw),yaw,max(s,1.)])
def tracks(rows,timestamped=False):
 cols=['frame','timestamp','x','y','z','object_id','class'] if timestamped else ['frame','x','y','z','object_id','class'];df=pd.DataFrame(rows,columns=cols).sort_values(['object_id','frame'])
 for oid,g in df.groupby('object_id',sort=False):
  g=g.sort_values('frame');f=g.frame.to_numpy(int);xy=g[['x','y']].to_numpy(float);tm=g.timestamp.to_numpy(float) if timestamped else None;cuts=np.r_[0,np.where(np.diff(f)!=1)[0]+1,len(f)]
  for j,(a,b) in enumerate(zip(cuts[:-1],cuts[1:])):
   if b-a>=3:yield f'{oid}:{j}',oid,f[a:b],xy[a:b],None if tm is None else tm[a:b]
def load_transformer(path):
 import torch
 from iscai.prediction.transformer import TrajectoryTransformer
 ck=torch.load(path,map_location='cpu');model=TrajectoryTransformer(horizon=int(ck['horizon']));model.load_state_dict(ck['state_dict']);model.eval();cal=ck.get('sigma_calibration',{});scale=float(cal.get('scale',1.));source='validation_calibrated' if cal.get('fit_split')=='validation' else 'uncalibrated';timing=ck.get('timing',{'mode':'legacy_unknown','uses_physical_timestamps':False});return model,int(ck['history']),int(ck['horizon']),scale,source,timing
def validate_transformer_timing(timing,measured_timestamps):
 if measured_timestamps and not bool(timing.get('uses_physical_timestamps',False)):
  raise ValueError('Transformer checkpoint is frame-step based and cannot be used with --timestamps. Use CV measured-time replay, or train a timestamp-aware/resampled Transformer checkpoint.')
def transformer_forecast(model,hist,steps,sigma_scale=1.):
 import torch
 with torch.no_grad():mean,logs=model(torch.tensor(hist[None],dtype=torch.float32))
 mean=mean[0].cpu().numpy();sigma=np.exp(logs[0].cpu().numpy())*sigma_scale;k=min(steps,len(mean));return hist[-1]+mean[:k],sigma[:k]
def planner_targets(name,pred_xy,truth_xy,tf_mean,tf_sigma,dt,fixed_sigma,target_times=None):
 if name=='P4':return states_from_xy(truth_xy,dt,target_times),'oracle','none'
 if name=='P1':return states_from_xy(pred_xy,dt,target_times),'cv_reactive','none'
 if name=='P2':
  mean=tf_mean if tf_mean is not None else pred_xy;return states_from_xy(mean,dt,target_times),'transformer' if tf_mean is not None else 'cv','none'
 if name=='P3':
  mean=tf_mean if tf_mean is not None else pred_xy;sigma=tf_sigma if tf_sigma is not None else np.full_like(mean,fixed_sigma);return {'mean_xy':mean,'sigma_xy':sigma},'transformer' if tf_mean is not None else 'cv','validation_calibrated' if tf_sigma is not None else 'fixed_sigma'
 return states_from_xy(pred_xy,dt,target_times),'none','none'
def main():
 p=argparse.ArgumentParser();p.add_argument('--labels',type=Path,required=True);p.add_argument('--timestamps',type=Path);p.add_argument('--frame-start',type=int,default=0);p.add_argument('--history',type=int,default=10);p.add_argument('--horizon',type=int,default=20);p.add_argument('--dt',type=float,default=.1,help='planner integration dt and fallback data dt');p.add_argument('--sigma-m',type=float,default=.75);p.add_argument('--transformer-checkpoint',type=Path);p.add_argument('--max-tracks',type=int,default=100);p.add_argument('--link-calibration',type=Path);p.add_argument('--output',type=Path,default=Path('results/cmht_closed_loop.csv'));a=p.parse_args();ts=None
 if a.timestamps:
  vals=read_timestamp_file(a.timestamps);ts=timestamp_map(a.timestamps,frames=range(a.frame_start,a.frame_start+len(vals)))
 rows=extract_object_positions(a.labels,timestamps=ts);transformer=None;thist=thor=None;tscale=1.;tsource='none';ttiming={'mode':'none','uses_physical_timestamps':False}
 if a.transformer_checkpoint:
  transformer,thist,thor,tscale,tsource,ttiming=load_transformer(a.transformer_checkpoint);validate_transformer_timing(ttiming,ts is not None)
  if a.horizon>thor:raise ValueError(f'closed-loop horizon {a.horizon} exceeds Transformer horizon {thor}')
 if a.link_calibration:link=CalibratedGeometryLinkPredictor.from_json(a.link_calibration);threshold=link.outage_threshold_db;link_name='frozen_calibrated'
 else:link=LinkPredictor(reference_snr_db=20.,reference_distance=10.,min_snr_db=8.);threshold=link.min_snr_db;link_name='geometry_surrogate'
 builders={'P0':lambda:MobilityOnlyPlanner(link),'P1':lambda:ReactiveConnectivityPlanner(link),'P2':lambda:PredictiveConnectivityPlanner(link),'P3':lambda:RiskAwarePredictivePlanner(link,mc_samples=128,threshold_db=threshold,random_seed=0),'P4':lambda:OracleConnectivityPlanner(link)};rec=[];used=0
 for track_id,oid,frames,xy,times in tracks(rows,ts is not None):
  required=max(a.history,thist or 0)
  if len(xy)<required+2:continue
  used+=1
  if used>a.max_tracks:break
  for name,build in builders.items():
   planner=build();ego=initial_ego(xy[:required],a.dt,None if times is None else times[:required]);path=[ego.copy()];snrs=[];runtimes=[];distances=[];feasible=True;decisions=0;sigmas=[];predictor='none';unc='none';elapsed=[]
   for t in range(required,len(xy)-1):
    available=min(a.horizon,len(xy)-t);lo=max(0,t-a.history);hist=xy[lo:t];future_times=None if times is None else times[t:t+available];history_times=None if times is None else times[lo:t];pred_xy=constant_velocity(hist,available,a.dt,history_times=history_times,future_times=future_times);truth_xy=xy[t:t+available];tf_mean=tf_sigma=None
    if transformer is not None and name in ('P2','P3'):
     mh=xy[t-thist:t];tf_mean,tf_sigma=transformer_forecast(transformer,mh,available,tscale)
    target,predictor,unc=planner_targets(name,pred_xy,truth_xy,tf_mean,tf_sigma,a.dt,a.sigma_m,future_times)
    if name=='P3':sigmas.extend(np.asarray(target['sigma_xy']).ravel())
    tic=time.perf_counter();result=planner.plan(ego,target,obstacles=[],reference_speed=ego[3]);runtimes.append(1e3*(time.perf_counter()-tic));decisions+=1
    if result.candidate is None or len(result.candidate.states)<2:feasible=False;break
    nxt=np.asarray(result.candidate.states[1],float);pair_times=None if times is None else times[t:t+2];realized=link.predict(_ExecutedStep(np.vstack([ego,nxt])),states_from_xy(xy[t:t+2],a.dt,pair_times));snrs.append(float(np.asarray(realized.snr_db)[-1]));distances.append(float(np.linalg.norm(nxt[:2]-xy[t+1])));elapsed.append(a.dt if times is None else float(times[t+1]-times[t]));ego=nxt;path.append(ego.copy())
   path=np.asarray(path);plen=float(np.linalg.norm(np.diff(path[:,:2],axis=0),axis=1).sum()) if len(path)>1 else 0.;rec.append({'track_id':track_id,'object_id':oid,'planner':name,'trajectory_predictor':predictor,'link_model':link_name,'timing_source':'measured_timestamp' if times is not None else 'fixed_dt_fallback','transformer_timing_mode':ttiming.get('mode','none') if transformer is not None else 'none','planner_dt_s':a.dt,'trajectory_uncertainty':tsource if name=='P3' and transformer is not None else unc,'sigma_scale':tscale if name=='P3' and transformer is not None else np.nan,'feasible':feasible,'decisions':decisions,'duration_s':float(np.sum(elapsed)),'path_length_m':plen,'mean_speed_mps':float(path[:,3].mean()),'min_target_distance_m':float(min(distances)) if distances else np.nan,'mean_predictive_sigma_m':float(np.mean(sigmas)) if sigmas else np.nan,'mean_snr_db':float(np.mean(snrs)) if snrs else np.nan,'p05_snr_db':float(np.percentile(snrs,5)) if snrs else np.nan,'outage_rate':float(np.mean(np.asarray(snrs)<threshold)) if snrs else np.nan,'mean_runtime_ms':float(np.mean(runtimes)) if runtimes else np.nan})
 df=pd.DataFrame(rec);a.output.parent.mkdir(parents=True,exist_ok=True);df.to_csv(a.output,index=False);summary=df.groupby(['planner','trajectory_predictor','link_model','timing_source','trajectory_uncertainty'],as_index=False,dropna=False).agg(tracks=('track_id','count'),feasible_rate=('feasible','mean'),outage_rate=('outage_rate','mean'),mean_snr_db=('mean_snr_db','mean'),duration_s=('duration_s','mean'),path_length_m=('path_length_m','mean'),min_target_distance_m=('min_target_distance_m','mean'),mean_runtime_ms=('mean_runtime_ms','mean'));summary.to_csv(a.output.with_name(a.output.stem+'_summary.csv'),index=False);print(summary.to_string(index=False));print('Scientific status: measured CMHT target motion + simulated fixed-step ego planner + modeled connectivity. Frame-step Transformer checkpoints are not mixed with measured-timestamp replay.')
if __name__=='__main__':main()
