"""Run the dataset-free PC-FMCW-informed P0-P4 closed-loop benchmark."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings,run_benchmark
from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor

def main():
 p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=10);p.add_argument('--output-dir',type=Path,default=Path('results/pc_fmcw_sim'));p.add_argument('--mc-samples',type=int,default=32);a=p.parse_args();out=ROOT/a.output_dir;out.mkdir(parents=True,exist_ok=True)
 settings=BenchmarkSettings(p3_mc_samples=a.mc_samples);rows=run_benchmark(seeds=range(a.seeds),settings=settings);df=pd.DataFrame(rows);df.to_csv(out/'episodes.csv',index=False)
 summary=df.groupby('planner',as_index=False).agg(episodes=('seed','size'),outage=('mean_outage_probability','mean'),snr_db=('mean_snr_db','mean'),ber_model=('mean_ber_model','mean'),goodput_bps_model=('mean_goodput_bps_model','mean'),path_length_m=('path_length_m','mean'),progress_m=('progress_m','mean'),min_target_distance_m=('min_target_distance_m','min'),collision_rate=('collision_indicator','mean'))
 summary.to_csv(out/'summary.csv',index=False)
 manifest={'study':'dataset-free PC-FMCW-informed closed-loop robotics simulation','seeds':a.seeds,'planners':['P0','P1','P2','P3','P4'],'target_motion':'simulated','ego_motion':'simulated receding-horizon control','prediction':'P2/P3 share constant-velocity mean; P4 alone uses future truth','link_provenance':PCFMCWPlanningLinkPredictor().provenance(),'claim_boundary':'Simulation study; not optical measurements and not a real-vehicle trial.'};(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(summary.to_string(index=False))
if __name__=='__main__':main()
