"""Evaluate Transformer trajectory accuracy and uncertainty calibration on CMHT.

The script reconstructs the deterministic object-disjoint split used by
``train_transformer.py`` and evaluates only held-out object IDs. It reports ADE,
FDE, Gaussian NLL, 1-sigma/2-sigma coordinate coverage and predictive sharpness.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_dataset import make_windows
from iscai.prediction.trajectory_metrics import ade, fde
from iscai.prediction.transformer import TrajectoryTransformer
from iscai.prediction.uncertainty_metrics import gaussian_coverage, gaussian_nll_numpy, sharpness


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, default=Path("artifacts/trajectory_transformer.pt"))
    p.add_argument("--output", type=Path, default=Path("results/transformer_uncertainty.csv"))
    p.add_argument("--summary", type=Path, default=Path("results/transformer_uncertainty_summary.csv"))
    args = p.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu")
    history = int(ckpt["history"])
    horizon = int(ckpt["horizon"])

    rows = extract_object_positions(args.labels)
    samples = make_windows(rows, history, horizon)
    ids = np.unique([s["object_id"] for s in samples])
    if len(ids) < 2:
        raise RuntimeError("Need at least two object IDs for held-out evaluation")
    split = max(1, int(.8 * len(ids)))
    test_ids = set(ids[split:])
    test = [s for s in samples if s["object_id"] in test_ids]
    if not test:
        raise RuntimeError("Object-disjoint test split is empty")

    model = TrajectoryTransformer(horizon=horizon)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    records = []
    with torch.no_grad():
        for s in test:
            hist = torch.tensor(s["history"][None], dtype=torch.float32)
            mean_delta, log_sigma = model(hist)
            mean = s["history"][-1][None, :] + mean_delta[0].numpy()
            sigma = np.exp(log_sigma[0].numpy())
            truth = np.asarray(s["future"], dtype=float)
            records.append({
                "object_id": s["object_id"],
                "ADE_m": ade(mean, truth),
                "FDE_m": fde(mean, truth),
                "NLL": gaussian_nll_numpy(mean, sigma, truth),
                "coverage_1sigma": gaussian_coverage(mean, sigma, truth, 1.0),
                "coverage_2sigma": gaussian_coverage(mean, sigma, truth, 2.0),
                "sharpness_m": sharpness(sigma),
            })

    df = pd.DataFrame(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    summary = pd.DataFrame([{
        "n_windows": len(df),
        "n_test_objects": len(test_ids),
        "ADE_mean_m": df.ADE_m.mean(),
        "ADE_median_m": df.ADE_m.median(),
        "FDE_mean_m": df.FDE_m.mean(),
        "FDE_p95_m": np.percentile(df.FDE_m, 95),
        "NLL_mean": df.NLL.mean(),
        "coverage_1sigma": df.coverage_1sigma.mean(),
        "coverage_2sigma": df.coverage_2sigma.mean(),
        "sharpness_m": df.sharpness_m.mean(),
    }])
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary, index=False)
    print(summary.to_string(index=False))
    print(f"saved={args.output} summary={args.summary}")


if __name__ == "__main__":
    main()
