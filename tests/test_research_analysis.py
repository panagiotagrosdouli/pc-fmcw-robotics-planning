import pandas as pd

from iscai.evaluation.research_analysis import (
    feasibility_diagnostics,
    paired_effects,
    prediction_break_even,
    reliability_mobility_pareto,
)


def _rows(experiment="core", setting="nominal"):
    rows = []
    for scenario in ("a", "b"):
        for seed in (0, 1, 2):
            for planner, outage in (("P1", 0.10 + 0.01 * seed), ("P2", 0.08 + 0.01 * seed)):
                rows.append({
                    "experiment": experiment,
                    "setting_id": setting,
                    "scenario": scenario,
                    "seed": seed,
                    "planner": planner,
                    "mean_outage_probability": outage,
                    "mean_snr_db": 10.0 if planner == "P1" else 11.0,
                    "mean_goodput_bps_model": 1e8 if planner == "P1" else 1.1e8,
                    "progress_m": 20.0,
                    "collision_indicator": 0,
                    "no_candidate_steps": 1,
                    "mean_planning_time_s": 0.01 if planner == "P1" else 0.02,
                    "p95_planning_time_s": 0.02 if planner == "P1" else 0.03,
                    "candidate_evaluations": 100,
                    "candidate_road_rejections": 10,
                    "candidate_speed_rejections": 10,
                    "candidate_static_rejections": 10,
                    "candidate_dynamic_rejections": 10,
                    "candidate_feasible": 60,
                    "steps": 10,
                })
    return rows


def test_paired_effects_preserve_scenario_seed_pairing():
    frame = pd.DataFrame(_rows())
    effects = paired_effects(
        frame,
        comparisons=(("P1", "P2"),),
        metrics=("mean_outage_probability",),
        bootstrap_samples=200,
        rng=1,
    )
    row = effects.iloc[0]
    assert row["n_pairs"] == 6
    assert row["n_seed_clusters"] == 3
    assert row["mean_delta"] < 0.0


def test_break_even_flags_predictive_advantage():
    frame = pd.DataFrame(_rows("shift", "pred_noise=2"))
    effects = paired_effects(
        frame,
        comparisons=(("P1", "P2"),),
        metrics=("mean_outage_probability",),
        bootstrap_samples=200,
        rng=1,
    )
    result = prediction_break_even(effects)
    assert bool(result.iloc[0]["predictive_advantage"])


def test_feasibility_fractions_are_diagnostic_aggregates():
    result = feasibility_diagnostics(pd.DataFrame(_rows()))
    assert (result["feasible_candidate_fraction"] == 0.6).all()
    assert (result["no_candidate_step_fraction"] == 0.1).all()


def test_pareto_keeps_non_dominated_reliability_mobility_points():
    frame = pd.DataFrame(_rows())
    result = reliability_mobility_pareto(frame)
    assert result["pareto_efficient"].any()
