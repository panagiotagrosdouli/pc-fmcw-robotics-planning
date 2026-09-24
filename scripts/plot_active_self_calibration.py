#!/usr/bin/env python3
"""Generate prospective active-self-calibration figures from executed artifacts."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ORDER=["C0","C1","C2","C3","C4"]

def _bootstrap(x,samples=2000,seed=2026):
    x=np.asarray(x,float);x=x[np.isfinite(x)]
    if len(x)==0:return np.nan,np.nan,np.nan
    if len(x)==1:return float(x[0]),float(x[0]),float(x[0])
    rng=np.random.default_rng(seed);idx=rng.integers(0,len(x),size=(samples,len(x)))
    b=x[idx].mean(axis=1)
    return float(x.mean()),float(np.quantile(b,.025)),float(np.quantile(b,.975))

def _planner_plot(df,metric,ylabel,out):
    seed=df.groupby(["seed","planner"],as_index=False)[metric].mean()
    means=[];lo=[];hi=[]
    for i,p in enumerate(ORDER):
        m,l,h=_bootstrap(seed.loc[seed.planner==p,metric],seed=2026+i)
        means.append(m);lo.append(m-l);hi.append(h-m)
    fig,ax=plt.subplots(figsize=(6.4,4.2))
    ax.bar(ORDER,means,yerr=np.array([lo,hi]),capsize=3)
    ax.set_ylabel(ylabel);ax.set_xlabel("Planner");ax.grid(axis="y",alpha=.25)
    fig.tight_layout();fig.savefig(out,dpi=220);plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episodes",type=Path,required=True)
    p.add_argument("--steps",type=Path,default=None)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    episodes=pd.read_csv(ROOT/args.episodes);out=ROOT/args.output_dir;out.mkdir(parents=True,exist_ok=True)
    _planner_plot(episodes,"cumulative_decision_regret","Mean cumulative decision regret",out/"decision_regret_by_planner.png")
    _planner_plot(episodes,"final_parameter_error_normalized","Final normalized parameter error",out/"parameter_error_by_planner.png")
    probe=episodes.groupby(["scenario","planner"],as_index=False)["probe_fraction"].mean()
    fig,ax=plt.subplots(figsize=(8.0,4.5))
    x=np.arange(probe.scenario.nunique());width=.15
    scenarios=list(dict.fromkeys(probe.scenario))
    for i,planner in enumerate(ORDER):
        vals=[float(probe[(probe.scenario==s)&(probe.planner==planner)].probe_fraction.iloc[0]) if len(probe[(probe.scenario==s)&(probe.planner==planner)]) else np.nan for s in scenarios]
        ax.bar(x+(i-2)*width,vals,width,label=planner)
    ax.set_xticks(x,scenarios,rotation=25,ha="right");ax.set_ylabel("Probe fraction");ax.legend(ncol=5)
    fig.tight_layout();fig.savefig(out/"probe_fraction_by_scenario.png",dpi=220);plt.close(fig)
    if args.steps is not None:
        steps=pd.read_csv(ROOT/args.steps);c3=steps[steps.planner=="C3"]
        fig,ax=plt.subplots(figsize=(6.4,4.2))
        ax.scatter(c3.decision_uncertainty,c3.selected_information_gain,s=12,alpha=.5)
        ax.set_xlabel("Decision uncertainty");ax.set_ylabel("Selected information gain")
        fig.tight_layout();fig.savefig(out/"decision_trigger_information.png",dpi=220);plt.close(fig)
    print(f"wrote figures to {out}")

if __name__=="__main__":main()
