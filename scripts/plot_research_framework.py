#!/usr/bin/env python3
"""Generate publication figures directly from research-framework raw outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLANNER_ORDER = ["P0", "P1", "P2", "P3", "P4", "P2-CVaR", "P2-Chance", "P2-Adaptive", "P2-Worst"]


def _save(fig, output: Path, stem: str):
    fig.tight_layout()
    fig.savefig(output / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(output / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _ordered(frame):
    frame = frame.copy()
    frame["planner"] = pd.Categorical(frame["planner"], PLANNER_ORDER, ordered=True)
    return frame.sort_values("planner")


def plot_core_information_value(episodes, output):
    core = episodes[episodes["experiment"] == "core"]
    core = core[core["planner"].isin(["P1", "P2", "P3", "P4"])]
    if core.empty:
        return
    stats = core.groupby("planner")["mean_outage_probability"].agg(["mean", "sem"]).reset_index()
    stats = _ordered(stats)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    x = np.arange(len(stats))
    ax.errorbar(x, stats["mean"], yerr=1.96 * stats["sem"].fillna(0), marker="o", capsize=4)
    ax.set_xticks(x, stats["planner"].astype(str))
    ax.set_ylabel("Mean realized outage probability")
    ax.set_xlabel("Information level")
    ax.set_title("Value of future connectivity information")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output, "value_of_information")


def _horizon_value(setting_id):
    match = re.search(r"H=([0-9.]+)s", str(setting_id))
    return float(match.group(1)) if match else np.nan


def plot_horizon_saturation(episodes, output):
    data = episodes[episodes["experiment"] == "horizon"].copy()
    if data.empty:
        return
    data["horizon_s_plot"] = data["setting_id"].map(_horizon_value)
    stats = data.groupby(["planner", "horizon_s_plot"], as_index=False)["mean_outage_probability"].mean()
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for planner in ["P1", "P2", "P3", "P4", "P2-CVaR", "P2-Chance", "P2-Adaptive"]:
        sub = stats[stats["planner"] == planner].sort_values("horizon_s_plot")
        if not sub.empty:
            ax.plot(sub["horizon_s_plot"], sub["mean_outage_probability"], marker="o", label=planner)
    ax.set_xlabel("Prediction/planning horizon (s)")
    ax.set_ylabel("Mean realized outage probability")
    ax.set_title("Prediction-horizon saturation")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    _save(fig, output, "horizon_saturation")


def plot_reliability_mobility_pareto(episodes, output):
    data = episodes[episodes["experiment"] == "weight"].copy()
    if data.empty:
        return
    stats = data.groupby(["planner", "setting_id"], as_index=False).agg(
        outage=("mean_outage_probability", "mean"), progress=("progress_m", "mean")
    )
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for planner in ["P0", "P1", "P2", "P3", "P2-CVaR", "P2-Chance", "P2-Adaptive"]:
        sub = stats[stats["planner"] == planner]
        if not sub.empty:
            ax.scatter(sub["outage"], sub["progress"], label=planner, s=30)
    ax.set_xlabel("Mean realized outage probability (lower is better)")
    ax.set_ylabel("Progress (m, higher is better)")
    ax.set_title("Reliability–mobility operating frontier")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    _save(fig, output, "reliability_mobility_frontier")


def plot_shift_break_even(effects, output):
    if effects is None or effects.empty:
        return
    data = effects[
        (effects["experiment"] == "shift")
        & (effects["baseline"] == "P1")
        & (effects["candidate"] == "P2")
        & (effects["metric"] == "mean_outage_probability")
    ].copy()
    if data.empty:
        return
    data = data.sort_values("setting_id")
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(data))
    y = data["mean_delta"].to_numpy(float)
    lo = data["cluster_ci_low"].to_numpy(float)
    hi = data["cluster_ci_high"].to_numpy(float)
    ax.errorbar(x, y, yerr=np.vstack([y - lo, hi - y]), fmt="o", capsize=3)
    ax.axhline(0.0, linewidth=1)
    ax.set_xticks(x, data["setting_id"], rotation=65, ha="right", fontsize=7)
    ax.set_ylabel("P2 − P1 outage (seed-cluster 95% CI)")
    ax.set_title("Predictive-planning break-even under distribution shift")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output, "prediction_shift_break_even")


def plot_compute_frontier(episodes, output):
    data = episodes[episodes["experiment"] == "compute"]
    if data.empty:
        return
    stats = data.groupby(["planner", "setting_id"], as_index=False).agg(
        outage=("mean_outage_probability", "mean"), runtime=("mean_planning_time_s", "mean")
    )
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for planner in ["P2", "P3", "P2-CVaR", "P2-Chance", "P2-Worst"]:
        sub = stats[stats["planner"] == planner]
        if not sub.empty:
            ax.scatter(sub["runtime"], sub["outage"], s=28, label=planner)
    ax.set_xscale("log")
    ax.set_xlabel("Mean planning time per step (s, log scale)")
    ax.set_ylabel("Mean realized outage probability")
    ax.set_title("Compute–performance frontier")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    _save(fig, output, "compute_performance_frontier")


def plot_counterfactual_trajectory(trajectories, output):
    if trajectories is None or trajectories.empty:
        return
    core = trajectories[
        (trajectories["experiment"] == "core")
        & (trajectories["seed"] == trajectories["seed"].min())
        & (trajectories["planner"].isin(["P1", "P2", "P2-CVaR", "P2-Chance", "P2-Adaptive"]))
    ]
    if core.empty:
        return
    scenario = core["scenario"].iloc[0]
    core = core[core["scenario"] == scenario]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for planner, sub in core.groupby("planner"):
        sub = sub.sort_values("step")
        ax.plot(sub["ego_x_m"], sub["ego_y_m"], label=planner)
    target = core.sort_values("step").drop_duplicates("step")
    ax.plot(target["target_x_m"], target["target_y_m"], linestyle="--", label="target")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Matched counterfactual trajectories: {scenario}")
    ax.axis("equal")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    _save(fig, output, "counterfactual_trajectory")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", required=True)
    parser.add_argument("--effects")
    parser.add_argument("--trajectories")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    episodes = pd.read_csv(args.episodes)
    effects = pd.read_csv(args.effects) if args.effects and Path(args.effects).exists() else None
    trajectories = pd.read_csv(args.trajectories) if args.trajectories and Path(args.trajectories).exists() else None
    plot_core_information_value(episodes, output)
    plot_horizon_saturation(episodes, output)
    plot_reliability_mobility_pareto(episodes, output)
    plot_shift_break_even(effects, output)
    plot_compute_frontier(episodes, output)
    plot_counterfactual_trajectory(trajectories, output)
    print(f"wrote research figures to {output}")


if __name__ == "__main__":
    main()
