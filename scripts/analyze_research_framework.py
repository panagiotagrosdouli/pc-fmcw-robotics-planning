#!/usr/bin/env python3
"""Analyze research-framework experiments into publication-ready statistical tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from iscai.evaluation.research_analysis import (
    compute_frontier,
    feasibility_diagnostics,
    paired_effects,
    prediction_break_even,
    reliability_mobility_pareto,
    scenario_paired_effects,
    value_of_information,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="episodes.csv from run_research_framework.py")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--rng-seed", type=int, default=2026)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.bootstrap_samples < 1:
        raise SystemExit("--bootstrap-samples must be >= 1")
    frame = pd.read_csv(args.input)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    effects = paired_effects(frame, bootstrap_samples=args.bootstrap_samples, rng=args.rng_seed)
    scenario = scenario_paired_effects(frame, bootstrap_samples=args.bootstrap_samples, rng=args.rng_seed)
    voi = value_of_information(frame)
    pareto = reliability_mobility_pareto(frame)
    compute = compute_frontier(frame)
    feasibility = feasibility_diagnostics(frame)
    break_even = prediction_break_even(effects)

    effects.to_csv(output / "paired_effects.csv", index=False)
    scenario.to_csv(output / "scenario_paired_effects.csv", index=False)
    voi.to_csv(output / "value_of_information.csv", index=False)
    pareto.to_csv(output / "reliability_mobility_pareto.csv", index=False)
    compute.to_csv(output / "compute_frontier.csv", index=False)
    feasibility.to_csv(output / "feasibility_diagnostics.csv", index=False)
    break_even.to_csv(output / "prediction_break_even.csv", index=False)

    print(f"wrote research analysis tables to {output}")


if __name__ == "__main__":
    main()
