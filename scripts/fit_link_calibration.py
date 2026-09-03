"""Fit the frozen planner link model from measured/calibration CSV data.

Required columns: distance_m, heading_error_rad, snr_db.
The script never invents provenance: source, measurement type and calibration
date are mandatory command-line metadata and are stored with the fit.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--measurement-type", required=True)
    p.add_argument("--calibration-date", required=True)
    p.add_argument("--outage-threshold-db", type=float, default=8.0)
    p.add_argument("--output", type=Path, default=Path("artifacts/link_calibration.json"))
    a=p.parse_args()
    df=pd.read_csv(a.csv)
    req={"distance_m","heading_error_rad","snr_db"}
    if not req.issubset(df.columns):
        raise SystemExit(f"Missing required columns: {sorted(req-set(df.columns))}")
    d=np.maximum(df.distance_m.to_numpy(float),1.0)
    ang=df.heading_error_rad.to_numpy(float)
    y=df.snr_db.to_numpy(float)
    # y = intercept + beta_log*log10(d) + beta_ang*ang^2
    X=np.column_stack([np.ones(len(y)), np.log10(d), ang**2])
    beta, *_=np.linalg.lstsq(X,y,rcond=None)
    reference=float(beta[0]); pathloss=float(-beta[1]/10.0)
    if beta[2] >= 0:
        raise SystemExit("Calibration produced nonphysical non-negative angular-loss coefficient")
    beam_sigma=float(np.sqrt(-4.343/beta[2]))
    pred=X@beta
    rmse=float(np.sqrt(np.mean((pred-y)**2)))
    out={
      "metadata":{"source":a.source,"measurement_type":a.measurement_type,
                  "calibration_date":a.calibration_date,"n_samples":int(len(y)),"fit_rmse_db":rmse},
      "parameters":{"reference_snr_db":reference,"pathloss_exponent":pathloss,
                    "beam_sigma_rad":beam_sigma,"outage_threshold_db":a.outage_threshold_db,
                    "ber_slope":1.0}}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
