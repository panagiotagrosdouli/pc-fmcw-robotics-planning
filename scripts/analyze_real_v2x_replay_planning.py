#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

def bootstrap(x, n=5000, seed=0):
    x=np.asarray(x,float)
    rng=np.random.default_rng(seed)
    vals=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)])
    return float(x.mean()), float(np.quantile(vals,.025)), float(np.quantile(vals,.975))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",default="results/real_v2x_replay"); ap.add_argument("--bootstrap",type=int,default=5000)
    a=ap.parse_args(); root=Path(a.input); d=pd.read_csv(root/"run_metrics.csv")
    rows=[]
    for metric in ("violation_fraction","mean_measured_delay_ms","mean_mobility_deviation","unsupported_fraction"):
        pivot=d.pivot(index="run_id",columns="mode",values=metric)
        for lhs,rhs in (("P2","P1"),("P3","P2"),("P3","P1")):
            x=(pivot[lhs]-pivot[rhs]).dropna().to_numpy(float)
            mean,lo,hi=bootstrap(x,a.bootstrap)
            try:
                p=float(wilcoxon(x).pvalue) if np.any(x!=0) else 1.0
            except ValueError:
                p=1.0
            rows.append({"metric":metric,"comparison":f"{lhs}-{rhs}","n_runs":len(x),
                         "mean_delta":mean,"ci95_lo":lo,"ci95_hi":hi,"wilcoxon_p":p})
    out=pd.DataFrame(rows); out.to_csv(root/"paired_planner_effects.csv",index=False); print(out.to_string(index=False))

if __name__=="__main__": main()
