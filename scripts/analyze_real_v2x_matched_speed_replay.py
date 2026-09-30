#!/usr/bin/env python3
"""Descriptive run-level analysis for matched field speed replay.

The donor library is shared across query runs, so ordinary query-run p-values would
understate dependence. This script reports paired run effects and bootstrap intervals
as development diagnostics only. A paper-level confirmatory analysis must resample both
query and donor runs or use an explicitly cross-fitted multiway-cluster procedure.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def bootstrap_mean(x: np.ndarray, n_boot: int, seed: int):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, float)
    for i in range(n_boot):
        draws[i] = rng.choice(x, size=len(x), replace=True).mean()
    return float(x.mean()), float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/real_v2x_matched_speed")
    ap.add_argument("--bootstrap", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    root = Path(args.input)
    d = pd.read_csv(root / "run_metrics.csv")
    rows = []

    metrics = [
        "mean_matched_delay_ms",
        "p95_matched_delay_ms",
        "mean_mobility_cost",
        "changed_from_fast_fraction",
    ]
    comparisons = [
        ("PRED", "FAST"),
        ("PRED_SUPPORT", "FAST"),
        ("SLOW", "FAST"),
        ("ORACLE_MATCHED", "FAST"),
    ]

    for metric in metrics:
        pivot = d.pivot(index="query_run_id", columns="mode", values=metric)
        for lhs, rhs in comparisons:
            if lhs not in pivot or rhs not in pivot:
                continue
            delta = (pivot[lhs] - pivot[rhs]).dropna().to_numpy(float)
            if len(delta) == 0:
                continue
            mean, lo, hi = bootstrap_mean(delta, args.bootstrap, args.seed)
            rows.append({
                "metric": metric,
                "comparison": f"{lhs}-{rhs}",
                "n_query_runs": len(delta),
                "mean_delta": mean,
                "bootstrap95_lo": lo,
                "bootstrap95_hi": hi,
                "inference_status": (
                    "development descriptive only; donor-run dependence not accounted for"
                ),
            })

    out = pd.DataFrame(rows)
    out.to_csv(root / "paired_effects_development.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
