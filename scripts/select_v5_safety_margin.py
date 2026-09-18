#!/usr/bin/env python3
"""Apply the frozen V5 development-only safety rule to complete margin runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

MARGINS = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
SEEDS = set(range(12000, 12020))
PLANNERS = {"P0", "P1", "P2", "P3", "P4"}
SCENARIOS = {"following_lateral_offset", "intersection_turn", "lane_choice", "occluding_cut_in", "overtake"}


def select(inputs: list[Path], output_dir: Path) -> float | None:
    if len(inputs) != len(MARGINS):
        raise ValueError(f"expected {len(MARGINS)} margin artifacts; found {len(inputs)}")
    rows = []
    for path in inputs:
        df = pd.read_csv(path)
        required = {"seed", "scenario", "planner", "planning_safety_margin_m",
                    "collision_indicator", "no_candidate_steps", "static_clearance_violation_indicator",
                    "min_target_distance_m", "min_static_obstacle_clearance_m"}
        if required - set(df):
            raise ValueError(f"{path}: missing {sorted(required - set(df))}")
        if len(df) != 500 or set(df.seed) != SEEDS or set(df.planner) != PLANNERS or set(df.scenario) != SCENARIOS:
            raise ValueError(f"{path}: incorrect cardinality, seed set, planners or scenarios")
        if df.duplicated(["seed", "scenario", "planner"]).any():
            raise ValueError(f"{path}: duplicate paired episode")
        if df.planning_safety_margin_m.nunique() != 1:
            raise ValueError(f"{path}: mixed margins")
        margin = float(df.planning_safety_margin_m.iloc[0])
        rows.append({
            "margin_m": margin,
            "episodes": len(df),
            "target_collision_episodes": int(df.collision_indicator.sum()),
            "no_candidate_episodes": int((df.no_candidate_steps > 0).sum()),
            "static_clearance_violation_episodes": int(df.static_clearance_violation_indicator.sum()),
            "minimum_target_separation_m": float(df.min_target_distance_m.min()),
            "minimum_static_surface_clearance_m": float(df.min_static_obstacle_clearance_m.min()),
        })
    summary = pd.DataFrame(rows).sort_values("margin_m")
    if summary.margin_m.tolist() != list(MARGINS):
        raise ValueError("incorrect predeclared margins")
    summary["passes"] = (
        (summary.target_collision_episodes == 0)
        & (summary.no_candidate_episodes == 0)
        & (summary.static_clearance_violation_episodes == 0)
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / "development_safety_summary.csv", index=False)
    passing = summary.loc[summary.passes, "margin_m"]
    selected = float(passing.min()) if len(passing) else None
    (output_dir / "selection.json").write_text(json.dumps({"selected_margin_m": selected,
        "gate_passes": selected is not None, "confirmatory_seeds_used": False}, indent=2) + "\n")
    print(summary.to_string(index=False))
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    inputs = sorted(args.input_dir.glob("v5_margin_*/episodes.csv"))
    selected = select(inputs, args.output_dir)
    if selected is None:
        raise SystemExit("V5 SAFETY GATE FAILED: no margin selected; confirmation prohibited")
    print(f"FROZEN V5 MARGIN={selected:.1f} m")


if __name__ == "__main__":
    main()
