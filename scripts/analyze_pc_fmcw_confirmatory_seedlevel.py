#!/usr/bin/env python3
"""Predeclared seed-level confirmatory analysis for Part-B final-v1.

Each simulation seed contains repeated scenario conditions. The independent inferential
unit is therefore the seed, not the individual scenario row. For every planner comparison
and endpoint this script computes paired episode differences, averages them over scenarios
within each seed, and performs bootstrap/Wilcoxon inference over the resulting seed-level
effects.
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

COMPARISONS = (("P1", "P2"), ("P2", "P3"), ("P2", "P4"))
METRICS = (
    "mean_outage_probability",
    "mean_snr_db",
    "min_snr_db",
    "mean_ber_model",
    "mean_goodput_bps_model",
)


def bootstrap_mean(x, samples=100000, seed=2026):
    x = np.asarray(x, float)
    if x.ndim != 1 or len(x) == 0:
        raise ValueError("x must be a non-empty 1D effect vector")
    rng = np.random.default_rng(seed)
    # Chunk to avoid allocating samples x n_seed arrays unnecessarily.
    chunk = 10000
    vals = []
    remaining = samples
    while remaining:
        n = min(chunk, remaining)
        idx = rng.integers(0, len(x), size=(n, len(x)))
        vals.append(x[idx].mean(axis=1))
        remaining -= n
    boot = np.concatenate(vals)
    return float(np.mean(x)), float(np.quantile(boot, .025)), float(np.quantile(boot, .975))


def signed_wilcoxon(x):
    x = np.asarray(x, float)
    if np.allclose(x, 0.0):
        return 1.0
    try:
        return float(wilcoxon(x, alternative="two-sided", zero_method="wilcox").pvalue)
    except ValueError:
        return 1.0


def seed_effects(df, planner_a, planner_b, metric):
    keys = ["scenario", "seed"]
    left = df[df.planner == planner_a][keys + [metric]].rename(columns={metric: "a"})
    right = df[df.planner == planner_b][keys + [metric]].rename(columns={metric: "b"})
    paired = left.merge(right, on=keys, how="inner", validate="one_to_one")
    if paired.empty:
        raise ValueError(f"no pairs for {planner_a} vs {planner_b}, {metric}")
    paired["delta"] = paired.b.astype(float) - paired.a.astype(float)
    # One effect per independent simulation seed; scenario is a repeated condition.
    by_seed = paired.groupby("seed", sort=True).agg(
        seed_delta=("delta", "mean"),
        n_scenarios=("scenario", "nunique"),
    )
    if by_seed.n_scenarios.nunique() != 1:
        raise ValueError("unequal scenario coverage across seeds in confirmatory analysis")
    return by_seed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/part_b_final/episodes.csv")
    ap.add_argument("--output-dir", default="results/part_b_final")
    ap.add_argument("--bootstrap-samples", type=int, default=100000)
    args = ap.parse_args()
    if args.bootstrap_samples < 1:
        raise SystemExit("--bootstrap-samples must be >= 1")

    df = pd.read_csv(args.input)
    required = {"planner", "scenario", "seed", *METRICS}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"missing columns: {sorted(missing)}")
    if df.duplicated(["planner", "scenario", "seed"]).any():
        raise SystemExit("duplicate planner/scenario/seed rows")

    rows = []
    seed_rows = []
    for a, b in COMPARISONS:
        for metric in METRICS:
            se = seed_effects(df, a, b, metric)
            x = se.seed_delta.to_numpy(float)
            mean, lo, hi = bootstrap_mean(x, args.bootstrap_samples)
            p = signed_wilcoxon(x)
            rows.append({
                "planner_a": a,
                "planner_b": b,
                "comparison": f"{b}-{a}",
                "metric": metric,
                "n_independent_seeds": len(x),
                "scenarios_per_seed": int(se.n_scenarios.iloc[0]),
                "mean_seed_delta_b_minus_a": mean,
                "ci95_low": lo,
                "ci95_high": hi,
                "wilcoxon_p": p,
            })
            for seed_id, r in se.iterrows():
                seed_rows.append({
                    "planner_a": a,
                    "planner_b": b,
                    "comparison": f"{b}-{a}",
                    "metric": metric,
                    "seed": int(seed_id),
                    "seed_delta_b_minus_a": float(r.seed_delta),
                    "n_scenarios": int(r.n_scenarios),
                })

    out = pd.DataFrame(rows)
    # Exactly the predeclared primary family: 3 comparisons x 5 communication metrics.
    out["holm_p"] = holm_adjust(out.wilcoxon_p.to_numpy(float))
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out.to_csv(outdir / "confirmatory_seed_level_effects.csv", index=False)
    pd.DataFrame(seed_rows).to_csv(outdir / "confirmatory_seed_level_deltas.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
