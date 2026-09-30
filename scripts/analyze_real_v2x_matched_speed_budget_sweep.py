#!/usr/bin/env python3
"""Aggregate fixed-budget matched-speed results across development configurations."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/real_v2x_matched_speed_w2s_balanced")
    args = ap.parse_args()
    root = Path(args.root)

    effects = []
    summaries = []
    for d in sorted(p for p in root.glob("seed_*_caliper_*") if p.is_dir()):
        parts = d.name.split("_")
        seed = int(parts[1])
        caliper = float(parts[3].replace("p", "."))
        epath = d / "budget_effects_development.csv"
        spath = d / "budget_summary.csv"
        if not epath.exists() or not spath.exists():
            continue
        e = pd.read_csv(epath)
        e["seed"] = seed
        e["caliper_m"] = caliper
        effects.append(e)
        s = pd.read_csv(spath)
        s["seed"] = seed
        s["caliper_m"] = caliper
        summaries.append(s)

    if not effects:
        raise RuntimeError("no budget results found")

    effects = pd.concat(effects, ignore_index=True)
    summaries = pd.concat(summaries, ignore_index=True)
    effects.to_csv(root / "budget_all_effects.csv", index=False)
    summaries.to_csv(root / "budget_all_summaries.csv", index=False)

    agg = effects.groupby(["budget", "comparison"]).agg(
        n_configs=("mean_delta_ms", "size"),
        mean_delta_ms=("mean_delta_ms", "mean"),
        min_delta_ms=("mean_delta_ms", "min"),
        max_delta_ms=("mean_delta_ms", "max"),
        favorable_configs=("mean_delta_ms", lambda x: int((x < 0).sum())),
        unfavorable_configs=("mean_delta_ms", lambda x: int((x > 0).sum())),
        zero_configs=("mean_delta_ms", lambda x: int((x == 0).sum())),
        median_query_runs=("n_query_runs", "median"),
    ).reset_index()
    agg.to_csv(root / "budget_robustness_summary.csv", index=False)

    policy = summaries.groupby(["budget", "mode"]).agg(
        n_configs=("mean_delay_ms", "size"),
        mean_delay_ms=("mean_delay_ms", "mean"),
        mean_p95_delay_ms=("mean_p95_delay_ms", "mean"),
        mean_slow_fraction=("mean_slow_fraction", "mean"),
        mean_gain_vs_fast_ms=("mean_gain_vs_fast_ms", "mean"),
    ).reset_index()
    policy.to_csv(root / "budget_policy_summary.csv", index=False)

    print("=== Budget robustness ===")
    print(agg.to_string(index=False))
    print("\n=== Policy operating points ===")
    print(policy.to_string(index=False))


if __name__ == "__main__":
    main()
