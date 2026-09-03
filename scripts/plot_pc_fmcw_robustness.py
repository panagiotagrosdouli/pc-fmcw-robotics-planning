"""Generate paper-ready figures strictly from PC-FMCW simulation outputs.

When episode-level outputs are supplied, plotted means include deterministic
95% bootstrap confidence intervals over complete simulated episodes. Summary
CSV input remains supported for lightweight CI smoke tests, but does not imply
uncertainty estimates.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLANNER_ORDER = ["P0", "P1", "P2", "P3", "P4"]
METRIC_COLUMNS = {
    "outage": "mean_outage_probability",
    "progress_m": "progress_m",
    "collision_rate": "collision_indicator",
}


def _bootstrap_mean_ci(values, *, samples=2000, seed=0):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan, np.nan, np.nan
    mean = float(np.mean(values))
    if values.size == 1:
        return mean, mean, mean
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(samples, values.size))
    boot = values[indices].mean(axis=1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    return mean, float(lo), float(hi)


def _aggregate_episodes(episodes, *, bootstrap_samples, seed):
    required = {"sweep_parameter", "sweep_value", "planner", *METRIC_COLUMNS.values()}
    missing = required - set(episodes.columns)
    if missing:
        raise SystemExit(f"episode input missing columns: {sorted(missing)}")
    rows = []
    groups = episodes.groupby(["sweep_parameter", "sweep_value", "planner"], sort=True)
    for group_index, ((parameter, value, planner), frame) in enumerate(groups):
        row = {"sweep_parameter": parameter, "sweep_value": value, "planner": planner}
        for metric, column in METRIC_COLUMNS.items():
            mean, lo, hi = _bootstrap_mean_ci(
                frame[column].to_numpy(),
                samples=bootstrap_samples,
                seed=seed + group_index * 17 + list(METRIC_COLUMNS).index(metric),
            )
            row[metric] = mean
            row[f"{metric}_ci_low"] = lo
            row[f"{metric}_ci_high"] = hi
        rows.append(row)
    return pd.DataFrame(rows)


def _plot_metric(summary, parameter, metric, ylabel, output):
    subset = summary[summary["sweep_parameter"] == parameter]
    if subset.empty:
        raise ValueError(f"no rows for sweep parameter {parameter}")
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for planner in PLANNER_ORDER:
        p = subset[subset["planner"] == planner].sort_values("sweep_value")
        if p.empty:
            continue
        line = ax.plot(p["sweep_value"], p[metric], marker="o", label=planner)[0]
        lo_col, hi_col = f"{metric}_ci_low", f"{metric}_ci_high"
        if lo_col in p.columns and hi_col in p.columns:
            ax.fill_between(
                p["sweep_value"].to_numpy(float),
                p[lo_col].to_numpy(float),
                p[hi_col].to_numpy(float),
                alpha=0.15,
                color=line.get_color(),
            )
    ax.set_xlabel(parameter.replace("_", " "))
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=3)
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/pc_fmcw_robustness/summary.csv"))
    p.add_argument("--episodes", type=Path, default=None, help="Episode-level robustness CSV for 95% bootstrap confidence intervals")
    p.add_argument("--output-dir", type=Path, default=Path("results/pc_fmcw_robustness/figures"))
    p.add_argument("--bootstrap-samples", type=int, default=2000)
    p.add_argument("--bootstrap-seed", type=int, default=2026)
    args = p.parse_args()
    if args.bootstrap_samples < 1:
        raise SystemExit("--bootstrap-samples must be positive")
    if args.episodes is not None:
        episode_path = ROOT / args.episodes
        if not episode_path.exists():
            raise SystemExit(f"missing robustness episodes: {episode_path}")
        summary = _aggregate_episodes(
            pd.read_csv(episode_path),
            bootstrap_samples=args.bootstrap_samples,
            seed=args.bootstrap_seed,
        )
    else:
        inp = ROOT / args.input
        if not inp.exists():
            raise SystemExit(f"missing robustness summary: {inp}")
        summary = pd.read_csv(inp)
        required = {"sweep_parameter", "sweep_value", "planner", *METRIC_COLUMNS}
        missing = required - set(summary.columns)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    specs = [
        ("observation_sigma_m", "outage", "Mean outage probability", "outage_vs_observation_noise.png"),
        ("prediction_sigma_m", "outage", "Mean outage probability", "outage_vs_prediction_uncertainty.png"),
        ("horizon_steps", "outage", "Mean outage probability", "outage_vs_horizon.png"),
        ("connectivity_weight", "outage", "Mean outage probability", "outage_vs_connectivity_weight.png"),
        ("connectivity_weight", "progress_m", "Mean progress (m)", "progress_vs_connectivity_weight.png"),
        ("observation_sigma_m", "collision_rate", "Collision rate", "collision_vs_observation_noise.png"),
    ]
    for parameter, metric, ylabel, filename in specs:
        _plot_metric(summary, parameter, metric, ylabel, out / filename)
    print(f"wrote {len(specs)} figures to {out}")


if __name__ == "__main__":
    main()
