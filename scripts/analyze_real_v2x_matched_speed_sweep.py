#!/usr/bin/env python3
"""Aggregate matched-speed development sweeps across split seeds and spatial calipers."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/real_v2x_matched_speed_sweep")
    args = ap.parse_args()

    root = Path(args.root)
    summaries = []
    effects = []
    for d in sorted(p for p in root.glob("seed_*_caliper_*") if p.is_dir()):
        parts = d.name.split("_")
        seed = int(parts[1])
        caliper = float(parts[3].replace("p", "."))
        s = pd.read_csv(d / "summary.csv")
        s["seed"] = seed
        s["caliper_m"] = caliper
        summaries.append(s)
        e = pd.read_csv(d / "paired_effects_development.csv")
        e["seed"] = seed
        e["caliper_m"] = caliper
        effects.append(e)

    if not summaries:
        raise RuntimeError("no sweep outputs found")

    summaries = pd.concat(summaries, ignore_index=True)
    effects = pd.concat(effects, ignore_index=True)
    summaries.to_csv(root / "all_summaries.csv", index=False)
    effects.to_csv(root / "all_effects.csv", index=False)

    key = effects[
        effects["metric"].isin(["mean_matched_delay_ms", "p95_matched_delay_ms"])
        & effects["comparison"].isin(["PRED-FAST", "PRED_SUPPORT-FAST", "ORACLE_MATCHED-FAST"])
    ].copy()

    agg = key.groupby(["metric", "comparison"]).agg(
        n_configs=("mean_delta", "size"),
        mean_of_mean_delta=("mean_delta", "mean"),
        min_mean_delta=("mean_delta", "min"),
        max_mean_delta=("mean_delta", "max"),
        favorable_configs=("mean_delta", lambda x: int((x < 0).sum())),
        unfavorable_configs=("mean_delta", lambda x: int((x > 0).sum())),
        zero_configs=("mean_delta", lambda x: int((x == 0).sum())),
        median_query_runs=("n_query_runs", "median"),
    ).reset_index()
    agg.to_csv(root / "robustness_summary.csv", index=False)

    support = summaries.groupby(["seed", "caliper_m"]).agg(
        min_query_runs=("query_runs", "min"),
        max_query_runs=("query_runs", "max"),
        mean_nearest_donor_m=("mean_nearest_donor_m", "mean"),
        mean_donor_runs=("mean_donor_runs", "mean"),
    ).reset_index()
    support.to_csv(root / "support_summary.csv", index=False)

    print("=== Robustness summary ===")
    print(agg.to_string(index=False))
    print("\n=== Support summary ===")
    print(support.to_string(index=False))


if __name__ == "__main__":
    main()
