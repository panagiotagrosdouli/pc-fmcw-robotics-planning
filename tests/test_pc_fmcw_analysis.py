import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

P = Path(__file__).resolve().parents[1] / "scripts" / "analyze_pc_fmcw_benchmark.py"
spec = importlib.util.spec_from_file_location("analysis", P)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def _frame():
    rows = []
    for seed in (0, 1):
        for scenario in ("a", "b"):
            for idx, planner in enumerate(("P0", "P1", "P2", "P3", "P4")):
                row = {"planner": planner, "scenario": scenario, "seed": seed, "duration_s": 5.0}
                for metric in analysis.METRICS:
                    row[metric] = float(idx + seed)
                rows.append(row)
    return pd.DataFrame(rows)


def test_analysis_preserves_seed_scenario_pairing():
    out = analysis.analyze(_frame(), bootstrap_samples=100)
    assert len(out) == len(analysis.PAIRINGS) * len(analysis.METRICS)
    assert set(out["n_pairs"]) == {4}
    p12 = out[(out.planner_a == "P1") & (out.planner_b == "P2")]
    assert (p12["mean_delta_b_minus_a"] == 1.0).all()


def test_analysis_rejects_duplicate_episode_keys():
    df = _frame()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate planner/scenario/seed"):
        analysis.analyze(df, bootstrap_samples=10)


def test_analysis_rejects_missing_required_planner():
    df = _frame()
    df = df[df.planner != "P4"]
    with pytest.raises(ValueError, match="missing planners required"):
        analysis.analyze(df, bootstrap_samples=10)


def test_analysis_rejects_nonfinite_non_ttc_metric():
    df = _frame()
    df.loc[(df.planner == "P2") & (df.scenario == "a") & (df.seed == 0), "mean_snr_db"] = np.nan
    with pytest.raises(ValueError, match="non-finite values"):
        analysis.analyze(df, bootstrap_samples=10)


def test_analysis_caps_positive_infinite_ttc_at_its_paired_episode_duration():
    df = _frame()
    pair_mask = (df.scenario == "a") & (df.seed == 0) & df.planner.isin(["P1", "P2"])
    df.loc[pair_mask, "duration_s"] = 3.0
    mask = (df.planner == "P2") & (df.scenario == "a") & (df.seed == 0)
    df.loc[mask, "min_realized_ttc_s"] = np.inf
    va, vb, n = analysis.paired_ttc_vectors(df, "P1", "P2")
    assert n == 4
    assert 3.0 in vb
    assert np.isinf(df.loc[mask, "min_realized_ttc_s"]).all()
    out = analysis.analyze(df, bootstrap_samples=10)
    ttc = out[(out.planner_a == "P1") & (out.planner_b == "P2") & (out.metric == "min_realized_ttc_s")]
    assert len(ttc) == 1
    assert np.isfinite(ttc.iloc[0]["mean_b"])


@pytest.mark.parametrize("invalid_ttc", [np.nan, -np.inf])
def test_analysis_rejects_invalid_ttc_values(invalid_ttc):
    df = _frame()
    mask = (df.planner == "P2") & (df.scenario == "a") & (df.seed == 0)
    df.loc[mask, "min_realized_ttc_s"] = invalid_ttc
    with pytest.raises(ValueError, match="invalid TTC values"):
        analysis.analyze(df, bootstrap_samples=10)


def test_analysis_rejects_paired_duration_mismatch():
    df = _frame()
    mask = (df.planner == "P2") & (df.scenario == "a") & (df.seed == 0)
    df.loc[mask, "duration_s"] = 4.0
    with pytest.raises(ValueError, match="paired duration_s mismatch"):
        analysis.analyze(df, bootstrap_samples=10)


@pytest.mark.parametrize("bad_duration", [0.0, -1.0, np.nan, np.inf])
def test_analysis_rejects_invalid_paired_durations(bad_duration):
    df = _frame()
    pair_mask = (df.scenario == "a") & (df.seed == 0) & df.planner.isin(["P1", "P2"])
    df.loc[pair_mask, "duration_s"] = bad_duration
    with pytest.raises(ValueError, match="paired duration_s values must be positive and finite"):
        analysis.analyze(df, bootstrap_samples=10)


def test_analysis_requires_duration_for_ttc_censoring():
    with pytest.raises(ValueError, match="duration_s is required"):
        analysis.analyze(_frame().drop(columns=["duration_s"]), bootstrap_samples=10)


def test_analysis_rejects_nonpositive_bootstrap_samples():
    with pytest.raises(ValueError, match="bootstrap_samples must be >= 1"):
        analysis.analyze(_frame(), bootstrap_samples=0)
