#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt

def boot(x,n=3000,seed=0):
    x=np.asarray(x,float); rng=np.random.default_rng(seed); s=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)])
    return float(x.mean()),float(np.quantile(s,.025)),float(np.quantile(s,.975))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",default="results/real_v2x_horizon"); ap.add_argument("--bootstrap",type=int,default=3000); a=ap.parse_args(); root=Path(a.input); figs=root/"figures"; figs.mkdir(exist_ok=True)
    s=pd.read_csv(root/"horizon_summary.csv"); r=pd.read_csv(root/"horizon_run_metrics.csv"); d=s[s.target=="delay_ms"].sort_values("median_horizon_ms")
    fig,ax=plt.subplots(figsize=(6.5,4.2)); ax.plot(d.median_horizon_ms,d.persistence_mae,marker='o',label='persistence'); ax.plot(d.median_horizon_ms,d.global_spatial_mae,marker='o',label='global spatial'); ax.plot(d.median_horizon_ms,d.conditioned_spatial_mae,marker='o',label='conditioned spatial'); ax.plot(d.median_horizon_ms,d.fusion_mae,marker='o',label='calibrated fusion'); ax.set_xlabel('Median prediction horizon (ms)'); ax.set_ylabel('Delay MAE (ms)'); ax.legend(); fig.tight_layout(); fig.savefig(figs/'delay_mae_vs_horizon.png',dpi=220); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.5,4.2)); ax.plot(d.median_horizon_ms,d.global_coverage,marker='o',label='global conformal'); ax.plot(d.median_horizon_ms,d.adaptive_coverage,marker='o',label='support-conditioned'); ax.axhline(.9,linestyle='--',label='nominal 90%'); ax.set_xlabel('Median prediction horizon (ms)'); ax.set_ylabel('Empirical interval coverage'); ax.legend(); fig.tight_layout(); fig.savefig(figs/'coverage_vs_horizon.png',dpi=220); plt.close(fig)
    rows=[]; q=r[r.target=="delay_ms"]
    for h,g in q.groupby('horizon_steps'):
        delta=g.fusion_mae-g.persistence_mae; mean,lo,hi=boot(delta,a.bootstrap); p=float(wilcoxon(delta).pvalue) if len(delta)>=5 and np.any(np.abs(delta)>1e-12) else np.nan
        map_delta=g.conditioned_spatial_mae-g.global_spatial_mae; mmap,mlo,mhi=boot(map_delta,a.bootstrap)
        rows.append({'horizon_steps':h,'n_runs':len(g),'fusion_minus_persistence_mae_ms':mean,'ci95_lo':lo,'ci95_hi':hi,'wilcoxon_p':p,'conditioned_minus_global_spatial_mae_ms':mmap,'map_ci95_lo':mlo,'map_ci95_hi':mhi})
    pd.DataFrame(rows).to_csv(root/'paired_horizon_effects.csv',index=False); print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__': main()
