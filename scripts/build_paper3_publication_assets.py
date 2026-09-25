#!/usr/bin/env python3
"""Generate Paper 3 publication figures and LaTeX tables from frozen compact evidence."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLANNER_ORDER = ["C0", "C1", "C2", "C3", "C4"]
MECH_PLANNERS = ["C1", "C2", "C3"]


def _fmt_p(value: float) -> str:
    if value < 1e-3:
        s = f"{value:.2e}"
        mantissa, exponent = s.split("e")
        exp = int(exponent)
        return "$" + mantissa + rf"\times 10^{{{exp}}}$"
    return f"{value:.5f}".rstrip("0").rstrip(".")


def _write_planner_table(df: pd.DataFrame, out: Path) -> None:
    d = df.set_index("planner").loc[PLANNER_ORDER].reset_index()
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Planner & Regret & Probe frac. & Param. error & Outage\\",
        r"\midrule",
    ]
    for row in d.itertuples(index=False):
        lines.append(
            f"{row.planner} & {row.mean_regret:.6f} & {row.mean_probe_fraction:.6f} & "
            f"{row.mean_parameter_error:.6f} & {row.mean_outage:.6f}" + r"\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    out.write_text("\n".join(lines), encoding="utf-8")


def _write_regret_table(df: pd.DataFrame, out: Path) -> None:
    lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Comparison & Delta & 95\% CI & Holm $p$\\",
        r"\midrule",
    ]
    for row in df.itertuples(index=False):
        ci = f"[{row.ci95_low:.6f},{row.ci95_high:.6f}]"
        lines.append(
            f"{row.comparison} & {row.mean_delta_b_minus_a:+.6f} & {ci} & "
            f"{_fmt_p(float(row.holm_p))}" + r"\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    out.write_text("\n".join(lines), encoding="utf-8")


def _annotate_bars(ax, bars, fmt: str = ".3g") -> None:
    for bar in bars:
        value = float(bar.get_height())
        ax.annotate(
            format(value, fmt),
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7,
        )


def _overall_figure(summary: pd.DataFrame, out: Path) -> None:
    d = summary.set_index("planner").loc[PLANNER_ORDER].reset_index()
    x = np.arange(len(d))
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))

    bars = axes[0].bar(x, d["mean_regret"].to_numpy(float))
    axes[0].set_xticks(x, d["planner"])
    axes[0].set_ylabel("Mean cumulative decision regret")
    axes[0].set_xlabel("Planner")
    axes[0].grid(axis="y", alpha=0.25)
    _annotate_bars(axes[0], bars)

    bars = axes[1].bar(x, d["mean_probe_fraction"].to_numpy(float))
    axes[1].set_xticks(x, d["planner"])
    axes[1].set_ylabel("Mean probe fraction")
    axes[1].set_xlabel("Planner")
    axes[1].grid(axis="y", alpha=0.25)
    _annotate_bars(axes[1], bars)

    fig.tight_layout()
    fig.savefig(out / "fig_overall.pdf", bbox_inches="tight")
    fig.savefig(out / "fig_overall.svg", bbox_inches="tight")
    plt.close(fig)


def _mechanism_figure(ef: pd.DataFrame, out: Path) -> None:
    scenario_map = {
        "E_decision_irrelevant_uncertainty": "E: decision-irrelevant",
        "F_decision_critical_uncertainty": "F: decision-critical",
    }
    scenarios = list(scenario_map)
    x = np.arange(len(scenarios))
    width = 0.24
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))

    for i, planner in enumerate(MECH_PLANNERS):
        vals = []
        probes = []
        for scenario in scenarios:
            row = ef[(ef["scenario"] == scenario) & (ef["planner"] == planner)].iloc[0]
            vals.append(float(row["regret"]))
            probes.append(float(row["probe_fraction"]))
        offset = (i - 1) * width
        bars = axes[0].bar(x + offset, vals, width, label=planner)
        _annotate_bars(axes[0], bars)
        axes[1].bar(x + offset, probes, width, label=planner)

    labels = [scenario_map[s] for s in scenarios]
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("Mean cumulative decision regret")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("Mean probe fraction")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8)

    fig.tight_layout()
    fig.savefig(out / "fig_decision_relevance.pdf", bbox_inches="tight")
    fig.savefig(out / "fig_decision_relevance.svg", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("manuscripts/paper3_active_self_calibration/results_archive"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("manuscripts/paper3_active_self_calibration/generated"),
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    summary = pd.read_csv(args.input / "confirmatory_planner_summary.csv")
    effects = pd.read_csv(args.input / "primary_regret_effects.csv")
    ef = pd.read_csv(args.input / "scenario_EF.csv")

    _write_planner_table(summary, args.out / "table_planner_means.tex")
    _write_regret_table(effects, args.out / "table_primary_regret_effects.tex")
    _overall_figure(summary, args.out)
    _mechanism_figure(ef, args.out)

    print(f"Wrote Paper 3 publication assets to {args.out}")


if __name__ == "__main__":
    main()
