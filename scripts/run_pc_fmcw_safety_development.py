#!/usr/bin/env python3
"""Development-only safety study for the PC-FMCW planner.

This script deliberately uses seeds 3000--3019, disjoint from both the historical
and confirmatory ranges.  It exists to test safety-envelope changes before any
new confirmatory seed range is frozen.  Do not report its connectivity effects
as confirmatory evidence.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings, run_benchmark


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed-start", type=int, default=3000)
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--output-dir", type=Path, default=Path("results/pc_fmcw_safety_development"))
    a = p.parse_args()
    if a.seeds < 1:
        raise SystemExit("--seeds must be >= 1")
    settings = BenchmarkSettings(
        dt=0.1, history_steps=8, horizon_steps=20,
        observation_sigma_m=0.20, prediction_sigma_m=0.75,
        connectivity_weight=1.0, p3_mc_samples=32,
        collision_distance_m=2.0,
    )
    df = pd.DataFrame(run_benchmark(range(a.seed_start, a.seed_start + a.seeds), settings=settings))
    out = ROOT / a.output_dir
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "episodes.csv", index=False)
    summary = df.groupby(["scenario", "planner"], as_index=False).agg(
        episodes=("seed", "size"),
        collision_rate=("collision_indicator", "mean"),
        min_target_distance_m=("min_target_distance_m", "min"),
        mean_no_candidate_steps=("no_candidate_steps", "mean"),
        max_no_candidate_steps=("no_candidate_steps", "max"),
        mean_outage_probability=("mean_outage_probability", "mean"),
        mean_snr_db=("mean_snr_db", "mean"),
    )
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))
    unsafe = summary[(summary.collision_rate > 0.0) | (summary.max_no_candidate_steps > 0)]
    if len(unsafe):
        print("\nDEVELOPMENT SAFETY GATE: FAIL")
        print(unsafe[["scenario", "planner", "collision_rate", "max_no_candidate_steps"]].to_string(index=False))
        raise SystemExit(2)
    print("\nDEVELOPMENT SAFETY GATE: PASS")


if __name__ == "__main__":
    main()
