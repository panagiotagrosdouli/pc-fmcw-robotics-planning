"""Evaluate constant-velocity and constant-acceleration predictors on CMHT labels.

Usage:
  python scripts/evaluate_real_trajectories.py --labels data/raw/cmht/labels
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_metrics import ade, fde
from iscai.prediction.trajectory_dataset import make_windows


def cv(history, horizon):
    v = history[-1] - history[-2]
    return history[-1] + np.arange(1, horizon + 1)[:, None] * v


def ca(history, horizon):
    v1 = history[-1] - history[-2]
    v0 = history[-2] - history[-3]
    a = v1 - v0
    steps = np.arange(1, horizon + 1)[:, None]
    return history[-1] + steps * v1 + 0.5 * steps * (steps + 1) * a


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--history", type=int, default=8)
    parser.add_argument("--horizon", type=int, default=12)
    parser.add_argument("--output", type=Path, default=Path("results/real_trajectory_prediction.csv"))
    args = parser.parse_args()

    rows = extract_object_positions(args.labels)
    samples = make_windows(rows, args.history, args.horizon)
    records = []
    for s in samples:
        if len(s["history"]) < 3:
            continue
        for name, fn in (("CV", cv), ("CA", ca)):
            pred = fn(s["history"], len(s["future"]))
            records.append({"object_id": s["object_id"], "model": name,
                            "ADE_m": ade(pred, s["future"]),
                            "FDE_m": fde(pred, s["future"])})
    df = pd.DataFrame(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(df.groupby("model")[["ADE_m", "FDE_m"]].agg(["mean", "median", "count"]))
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
