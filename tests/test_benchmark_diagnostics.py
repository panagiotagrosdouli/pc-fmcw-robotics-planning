import numpy as np
import pandas as pd

from iscai.planning.dynamics import VehicleParams
from iscai.planning.feasibility import filter_with_diagnostics
from iscai.planning.trajectory import generate_candidates
from iscai.simulation.pc_fmcw_benchmark import (
    BenchmarkSettings,
    run_simulated_episode,
)
from iscai.simulation.scenario import following_lateral_offset
from scripts.diagnose_pc_fmcw_benchmark import diagnose


def test_candidate_feasibility_categories_are_exhaustive():
    target = np.column_stack([np.linspace(10.0, 20.0, 20), np.zeros(20)])
    candidates = generate_candidates(np.array([0.0, 0.0, 0.0, 8.0]), params=VehicleParams())
    _, counts = filter_with_diagnostics(
        candidates, target_xy=target, obstacles=[], target_clearance=2.0
    )
    assert counts["generated"] > 0
    assert counts["generated"] == sum(counts[key] for key in ("road", "speed", "static", "dynamic", "feasible"))


def test_episode_exports_auditable_safety_and_prediction_metrics():
    scenario = following_lateral_offset(steps=8, dt=0.1)
    row = run_simulated_episode(
        "P2", scenario, seed=4,
        settings=BenchmarkSettings(horizon_steps=5, p3_mc_samples=2),
    )
    assert row["candidate_evaluations"] == sum(
        row[key] for key in (
            "candidate_road_rejections", "candidate_speed_rejections",
            "candidate_static_rejections", "candidate_dynamic_rejections", "candidate_feasible",
        )
    )
    assert row["no_candidate_steps"] == row["zero_candidate_after_dynamic_steps"]
    assert row["prediction_ade_m"] >= 0.0
    assert row["prediction_fde_m"] >= 0.0


def test_diagnose_builds_per_scenario_outputs():
    scenario = following_lateral_offset(steps=7, dt=0.1)
    settings = BenchmarkSettings(horizon_steps=4, p3_mc_samples=2)
    rows = [run_simulated_episode(planner, scenario, seed=0, settings=settings) for planner in ("P0", "P1")]
    scenario_table, planner_table, causes = diagnose(pd.DataFrame(rows))
    assert len(scenario_table) == 2
    assert set(planner_table["planner"]) == {"P0", "P1"}
    assert np.allclose(causes["candidate_evaluations"], causes[
        ["candidate_road_rejections", "candidate_speed_rejections", "candidate_static_rejections",
         "candidate_dynamic_rejections", "candidate_feasible"]
    ].sum(axis=1))
