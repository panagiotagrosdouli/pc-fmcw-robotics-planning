"""Run predeclared CMHT planning ablations.

This is a hybrid benchmark: CMHT supplies measured target motion, ego motion is
simulated, and connectivity comes from the selected frozen/surrogate predictor.
Prediction noise is synthetic and seeded; it is used only for robustness curves.
"""
from __future__ import annotations
import argparse, itertools, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_dataset import make_windows
from iscai.prediction.trajectory_predictor import constant_velocity
from iscai.prediction.link_predictor import LinkPredictor
from iscai.connectivity.calibrated_predictor import CalibratedGeometryLinkPredictor
from iscai.planning.planners import PredictiveConnectivityPlanner
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner


def target_states(xy,dt):
    xy=np.asarray(xy,float); z=np.zeros((len(xy),4)); z[:,:2]=xy
    if len(xy)>1:
        v=np.gradient(xy,dt,axis=0); z[:,2]=np.arctan2(v[:,1],v[:,0]); z[:,3]=np.linalg.norm(v,axis=1)
    return z

def ego_state(h,dt,gap=12.):
    v=(h[-1]-h[-2])/dt; s=float(np.linalg.norm(v)); yaw=float(np.arctan2(v[1],v[0])) if s>1e-6 else 0.
    return np.array([h[-1,0]-gap*np.cos(yaw),h[-1,1]-gap*np.sin(yaw),yaw,max(s,1.)])

def main():
    p=argparse.ArgumentParser(); p.add_argument('--labels',type=Path,required=True)
    p.add_argument('--config',type=Path,default=Path('configs/experiments/ablations.yaml'))
    p.add_argument('--link-calibration',type=Path); p.add_argument('--output',type=Path,default=Path('results/ablations/cmht_ablation.csv'))
    a=p.parse_args(); cfg=yaml.safe_load(a.config.read_text()); dt=float(cfg['dt_s']); hist=int(cfg['history_steps'])
    max_h=max(cfg['horizons_s']); max_steps=int(round(max_h/dt))
    windows=make_windows(extract_object_positions(a.labels),history=hist,horizon=max_steps)[:int(cfg['max_windows'])]
    if not windows: raise SystemExit('No contiguous CMHT windows found')
    if a.link_calibration:
        link=CalibratedGeometryLinkPredictor.from_json(a.link_calibration); threshold=link.outage_threshold_db; link_name='frozen_calibrated'
    else:
        link=LinkPredictor(reference_snr_db=20.,reference_distance=10.,min_snr_db=8.); threshold=link.min_snr_db; link_name='geometry_surrogate'
    rec=[]
    grid=itertools.product(cfg['horizons_s'],cfg['prediction_noise_m'],cfg['uncertainty_sigma_m'],cfg['connectivity_weights'],cfg['random_seeds'])
    for horizon_s,noise,sigma,w,seed in grid:
        steps=int(round(float(horizon_s)/dt)); rng=np.random.default_rng(int(seed))
        for wi,sample in enumerate(windows):
            h=np.asarray(sample['history'],float); truth_xy=np.asarray(sample['future'],float)[:steps]
            pred=constant_velocity(h,steps,dt)
            if noise: pred=pred+rng.normal(0.,float(noise),size=pred.shape)
            truth=target_states(truth_xy,dt); pred_states=target_states(pred,dt); ego=ego_state(h,dt)
            planners={
              'P2':(PredictiveConnectivityPlanner(link,connectivity_weight=float(w)),pred_states),
              'P3':(RiskAwarePredictivePlanner(link,connectivity_weight=float(w),mc_samples=int(cfg['mc_samples']),threshold_db=threshold,random_seed=int(seed)),
                    {'mean_xy':pred,'sigma_xy':np.full_like(pred,float(sigma))})}
            for name,(planner,target) in planners.items():
                tic=time.perf_counter(); result=planner.plan(ego,target,obstacles=[],reference_speed=ego[3]); ms=1e3*(time.perf_counter()-tic)
                row={'window':wi,'object_id':sample['object_id'],'planner':name,'horizon_s':horizon_s,'prediction_noise_m':noise,
                     'sigma_m':sigma,'connectivity_weight':w,'seed':seed,'runtime_ms':ms,'link_model':link_name,'feasible':result.candidate is not None}
                if result.candidate is not None:
                    f=link.predict(result.candidate,truth[:len(result.candidate.states)]); snr=np.asarray(f.snr_db,float)
                    row.update(outage_rate=float(np.mean(snr<threshold)),mean_snr_db=float(np.mean(snr)),p05_snr_db=float(np.percentile(snr,5)),score=float(result.score))
                rec.append(row)
    out=pd.DataFrame(rec); a.output.parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False)
    summary=out.groupby(['planner','horizon_s','prediction_noise_m','sigma_m','connectivity_weight'],as_index=False).agg(
        n=('window','count'),feasible_rate=('feasible','mean'),outage_rate=('outage_rate','mean'),mean_snr_db=('mean_snr_db','mean'),runtime_ms=('runtime_ms','mean'))
    summary.to_csv(a.output.with_name(a.output.stem+'_summary.csv'),index=False)
    print(f'Wrote {len(out)} rows. Scientific status: real CMHT target motion; synthetic seeded prediction-error perturbations; {link_name} link model.')
if __name__=='__main__': main()
