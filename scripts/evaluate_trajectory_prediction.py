"""Evaluate constant-velocity/acceleration prediction on CMHT annotations."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.prediction.trajectory_predictor import constant_acceleration, constant_velocity


def evaluate(df, history, horizon, dt, model):
    errors = []
    for oid, g in df.groupby("object_id"):
        g = g.sort_values("frame")
        xy = g[["x", "y"]].to_numpy(float)
        if len(xy) < history + horizon:
            continue
        for i in range(history, len(xy) - horizon + 1):
            hist = xy[i-history:i]
            true = xy[i:i+horizon]
            pred = model(hist, horizon, dt)
            errors.append(np.linalg.norm(pred - true, axis=1))
    if not errors:
        return None
    e = np.vstack(errors)
    return {"n_windows": len(e), "horizon_s": horizon * dt,
            "ade_m": float(e.mean()), "fde_m": float(e[:, -1].mean()),
            "p95_fde_m": float(np.percentile(e[:, -1], 95))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv", default="data/processed/cmht_trajectories.csv", nargs="?")
    p.add_argument("--history", type=int, default=10)
    p.add_argument("--horizon", type=int, default=10)
    p.add_argument("--dt", type=float, default=0.1)
    p.add_argument("--model", choices=["cv", "ca"], default="cv")
    args = p.parse_args()
    df = pd.read_csv(ROOT / args.csv)
    model = constant_velocity if args.model == "cv" else constant_acceleration
    result = evaluate(df, args.history, args.horizon, args.dt, model)
    if result is None:
        raise SystemExit("Not enough contiguous samples for the requested evaluation window.")
    print(result)


if __name__ == "__main__":
    main()
