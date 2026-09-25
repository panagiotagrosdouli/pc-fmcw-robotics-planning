#!/usr/bin/env python3
"""Paper-ready plots for measured vehicular VLC validation."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=Path("artifacts/active_self_calibration/real_vvlc"))
    args=ap.parse_args();root=args.input;out=root/"figures";out.mkdir(parents=True,exist_ok=True)
    m=pd.read_csv(root/"model_metrics.csv")
    q=m[m.split.isin(["spatial_test","repository_validation"])].copy()
    splits=["spatial_test","repository_validation"];models=["distance_only","directional"]
    x=np.arange(len(splits));width=.34
    fig,ax=plt.subplots(figsize=(6.4,4.2))
    for i,model in enumerate(models):
        vals=[float(q[(q.split==s)&(q.model==model)].mae_db.iloc[0]) for s in splits]
        ax.bar(x+(i-.5)*width,vals,width,label=model)
    ax.set_xticks(x,["Held-out spatial groups","Repository validation"])
    ax.set_ylabel("Path-loss MAE (dB)");ax.legend();ax.grid(axis="y",alpha=.25)
    fig.tight_layout();fig.savefig(out/"real_vvlc_mae.png",dpi=220);plt.close(fig)

    s=pd.read_csv(root/"residual_strata.csv")
    angle=s.groupby("angle_deg",as_index=False).agg(
        distance_mae_db=("distance_mae_db","mean"),
        directional_mae_db=("directional_mae_db","mean"),
    ).sort_values("angle_deg")
    x=np.arange(len(angle));fig,ax=plt.subplots(figsize=(6.4,4.2))
    ax.bar(x-width/2,angle.distance_mae_db,width,label="distance_only")
    ax.bar(x+width/2,angle.directional_mae_db,width,label="directional")
    ax.set_xticks(x,[f"{v:g}°" for v in angle.angle_deg])
    ax.set_xlabel("Measured receiver inclination");ax.set_ylabel("Held-out MAE (dB)")
    ax.legend();ax.grid(axis="y",alpha=.25);fig.tight_layout()
    fig.savefig(out/"real_vvlc_mae_by_angle.png",dpi=220);plt.close(fig)
    print(f"wrote real V-VLC figures to {out}")

if __name__=="__main__":main()
