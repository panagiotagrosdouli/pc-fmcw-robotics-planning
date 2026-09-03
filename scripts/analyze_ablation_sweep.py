"""Generate paper-ready robustness curves from the predeclared ablation sweep."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def curve(df,x,fixed,out,name):
    d=df.copy()
    for k,v in fixed.items(): d=d[d[k]==v]
    if d.empty: return
    g=d.groupby(['planner',x],as_index=False).agg(outage_rate=('outage_rate','mean'),runtime_ms=('runtime_ms','mean'))
    fig,ax=plt.subplots(figsize=(6,4))
    for planner,p in g.groupby('planner'): ax.plot(p[x],p.outage_rate,marker='o',label=planner)
    ax.set_xlabel(x.replace('_',' ')); ax.set_ylabel('Mean realized outage rate'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(out/name,dpi=180); plt.close(fig)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,default=Path('results/ablations/cmht_ablation.csv')); p.add_argument('--output-dir',type=Path,default=Path('results/ablations'))
    a=p.parse_args(); df=pd.read_csv(a.input); df=df[df.feasible.astype(bool)].copy(); a.output_dir.mkdir(parents=True,exist_ok=True)
    # Predeclared reference slice for one-dimensional sensitivity curves.
    ref={'horizon_s':2.0,'prediction_noise_m':0.0,'sigma_m':0.75,'connectivity_weight':1.0}
    curve(df,'horizon_s',{k:v for k,v in ref.items() if k!='horizon_s'},a.output_dir,'outage_vs_horizon.png')
    curve(df,'prediction_noise_m',{k:v for k,v in ref.items() if k!='prediction_noise_m'},a.output_dir,'outage_vs_prediction_error.png')
    curve(df,'sigma_m',{k:v for k,v in ref.items() if k!='sigma_m'},a.output_dir,'outage_vs_uncertainty.png')
    curve(df,'connectivity_weight',{k:v for k,v in ref.items() if k!='connectivity_weight'},a.output_dir,'outage_vs_connectivity_weight.png')
    # Full factorial aggregate remains available for interaction analysis rather than hiding it behind 1-D plots.
    agg=df.groupby(['planner','horizon_s','prediction_noise_m','sigma_m','connectivity_weight'],as_index=False).agg(
        outage_mean=('outage_rate','mean'),outage_median=('outage_rate','median'),snr_mean=('mean_snr_db','mean'),runtime_mean_ms=('runtime_ms','mean'),n=('window','count'))
    agg.to_csv(a.output_dir/'factorial_summary.csv',index=False)
    print('Wrote four predeclared sensitivity curves and factorial_summary.csv')
if __name__=='__main__': main()
