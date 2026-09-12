#!/usr/bin/env python3
"""Build Paper 2 publication figures/tables from archived real-V2X summaries.

Accepts either the full extracted Actions artifact layout or the compact
`manuscripts/paper2_real_v2x/results_archive` snapshot committed for manuscript
reproducibility.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def save(fig, out: Path, stem: str):
    out.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def choose(root: Path, full: str, flat: str) -> Path:
    p = root / full
    if p.exists():
        return p
    p = root / flat
    if p.exists():
        return p
    raise FileNotFoundError(f"missing {full} or {flat} under {root}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact_root", type=Path)
    ap.add_argument("--out", type=Path, default=Path("manuscripts/paper2_real_v2x/generated"))
    args = ap.parse_args()
    root, out = args.artifact_root, args.out
    out.mkdir(parents=True, exist_ok=True)

    pred = pd.read_csv(choose(root, "real_v2x_support/predictor_metrics.csv", "predictor_metrics.csv"))
    delay = pred[pred["target"] == "delay_ms"].copy()
    fig, ax = plt.subplots(figsize=(4.3, 2.8))
    ax.bar(delay["model"].astype(str), delay["mae"].astype(float))
    ax.set_ylabel("Delay MAE (ms)")
    ax.set_xlabel("Predictor")
    ax.tick_params(axis="x", rotation=25)
    save(fig, out, "fig_predictor_mae")

    supp = pd.read_csv(choose(root, "real_v2x_support/support_stratified_metrics.csv", "support_stratified_metrics.csv"))
    mae_col = "mae_ms" if "mae_ms" in supp else [c for c in supp if "mae" in c.lower()][0]
    cov_col = "coverage" if "coverage" in supp else [c for c in supp if "coverage" in c.lower()][0]
    fig, ax = plt.subplots(figsize=(4.3, 2.8))
    ax.plot(supp["support_bin"].astype(str), supp[mae_col].astype(float), marker="o")
    ax.set_ylabel("Delay MAE (ms)")
    ax.set_xlabel("Nearest-training support bin")
    save(fig, out, "fig_support_mae")
    fig, ax = plt.subplots(figsize=(4.3, 2.8))
    ax.plot(supp["support_bin"].astype(str), supp[cov_col].astype(float), marker="o")
    ax.axhline(0.9, linestyle="--", linewidth=1)
    ax.set_ylabel("Empirical interval coverage")
    ax.set_xlabel("Nearest-training support bin")
    save(fig, out, "fig_support_coverage")

    multi = pd.read_csv(choose(root, "real_v2x_multisplit/multisplit_summary.csv", "multisplit_horizon_summary.csv"))
    dcol = "mean_delta_mae_ms" if "mean_delta_mae_ms" in multi else [c for c in multi if "delta" in c.lower() and "mae" in c.lower()][0]
    fig, ax = plt.subplots(figsize=(4.3, 2.8))
    ax.plot(multi["horizon_steps"], -multi[dcol].astype(float), marker="o")
    ax.axhline(0, linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Prediction horizon (steps, log scale)")
    ax.set_ylabel("Mean MAE improvement over persistence (ms)")
    save(fig, out, "fig_horizon_improvement")

    replay = pd.read_csv(choose(root, "real_v2x_replay/summary.csv", "replay_summary.csv"))
    pcol = "mode" if "mode" in replay else "planner"
    mdcol = "mean_delay_ms" if "mean_delay_ms" in replay else [c for c in replay if "delay" in c.lower()][0]
    fig, ax = plt.subplots(figsize=(4.3, 2.8))
    ax.bar(replay[pcol].astype(str), replay[mdcol].astype(float))
    ax.set_ylabel("Selected future measured delay (ms)")
    ax.set_xlabel("Planner")
    save(fig, out, "fig_replay_delay")

    pred.to_csv(out / "table_predictor_metrics.csv", index=False)
    supp.to_csv(out / "table_support_strata.csv", index=False)
    replay.to_csv(out / "table_replay_summary.csv", index=False)
    (out / "table_predictor_metrics.tex").write_text(pred.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))
    (out / "table_support_strata.tex").write_text(supp.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))
    (out / "table_replay_summary.tex").write_text(replay.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))

    effects_candidates = [root / "real_v2x_replay_multisplit" / "seed_effects.csv", root / "seed_effects.csv"]
    effects_path = next((p for p in effects_candidates if p.exists()), None)
    if effects_path is not None:
        effects = pd.read_csv(effects_path)
        effects.to_csv(out / "table_multisplit_seed_effects.csv", index=False)
        (out / "table_multisplit_seed_effects.tex").write_text(effects.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))


if __name__ == "__main__":
    main()
