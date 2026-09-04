"""Create safety, feasibility, and prediction diagnostics from benchmark episodes."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DIAGNOSTIC_COLUMNS = {
    "collision_steps",
    "first_collision_step",
    "first_collision_time_s",
    "zero_candidate_after_static_steps",
    "zero_candidate_after_dynamic_steps",
    "candidate_evaluations",
    "candidate_road_rejections",
    "candidate_speed_rejections",
    "candidate_static_rejections",
    "candidate_dynamic_rejections",
    "candidate_feasible",
    "prediction_ade_m",
    "prediction_fde_m",
}


def diagnose(episodes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = {"scenario", "planner", "seed", "steps", "collision_indicator", "no_candidate_steps", *DIAGNOSTIC_COLUMNS}
    missing = required - set(episodes.columns)
    if missing:
        raise ValueError(f"benchmark episodes missing diagnostic columns: {sorted(missing)}")
    if episodes.duplicated(["scenario", "planner", "seed"]).any():
        raise ValueError("duplicate scenario/planner/seed rows are not allowed")

    work = episodes.copy()
    work["collision_fraction_of_steps"] = work["collision_steps"] / work["steps"].replace(0, np.nan)
    work["no_candidate_fraction"] = work["no_candidate_steps"] / work["steps"].replace(0, np.nan)
    work["dynamic_filter_zeroed_steps"] = (
        work["zero_candidate_after_dynamic_steps"] - work["zero_candidate_after_static_steps"]
    )
    if (work["dynamic_filter_zeroed_steps"] < 0).any():
        raise ValueError("zero-candidate stage counts are inconsistent")
    rejected = work[[
        "candidate_road_rejections", "candidate_speed_rejections",
        "candidate_static_rejections", "candidate_dynamic_rejections", "candidate_feasible",
    ]].sum(axis=1)
    if not np.array_equal(rejected.to_numpy(), work["candidate_evaluations"].to_numpy()):
        raise ValueError("candidate rejection counts do not sum to candidate_evaluations")
    if not np.array_equal(work["no_candidate_steps"].to_numpy(), work["zero_candidate_after_dynamic_steps"].to_numpy()):
        raise ValueError("planner no-candidate count disagrees with feasibility audit")

    scenario = work.groupby(["scenario", "planner"], as_index=False).agg(
        episodes=("seed", "size"),
        collision_rate=("collision_indicator", "mean"),
        mean_collision_steps=("collision_steps", "mean"),
        mean_first_collision_time_s=("first_collision_time_s", lambda x: float(np.mean(x[np.isfinite(x)])) if np.isfinite(x).any() else np.inf),
        mean_no_candidate_steps=("no_candidate_steps", "mean"),
        static_stage_zero_rate=("zero_candidate_after_static_steps", lambda x: float(np.sum(x) / work.loc[x.index, "steps"].sum())),
        dynamic_stage_zero_rate=("dynamic_filter_zeroed_steps", lambda x: float(np.sum(x) / work.loc[x.index, "steps"].sum())),
        prediction_ade_m=("prediction_ade_m", "mean"),
        prediction_fde_m=("prediction_fde_m", "mean"),
    )
    planner = work.groupby("planner", as_index=False).agg(
        episodes=("seed", "size"),
        collision_rate=("collision_indicator", "mean"),
        mean_no_candidate_steps=("no_candidate_steps", "mean"),
        prediction_ade_m=("prediction_ade_m", "mean"),
        prediction_fde_m=("prediction_fde_m", "mean"),
    )
    causes = work.groupby(["scenario", "planner"], as_index=False)[[
        "candidate_evaluations", "candidate_road_rejections", "candidate_speed_rejections",
        "candidate_static_rejections", "candidate_dynamic_rejections", "candidate_feasible",
    ]].sum()
    for column in [
        "candidate_road_rejections", "candidate_speed_rejections", "candidate_static_rejections",
        "candidate_dynamic_rejections", "candidate_feasible",
    ]:
        causes[f"{column}_fraction"] = causes[column] / causes["candidate_evaluations"]
    return scenario, planner, causes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/pc_fmcw_sim/episodes.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/pc_fmcw_sim/diagnostics"))
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"missing benchmark episodes: {args.input}")
    try:
        scenario, planner, causes = diagnose(pd.read_csv(args.input))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenario.to_csv(args.output_dir / "scenario_safety_prediction.csv", index=False)
    planner.to_csv(args.output_dir / "planner_safety_prediction.csv", index=False)
    causes.to_csv(args.output_dir / "candidate_rejection_causes.csv", index=False)
    print(scenario.to_string(index=False))


if __name__ == "__main__":
    main()
