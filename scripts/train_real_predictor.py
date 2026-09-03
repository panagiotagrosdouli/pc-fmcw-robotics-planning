"""Train/evaluate a learned trajectory predictor on real CMHT tracklets.

This script uses an object-disjoint split, which prevents the same tracked
object from leaking across train and test sets.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_dataset import make_windows
from iscai.prediction.ml_baseline import HistoryGradientBoosting
from iscai.prediction.trajectory_metrics import ade, fde


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--history", type=int, default=8)
    p.add_argument("--horizon", type=int, default=12)
    p.add_argument("--test-fraction", type=float, default=0.2)
    p.add_argument("--output", type=Path, default=Path("results/learned_trajectory_prediction.csv"))
    args = p.parse_args()

    samples = make_windows(extract_object_positions(args.labels), args.history, args.horizon)
    ids = np.array([s["object_id"] for s in samples])
    unique = np.unique(ids)
    cut = max(1, int(round(len(unique) * (1 - args.test_fraction))))
    train_ids = set(unique[:cut])
    train = [s for s in samples if s["object_id"] in train_ids]
    test = [s for s in samples if s["object_id"] not in train_ids]
    if not train or not test:
        raise RuntimeError("Need at least two object IDs for an object-disjoint split")

    Xtr = np.stack([s["history"] for s in train])
    Ytr = np.stack([s["future"] for s in train])
    Xte = np.stack([s["history"] for s in test])
    Yte = np.stack([s["future"] for s in test])

    model = HistoryGradientBoosting().fit(Xtr, Ytr)
    pred = model.predict(Xte)
    metrics = pd.DataFrame([{"model": "history-gradient-boosting",
                             "ADE_m": ade(p, y), "FDE_m": fde(p, y)}
                            for p, y in zip(pred, Yte)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output, index=False)
    print(metrics[["ADE_m", "FDE_m"]].agg(["mean", "median", "count"]))
    print(f"train_windows={len(train)} test_windows={len(test)} saved={args.output}")


if __name__ == "__main__":
    main()
