"""Generate paper-ready figures strictly from PC-FMCW simulation outputs."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLANNER_ORDER = ["P0", "P1", "P2", "P3", "P4"]


def _plot_metric(summary, parameter, metric, ylabel, output):
    subset = summary[summary["sweep_parameter"] == parameter]
    if subset.empty:
        raise ValueError(f"no rows for sweep parameter {parameter}")
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for planner in PLANNER_ORDER:
        p = subset[subset["planner"] == planner].sort_values("sweep_value")
        if not p.empty:
            ax.plot(p["sweep_value"], p[metric], marker="o", label=planner)
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
    p.add_argument("--output-dir", type=Path, default=Path("results/pc_fmcw_robustness/figures"))
    args = p.parse_args()
    inp = ROOT / args.input
    if not inp.exists():
        raise SystemExit(f"missing robustness summary: {inp}")
    summary = pd.read_csv(inp)
    required = {"sweep_parameter", "sweep_value", "planner", "outage", "progress_m", "collision_rate"}
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
