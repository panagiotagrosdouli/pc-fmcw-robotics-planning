#!/usr/bin/env python3
"""Build publication tables from frozen research-framework outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PLANNER_ORDER = ["P0", "P1", "P2", "P3", "P4", "P2-CVaR", "P2-Chance", "P2-Adaptive", "P2-Worst"]
MAIN_METRICS = [
    "mean_outage_probability",
    "mean_snr_db",
    "mean_goodput_bps_model",
    "progress_m",
    "collision_indicator",
    "no_candidate_steps",
    "mean_planning_time_s",
]


def _write_latex(frame: pd.DataFrame, path: Path, float_format="%.4g"):
    path.write_text(frame.to_latex(index=False, escape=True, float_format=float_format))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", required=True)
    parser.add_argument("--effects", required=True)
    parser.add_argument("--scenario-effects", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    episodes = pd.read_csv(args.episodes)
    effects = pd.read_csv(args.effects)
    scenario_effects = pd.read_csv(args.scenario_effects)

    core = episodes[episodes["experiment"] == "core"].copy()
    if not core.empty:
        table = core.groupby("planner", as_index=False)[MAIN_METRICS].mean(numeric_only=True)
        table["planner"] = pd.Categorical(table["planner"], PLANNER_ORDER, ordered=True)
        table = table.sort_values("planner")
        table.to_csv(output / "main_planner_table.csv", index=False)
        _write_latex(table, output / "main_planner_table.tex")

    core_effects = effects[effects["experiment"] == "core"].copy()
    if not core_effects.empty:
        columns = [
            "baseline", "candidate", "metric", "n_pairs", "mean_delta", "ci_low", "ci_high",
            "cluster_ci_low", "cluster_ci_high", "holm_pvalue",
        ]
        core_effects[columns].to_csv(output / "main_effects_table.csv", index=False)
        _write_latex(core_effects[columns], output / "main_effects_table.tex")

    core_scenario = scenario_effects[
        (scenario_effects["experiment"] == "core")
        & (scenario_effects["metric"] == "mean_outage_probability")
        & (
            ((scenario_effects["baseline"] == "P1") & (scenario_effects["candidate"] == "P2"))
            | ((scenario_effects["baseline"] == "P2") & (scenario_effects["candidate"] == "P4"))
        )
    ].copy()
    if not core_scenario.empty:
        columns = [
            "scenario", "baseline", "candidate", "n_pairs", "mean_delta", "ci_low", "ci_high",
            "cluster_ci_low", "cluster_ci_high", "scenario_family_holm_pvalue",
        ]
        core_scenario[columns].to_csv(output / "scenario_effects_table.csv", index=False)
        _write_latex(core_scenario[columns], output / "scenario_effects_table.tex")

    print(f"wrote paper tables to {output}")


if __name__ == "__main__":
    main()
