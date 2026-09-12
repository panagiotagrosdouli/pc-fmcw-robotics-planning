#!/usr/bin/env python3
"""Aggregate route-constrained real-V2X replay across grouped split seeds.

The split seeds reuse the same finite collection of measured drives under different
train/calibration/test assignments. They are therefore *not* independent statistical
replicates. This script intentionally performs descriptive robustness analysis only:
within-split run-level planner effects are computed first, then their direction/range is
summarized across split assignments. No Wilcoxon test or confidence interval is reported
across split seeds.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

METRICS = (
    "violation_fraction",
    "mean_measured_delay_ms",
    "mean_mobility_deviation",
    "unsupported_fraction",
)
COMPARISONS = (("P2", "P1"), ("P3", "P2"), ("P3", "P1"))


def seed_effects(seed_dir: Path, seed: int):
    d = pd.read_csv(seed_dir / "run_metrics.csv")
    rows = []
    for metric in METRICS:
        pivot = d.pivot(index="run_id", columns="mode", values=metric)
        for lhs, rhs in COMPARISONS:
            diff = (pivot[lhs] - pivot[rhs]).dropna().to_numpy(float)
            rows.append({
                "seed": seed,
                "metric": metric,
                "comparison": f"{lhs}-{rhs}",
                "n_test_runs": len(diff),
                "seed_mean_delta": float(np.mean(diff)) if len(diff) else np.nan,
                "seed_median_delta": float(np.median(diff)) if len(diff) else np.nan,
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/real_v2x_replay_multisplit")
    # Kept for backward-compatible workflow calls; no inferential bootstrap is performed.
    ap.add_argument("--bootstrap", type=int, default=0)
    args = ap.parse_args()
    root = Path(args.root)

    rows = []
    for seed_dir in sorted(root.glob("seed_*")):
        try:
            seed = int(seed_dir.name.split("_")[-1])
        except ValueError:
            continue
        if (seed_dir / "run_metrics.csv").exists():
            rows.extend(seed_effects(seed_dir, seed))
    if not rows:
        raise SystemExit(f"no seed_*/run_metrics.csv found under {root}")

    per_seed = pd.DataFrame(rows)
    per_seed.to_csv(root / "seed_effects.csv", index=False)

    summary = []
    for (metric, comparison), g in per_seed.groupby(["metric", "comparison"], sort=True):
        x = g.seed_mean_delta.dropna().to_numpy(float)
        if not len(x):
            continue
        # Negative is the desired direction for delay, threshold violations and
        # unsupported exposure. Mobility deviation is a cost, so positive means
        # more mobility cost rather than "favorable" performance.
        negative_fraction = float(np.mean(x < 0))
        positive_fraction = float(np.mean(x > 0))
        summary.append({
            "metric": metric,
            "comparison": comparison,
            "n_split_assignments": len(x),
            "mean_split_effect": float(np.mean(x)),
            "median_split_effect": float(np.median(x)),
            "min_split_effect": float(np.min(x)),
            "max_split_effect": float(np.max(x)),
            "fraction_splits_negative": negative_fraction,
            "fraction_splits_positive": positive_fraction,
            "all_splits_same_nonzero_direction": bool(np.all(x < 0) or np.all(x > 0)),
            "inference_status": "descriptive sensitivity only; split assignments reuse measured drives",
        })

    out = pd.DataFrame(summary)
    out.to_csv(root / "multisplit_summary.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
