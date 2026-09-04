"""Aggregate the two confirmatory paper ablations with seed-level uncertainty.

The input is expected to contain one row per planner/seed (and, if applicable,
scenario) at each ablation setting.  Candidate/window rows must be aggregated to
that experimental unit before using this script.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def bootstrap_mean(values: np.ndarray, samples: int, rng: np.random.Generator) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise ValueError("bootstrap values must be non-empty and finite")
    draws = rng.choice(values, size=(samples, values.size), replace=True).mean(axis=1)
    return float(values.mean()), float(np.quantile(draws, .025)), float(np.quantile(draws, .975))


def summarize(df: pd.DataFrame, x: str, metric: str, samples: int) -> pd.DataFrame:
    required = {"planner", "seed", x, metric}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    keys = ["planner", "seed", x]
    if "scenario" in df.columns:
        keys.insert(2, "scenario")
    if df.duplicated(keys).any():
        raise ValueError(
            "input contains repeated experimental units; aggregate window/candidate rows before paper inference"
        )
    rows = []
    rng = np.random.default_rng(2026)
    for (planner, setting), frame in df.groupby(["planner", x], sort=True):
        mean, low, high = bootstrap_mean(frame[metric].to_numpy(float), samples, rng)
        rows.append({"planner": planner, x: setting, "metric": metric, "n_units": len(frame),
                     "mean": mean, "ci95_low": low, "ci95_high": high})
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--x", choices=["horizon_s", "connectivity_weight"], required=True)
    p.add_argument("--metric", default="outage_rate")
    p.add_argument("--bootstrap-samples", type=int, default=10000)
    a = p.parse_args()
    if a.bootstrap_samples < 1:
        raise SystemExit("--bootstrap-samples must be >= 1")
    df = pd.read_csv(a.input)
    out = summarize(df, a.x, a.metric, a.bootstrap_samples)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.output_dir / f"{a.x}_{a.metric}_effects.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
