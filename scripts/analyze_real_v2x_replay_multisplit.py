#!/usr/bin/env python3
"""Aggregate route-constrained real-V2X replay across grouped split seeds.

Each seed contributes run-level planner metrics from a fully disjoint train/cal/test split.
The aggregation first computes within-seed planner deltas and then summarizes those seed-level
effects. This avoids pretending that repeated timestamps or overlapping runs are independent.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.evaluation.statistics import holm_adjust

METRICS = (
    "violation_fraction",
    "mean_measured_delay_ms",
    "mean_mobility_deviation",
    "unsupported_fraction",
)
COMPARISONS = (("P2", "P1"), ("P3", "P2"), ("P3", "P1"))


def bootstrap_mean(x, n=10000, seed=2026):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.mean(x)), float(np.quantile(draws, .025)), float(np.quantile(draws, .975))


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
    ap.add_argument("--bootstrap", type=int, default=10000)
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
        mean, lo, hi = bootstrap_mean(x, args.bootstrap)
        try:
            p = float(wilcoxon(x).pvalue) if np.any(x != 0) else 1.0
        except ValueError:
            p = 1.0
        summary.append({
            "metric": metric,
            "comparison": comparison,
            "n_split_seeds": len(x),
            "mean_seed_effect": mean,
            "ci95_lo": lo,
            "ci95_hi": hi,
            "fraction_split_seeds_favorable": float(np.mean(x < 0)) if metric != "mean_mobility_deviation" else float(np.mean(x > 0)),
            "wilcoxon_p": p,
            "min_seed_effect": float(np.min(x)),
            "max_seed_effect": float(np.max(x)),
        })

    out = pd.DataFrame(summary)
    out["holm_p"] = holm_adjust(out["wilcoxon_p"].to_numpy(float))
    out.to_csv(root / "multisplit_summary.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
