"""Paper-grade paired analysis of hybrid CMHT closed-loop runs."""
from __future__ import annotations
import argparse,sys
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from iscai.evaluation.statistics import cluster_paired_bootstrap_delta,paired_wilcoxon,holm_adjust,pareto_mask
METRICS={'outage_rate':'min','mean_snr_db':'max','path_length_m':'min','min_target_distance_m':'max','mean_runtime_ms':'min'}
def parse_bool(s):
 if pd.api.types.is_bool_dtype(s):return s
 x=s.astype(str).str.strip().str.lower();valid=x.isin(['true','false','1','0'])
 if not valid.all():raise ValueError('feasible column contains unrecognized boolean values')
 return x.isin(['true','1'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('results/cmht_closed_loop.csv'));p.add_argument('--output-dir',type=Path,default=Path('results/cmht_closed_loop_analysis'));a=p.parse_args();df=pd.read_csv(a.input)
 if 'track_id' not in df.columns:raise ValueError('track_id is required: rerun closed-loop replay with contiguous-segment identifiers')
 df=df[parse_bool(df.feasible)].copy();a.output_dir.mkdir(parents=True,exist_ok=True);planners=sorted(df.planner.unique());rows=[]
 # Statistical unit is a contiguous CMHT track segment, not merely object_id.
 track=df.groupby(['track_id','planner'],as_index=False)[list(METRICS)].mean()
 for metric in METRICS:
  mr=[]
  for pa,pb in combinations(planners,2):
   x=track[track.planner==pa][['track_id',metric]].merge(track[track.planner==pb][['track_id',metric]],on='track_id',suffixes=('_a','_b')).dropna()
   if len(x)<2:continue
   boot=cluster_paired_bootstrap_delta(x[f'{metric}_a'],x[f'{metric}_b'],x.track_id,samples=10000,rng=7);test=paired_wilcoxon(x[f'{metric}_a'],x[f'{metric}_b']);mr.append({'metric':metric,'planner_a':pa,'planner_b':pb,'n_tracks':len(x),**boot,'pvalue':test['pvalue']})
  if mr:
   adj=holm_adjust([r['pvalue'] for r in mr])
   for r,q in zip(mr,adj):r['pvalue_holm']=float(q);rows.append(r)
 pd.DataFrame(rows).to_csv(a.output_dir/'paired_track_statistics.csv',index=False);summary=track.groupby('planner',as_index=False).agg(tracks=('track_id','nunique'),outage_rate=('outage_rate','mean'),mean_snr_db=('mean_snr_db','mean'),path_length_m=('path_length_m','mean'),min_target_distance_m=('min_target_distance_m','mean'),mean_runtime_ms=('mean_runtime_ms','mean'));summary['pareto_connectivity_mobility']=pareto_mask(summary[['outage_rate','path_length_m']].to_numpy(),minimize=[True,True]);summary.to_csv(a.output_dir/'planner_track_summary.csv',index=False);fig,ax=plt.subplots(figsize=(6,4));ax.scatter(summary.path_length_m,summary.outage_rate)
 for _,r in summary.iterrows():ax.annotate(r.planner,(r.path_length_m,r.outage_rate))
 ax.set_xlabel('Mean closed-loop path length (m)');ax.set_ylabel('Mean outage rate');ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(a.output_dir/'pareto_connectivity_mobility.png',dpi=180);plt.close(fig);print('Wrote contiguous-track paired statistics, Holm-adjusted p-values, and connectivity-mobility Pareto summary.')
if __name__=='__main__':main()
