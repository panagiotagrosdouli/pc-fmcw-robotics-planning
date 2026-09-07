#!/usr/bin/env python3
"""Generate publication-style figures from episode/traces CSV files."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLANNERS=['P0','P1','P2','P3','P4']


def parse_args():
    p=argparse.ArgumentParser(); p.add_argument('--episodes',required=True); p.add_argument('--traces'); p.add_argument('--output-dir',required=True); p.add_argument('--bootstrap-samples',type=int,default=5000); p.add_argument('--rng-seed',type=int,default=2026); return p.parse_args()


def boot_ci(x,samples,rng):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if len(x)==0:return np.nan,np.nan,np.nan
    g=np.random.default_rng(rng); idx=g.integers(0,len(x),size=(samples,len(x))); means=x[idx].mean(axis=1); return float(x.mean()),float(np.quantile(means,.025)),float(np.quantile(means,.975))


def save_violin(frame,metric,out):
    data=[frame.loc[frame.planner==p,metric].replace([np.inf,-np.inf],np.nan).dropna().to_numpy() for p in PLANNERS]
    fig,ax=plt.subplots(figsize=(7.2,4.4)); ax.violinplot(data,showmedians=True); ax.boxplot(data,widths=.15,showfliers=False); ax.set_xticks(range(1,len(PLANNERS)+1),PLANNERS); ax.set_ylabel(metric.replace('_',' ')); ax.set_title(f'Planner comparison: {metric}'); fig.tight_layout(); fig.savefig(out/f'violin_{metric}.png',dpi=300); plt.close(fig)


def save_paired(frame,metric,baseline,candidate,out):
    keys=['experiment','setting_id','scenario','seed']; s=frame[frame.planner.isin([baseline,candidate])]; p=s.pivot(index=keys,columns='planner',values=metric).dropna()
    if baseline not in p or candidate not in p or p.empty:return
    d=p[candidate]-p[baseline]; fig,ax=plt.subplots(figsize=(6.4,4.2)); ax.scatter(np.arange(len(d)),d.values,s=16); ax.axhline(0,linewidth=1); ax.set_xlabel('Matched scenario-seed pair'); ax.set_ylabel(f'{candidate} - {baseline}'); ax.set_title(f'Paired improvement: {metric}'); fig.tight_layout(); fig.savefig(out/f'paired_{candidate}_vs_{baseline}_{metric}.png',dpi=300); plt.close(fig)


def save_robustness(frame,experiment,metric,out,samples,rng):
    sub=frame[frame.experiment==experiment]
    if sub.empty:return
    settings=list(dict.fromkeys(sub.setting_id.tolist())); fig,ax=plt.subplots(figsize=(7.4,4.5))
    for planner in [p for p in PLANNERS if p in set(sub.planner)]:
        means=[]; lows=[]; highs=[]; xs=[]
        for i,sid in enumerate(settings):
            x=sub[(sub.setting_id==sid)&(sub.planner==planner)][metric]; m,l,h=boot_ci(x,samples,rng+i); xs.append(i); means.append(m); lows.append(m-l); highs.append(h-m)
        ax.errorbar(xs,means,yerr=np.vstack([lows,highs]),marker='o',capsize=2,label=planner)
    ax.set_xticks(range(len(settings)),settings,rotation=35,ha='right'); ax.set_ylabel(metric.replace('_',' ')); ax.set_title(f'Robustness: {experiment}'); ax.legend(ncol=3); fig.tight_layout(); fig.savefig(out/f'robustness_{experiment}_{metric}.png',dpi=300); plt.close(fig)


def save_tradeoff(frame,out):
    core=frame[frame.experiment=='core'];
    if core.empty:return
    g=core.groupby('planner',as_index=False).agg(outage=('mean_outage_probability','mean'),progress=('progress_m','mean'),clearance=('min_target_distance_m','mean'))
    fig,ax=plt.subplots(figsize=(6.2,4.6)); ax.scatter(g.progress,g.outage,s=50)
    for _,r in g.iterrows(): ax.annotate(r.planner,(r.progress,r.outage),xytext=(4,4),textcoords='offset points')
    ax.set_xlabel('Progress (m)'); ax.set_ylabel('Modeled outage probability'); ax.set_title('Communication–mobility trade-off'); fig.tight_layout(); fig.savefig(out/'tradeoff_outage_progress.png',dpi=300); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.2,4.6)); ax.scatter(g.clearance,g.outage,s=50)
    for _,r in g.iterrows(): ax.annotate(r.planner,(r.clearance,r.outage),xytext=(4,4),textcoords='offset points')
    ax.set_xlabel('Minimum target clearance (m)'); ax.set_ylabel('Modeled outage probability'); ax.set_title('Communication–safety trade-off'); fig.tight_layout(); fig.savefig(out/'tradeoff_outage_clearance.png',dpi=300); plt.close(fig)


def save_trajectory(traces,out):
    if traces is None or traces.empty:return
    core=traces[(traces.experiment=='core') & traces.planner.isin(PLANNERS)]
    if core.empty:return
    scenario=core.scenario.iloc[0]; seed=int(core.seed.iloc[0]); sub=core[(core.scenario==scenario)&(core.seed==seed)]
    fig,ax=plt.subplots(figsize=(6.6,5.0));
    target=sub.sort_values('step').drop_duplicates('step'); ax.plot(target.target_x_m,target.target_y_m,'--',label='target truth')
    for p in PLANNERS:
        q=sub[sub.planner==p].sort_values('step')
        if not q.empty: ax.plot(q.ego_x_m,q.ego_y_m,label=p)
    ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)'); ax.set_title(f'Representative matched trajectory: {scenario}, seed {seed}'); ax.axis('equal'); ax.legend(ncol=3); fig.tight_layout(); fig.savefig(out/'representative_trajectory.png',dpi=300); plt.close(fig)


def main():
    a=parse_args(); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True); frame=pd.read_csv(a.episodes); traces=pd.read_csv(a.traces) if a.traces else None
    core=frame[frame.experiment=='core'] if 'experiment' in frame else frame
    for metric in ['mean_snr_db','min_snr_db','mean_outage_probability','mean_goodput_bps_model','progress_m','min_target_distance_m','collision_indicator','no_candidate_rate']:
        if metric in core: save_violin(core,metric,out)
    for metric in ['mean_outage_probability','mean_snr_db','min_snr_db','progress_m','min_target_distance_m','collision_indicator','no_candidate_rate']:
        if metric in frame:
            save_paired(frame,metric,'P1','P2',out); save_paired(frame,metric,'P2','P3',out); save_paired(frame,metric,'P2','P4',out)
    for experiment in ['horizon','weight','shift','blackout']:
        if 'mean_outage_probability' in frame: save_robustness(frame,experiment,'mean_outage_probability',out,a.bootstrap_samples,a.rng_seed)
    save_tradeoff(frame,out); save_trajectory(traces,out); print(f'wrote publication figures to {out}')

if __name__=='__main__': main()
