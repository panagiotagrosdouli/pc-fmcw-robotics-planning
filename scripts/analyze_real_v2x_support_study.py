#!/usr/bin/env python3
"""Statistics and publication figures for the real-V2X support study."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt

def bootstrap_mean_ci(x,n=5000,seed=0):
    x=np.asarray(x,float); rng=np.random.default_rng(seed)
    if len(x)==0: return (np.nan,np.nan,np.nan)
    sims=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)])
    return float(x.mean()),float(np.quantile(sims,.025)),float(np.quantile(sims,.975))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",default="results/real_v2x_support"); ap.add_argument("--bootstrap",type=int,default=5000); a=ap.parse_args()
    root=Path(a.input); figs=root/"figures"; figs.mkdir(exist_ok=True)
    pm=pd.read_csv(root/"predictor_metrics.csv"); prm=pd.read_csv(root/"predictor_run_metrics.csv"); pred=pd.read_csv(root/"test_predictions.csv"); sm=pd.read_csv(root/"support_stratified_metrics.csv")
    rows=[]; d=prm[prm.target=="delay_ms"]; base=d[d.model=="persistence"][["run_id","mae"]].rename(columns={"mae":"base"})
    for model in sorted(set(d.model)-{"persistence"}):
        m=d[d.model==model][["run_id","mae"]].rename(columns={"mae":"model"}); z=base.merge(m,on="run_id"); delta=z.model-z.base; mean,lo,hi=bootstrap_mean_ci(delta,a.bootstrap)
        p=float(wilcoxon(delta).pvalue) if len(delta)>=5 and np.any(np.abs(delta)>1e-12) else np.nan
        rows.append({"comparison":f"{model} - persistence","n_runs":len(delta),"delta_mae_ms":mean,"ci95_lo":lo,"ci95_hi":hi,"wilcoxon_p":p})
    pd.DataFrame(rows).to_csv(root/"paired_predictor_effects.csv",index=False)
    q=pm[pm.target=="delay_ms"].sort_values("mae"); fig,ax=plt.subplots(figsize=(6.4,4.2)); ax.bar(q.model,q.mae); ax.set_ylabel("Delay MAE (ms)"); ax.set_xlabel("Predictor"); ax.tick_params(axis="x",rotation=25); fig.tight_layout(); fig.savefig(figs/"delay_predictor_mae.png",dpi=220); plt.close(fig)
    err=np.abs(pred.delay_ms-pred.pred_delay_ms); fig,ax=plt.subplots(figsize=(6.4,4.2)); ax.scatter(pred.nearest_train_m,err,s=5,alpha=.25); ax.set_xlabel("Nearest training measurement (m)"); ax.set_ylabel("Absolute delay error (ms)"); fig.tight_layout(); fig.savefig(figs/"error_vs_support_distance.png",dpi=220); plt.close(fig)
    if len(sm):
        fig,ax=plt.subplots(figsize=(6.4,4.2)); ax.bar(sm.support_bin,sm.mae_ms); ax.set_xlabel("Spatial support bin"); ax.set_ylabel("Delay MAE (ms)"); ax.tick_params(axis="x",rotation=25); fig.tight_layout(); fig.savefig(figs/"support_stratified_mae.png",dpi=220); plt.close(fig)
    widths=pred.interval_hi_ms-pred.interval_lo_ms; fig,ax=plt.subplots(figsize=(6.4,4.2)); nbins=1 if float(np.ptp(widths))<1e-12 else 30; ax.hist(widths,bins=nbins); ax.set_xlabel("Conformal interval width (ms)"); ax.set_ylabel("Samples"); fig.tight_layout(); fig.savefig(figs/"conformal_interval_width.png",dpi=220); plt.close(fig)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=="__main__": main()
