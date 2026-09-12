#!/usr/bin/env python3
"""Aggregate deterministic grouped-run split robustness results.

Split seeds are robustness configurations, not independent statistical samples; no
p-values are computed across seeds. The script reports the distribution/range of the
held-out fusion-minus-persistence effect across grouped partitions.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="results/real_v2x_multisplit"); a=ap.parse_args(); root=Path(a.root)
    rows=[]
    for d in sorted(root.glob("seed_*")):
        f=d/"horizon_summary.csv"
        if not f.exists(): continue
        seed=int(d.name.split("_")[-1]); q=pd.read_csv(f); q=q[q.target=="delay_ms"]
        for _,r in q.iterrows():
            rows.append({"seed":seed,"horizon_steps":int(r.horizon_steps),"median_horizon_ms":float(r.median_horizon_ms),"persistence_mae":float(r.persistence_mae),"fusion_mae":float(r.fusion_mae),"delta_mae_ms":float(r.fusion_mae-r.persistence_mae),"fallback_fraction":float(r.fallback_to_persistence_fraction),"global_coverage":float(r.global_coverage),"adaptive_coverage":float(r.adaptive_coverage)})
    detail=pd.DataFrame(rows)
    if detail.empty: raise SystemExit("No multi-split horizon summaries found")
    detail.to_csv(root/"multisplit_detail.csv",index=False)
    agg=[]
    for h,g in detail.groupby("horizon_steps"):
        x=g.delta_mae_ms.to_numpy(float)
        agg.append({"horizon_steps":h,"n_seeds":len(g),"median_horizon_ms":float(g.median_horizon_ms.median()),"mean_delta_mae_ms":float(x.mean()),"median_delta_mae_ms":float(np.median(x)),"min_delta_mae_ms":float(x.min()),"max_delta_mae_ms":float(x.max()),"fraction_seeds_improved":float(np.mean(x<0)),"mean_fallback_fraction":float(g.fallback_fraction.mean()),"mean_global_coverage":float(g.global_coverage.mean()),"mean_adaptive_coverage":float(g.adaptive_coverage.mean())})
    out=pd.DataFrame(agg); out.to_csv(root/"multisplit_summary.csv",index=False); print(out.to_string(index=False))
if __name__=="__main__": main()
