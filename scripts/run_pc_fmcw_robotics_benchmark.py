"""Run the dataset-free PC-FMCW-informed P0-P4 closed-loop benchmark."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings,run_benchmark
from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor

def _validate_args(a):
 if a.seeds<1:raise SystemExit('--seeds must be >= 1')
 if not np.isfinite(a.dt) or a.dt<=0:raise SystemExit('--dt must be finite and > 0')
 if a.history<2:raise SystemExit('--history must be >= 2')
 if a.horizon<1:raise SystemExit('--horizon must be >= 1')
 if not np.isfinite(a.observation_sigma_m) or a.observation_sigma_m<0:raise SystemExit('--observation-sigma-m must be finite and >= 0')
 if not np.isfinite(a.prediction_sigma_m) or a.prediction_sigma_m<0:raise SystemExit('--prediction-sigma-m must be finite and >= 0')
 if not np.isfinite(a.connectivity_weight) or a.connectivity_weight<0:raise SystemExit('--connectivity-weight must be finite and >= 0')
 if a.mc_samples<1:raise SystemExit('--mc-samples must be >= 1')
 if not np.isfinite(a.collision_distance_m) or a.collision_distance_m<0:raise SystemExit('--collision-distance-m must be finite and >= 0')

def main():
 p=argparse.ArgumentParser();p.add_argument('--seed-start',type=int,default=0);p.add_argument('--seeds',type=int,default=10);p.add_argument('--output-dir',type=Path,default=Path('results/pc_fmcw_sim'));p.add_argument('--dt',type=float,default=.1);p.add_argument('--history',type=int,default=8);p.add_argument('--horizon',type=int,default=20);p.add_argument('--observation-sigma-m',type=float,default=.20);p.add_argument('--prediction-sigma-m',type=float,default=.75);p.add_argument('--connectivity-weight',type=float,default=1.0);p.add_argument('--mc-samples',type=int,default=32);p.add_argument('--collision-distance-m',type=float,default=2.0);a=p.parse_args();_validate_args(a);out=ROOT/a.output_dir;out.mkdir(parents=True,exist_ok=True)
 settings=BenchmarkSettings(dt=a.dt,history_steps=a.history,horizon_steps=a.horizon,observation_sigma_m=a.observation_sigma_m,prediction_sigma_m=a.prediction_sigma_m,connectivity_weight=a.connectivity_weight,p3_mc_samples=a.mc_samples,collision_distance_m=a.collision_distance_m);seed_values=range(a.seed_start,a.seed_start+a.seeds);rows=run_benchmark(seeds=seed_values,settings=settings);df=pd.DataFrame(rows);df.to_csv(out/'episodes.csv',index=False)
 summary=df.groupby('planner',as_index=False).agg(episodes=('seed','size'),outage=('mean_outage_probability','mean'),snr_db=('mean_snr_db','mean'),ber_model=('mean_ber_model','mean'),goodput_bps_model=('mean_goodput_bps_model','mean'),path_length_m=('path_length_m','mean'),progress_m=('progress_m','mean'),min_target_distance_m=('min_target_distance_m','min'),min_realized_ttc_s=('min_realized_ttc_s','min'),collision_rate=('collision_indicator','mean'),mean_no_candidate_steps=('no_candidate_steps','mean'),max_no_candidate_steps=('no_candidate_steps','max'));summary.to_csv(out/'summary.csv',index=False)
 manifest={'schema_version':1,'study':'dataset-free PC-FMCW-informed closed-loop robotics simulation','seed_start':a.seed_start,'seed_count':a.seeds,'seed_values':list(range(a.seed_start,a.seed_start+a.seeds)),'settings':settings.__dict__,'planners':['P0','P1','P2','P3','P4'],'target_motion':'simulated','ego_motion':'simulated receding-horizon control','prediction':'P0-P4 share the same mean target prediction for dynamic safety; P2/P3 use that mean for predictive connectivity; P4 alone uses future truth for connectivity forecasting','link_provenance':PCFMCWPlanningLinkPredictor().provenance(),'claim_boundary':'Simulation study; not optical measurements and not a real-vehicle trial.'};(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(summary.to_string(index=False))
if __name__=='__main__':main()
