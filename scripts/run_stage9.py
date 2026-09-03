"""Run the Stage 9 synthetic planner comparison.

Usage:
    python scripts/run_stage9.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.prediction.link_predictor import LinkPredictor
from iscai.planning.planners import (
    MobilityOnlyPlanner,
    ReactiveConnectivityPlanner,
    PredictiveConnectivityPlanner,
    OracleConnectivityPlanner,
)
from iscai.simulation.scenario import make_primary_scenarios
from iscai.simulation.runner import run_episode


def main():
    predictor = LinkPredictor(reference_snr_db=20.0, reference_distance=10.0, min_snr_db=8.0)
    scenarios = make_primary_scenarios()
    planners = [
        ("P0_mobility_only", MobilityOnlyPlanner()),
        ("P1_reactive", ReactiveConnectivityPlanner(predictor, connectivity_weight=1.0)),
        ("P2_predictive", PredictiveConnectivityPlanner(predictor, connectivity_weight=1.0)),
        ("P4_oracle", OracleConnectivityPlanner(predictor, connectivity_weight=1.0)),
    ]

    rows = []
    for scenario in scenarios:
        for name, planner in planners:
            result = run_episode(planner, scenario, planner_name=name)
            rows.append({
                "planner": result.planner,
                "scenario": result.scenario,
                "travel_time_s": result.travel_time,
                "path_length_m": result.path_length,
                "outage_fraction": result.outage_fraction,
                "link_lifetime_s": result.link_lifetime,
                "min_obstacle_distance_m": result.min_obstacle_distance,
            })

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "stage9_primary.csv", index=False)

    summary = df.groupby("planner", as_index=False).agg(
        outage_fraction=("outage_fraction", "mean"),
        link_lifetime_s=("link_lifetime_s", "mean"),
        travel_time_s=("travel_time_s", "mean"),
        path_length_m=("path_length_m", "mean"),
        min_obstacle_distance_m=("min_obstacle_distance_m", "min"),
    )
    summary.to_csv(out / "stage9_summary.csv", index=False)

    plt.figure(figsize=(7, 5))
    for planner in summary["planner"]:
        sub = df[df["planner"] == planner]
        plt.scatter(sub["travel_time_s"], sub["outage_fraction"], label=planner)
    plt.xlabel("Travel time (s)")
    plt.ylabel("Outage fraction")
    plt.title("Stage 9: mobility-connectivity trade-off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "stage9_outage_vs_travel_time.png", dpi=200)
    plt.close()

    print(summary.to_string(index=False))
    print(f"\nSaved results to: {out}")


if __name__ == "__main__":
    main()
