"""Statistical analysis for the research-framework experiment matrix.

All confirmatory planner effects are paired by scenario and seed. Overall
confidence intervals are reported both at the declared scenario-seed unit and as
a seed-cluster sensitivity analysis. Candidate-level counts are never treated as
independent inferential samples.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from iscai.evaluation.statistics import (
    cluster_paired_bootstrap_delta,
    holm_adjust,
    paired_bootstrap_delta,
    paired_wilcoxon,
    pareto_mask,
)


DEFAULT_COMPARISONS = (
    ("P1", "P2"),
    ("P2", "P3"),
    ("P2", "P4"),
    ("P2", "P2-CVaR"),
    ("P2", "P2-Chance"),
    ("P2", "P2-Adaptive"),
    ("P2", "P2-Worst"),
)

DEFAULT_METRICS = (
    "mean_outage_probability",
    "mean_snr_db",
    "mean_goodput_bps_model",
    "progress_m",
    "collision_indicator",
    "no_candidate_steps",
    "mean_planning_time_s",
)


def _require_columns(frame: pd.DataFrame, columns):
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def _paired(frame: pd.DataFrame, baseline: str, candidate: str, metric: str):
    keys = ["experiment", "setting_id", "scenario", "seed"]
    subset = frame[frame["planner"].isin([baseline, candidate])]
    dup = subset.duplicated(keys + ["planner"], keep=False)
    if dup.any():
        raise ValueError("duplicate planner rows within paired experiment unit")
    pivot = subset.pivot(index=keys, columns="planner", values=metric)
    if baseline not in pivot or candidate not in pivot:
        return pd.DataFrame()
    return pivot[[baseline, candidate]].dropna().reset_index()


def paired_effects(
    frame: pd.DataFrame,
    comparisons=DEFAULT_COMPARISONS,
    metrics=DEFAULT_METRICS,
    *,
    bootstrap_samples=10000,
    rng=2026,
) -> pd.DataFrame:
    """Return paired effect estimates for every experiment setting.

    Deltas are candidate - baseline. A negative outage delta is therefore an
    improvement, while a positive SNR/goodput/progress delta is an improvement.
    """
    _require_columns(frame, ["experiment", "setting_id", "scenario", "seed", "planner", *metrics])
    rows = []
    for (experiment, setting_id), group in frame.groupby(["experiment", "setting_id"], sort=False):
        for baseline, candidate in comparisons:
            for metric in metrics:
                paired = _paired(group, baseline, candidate, metric)
                if paired.empty:
                    continue
                a = paired[baseline].to_numpy(float)
                b = paired[candidate].to_numpy(float)
                ordinary = paired_bootstrap_delta(a, b, samples=bootstrap_samples, rng=rng)
                clustered = cluster_paired_bootstrap_delta(
                    a, b, paired["seed"].to_numpy(), samples=bootstrap_samples, rng=rng
                )
                test = paired_wilcoxon(a, b)
                rows.append({
                    "experiment": experiment,
                    "setting_id": setting_id,
                    "baseline": baseline,
                    "candidate": candidate,
                    "metric": metric,
                    "n_pairs": int(len(paired)),
                    "n_seed_clusters": int(clustered["n_clusters"]),
                    "baseline_mean": float(np.mean(a)),
                    "candidate_mean": float(np.mean(b)),
                    "mean_delta": ordinary["mean_delta"],
                    "ci_low": ordinary["ci_low"],
                    "ci_high": ordinary["ci_high"],
                    "cluster_ci_low": clustered["ci_low"],
                    "cluster_ci_high": clustered["ci_high"],
                    "wilcoxon_statistic": test["statistic"],
                    "pvalue": test["pvalue"],
                })
    out = pd.DataFrame(rows)
    if not out.empty:
        # One multiplicity family per experiment family so sweeps do not silently
        # dilute or sharpen the nominal core comparison family after results exist.
        out["holm_pvalue"] = np.nan
        for experiment, idx in out.groupby("experiment").groups.items():
            out.loc[idx, "holm_pvalue"] = holm_adjust(out.loc[idx, "pvalue"].to_numpy(float))
    return out


def scenario_paired_effects(
    frame: pd.DataFrame,
    comparisons=DEFAULT_COMPARISONS,
    metrics=DEFAULT_METRICS,
    *,
    bootstrap_samples=10000,
    rng=2026,
) -> pd.DataFrame:
    """Scenario-stratified paired effects with seed as the paired unit."""
    rows = []
    for scenario, group in frame.groupby("scenario", sort=False):
        effects = paired_effects(
            group,
            comparisons=comparisons,
            metrics=metrics,
            bootstrap_samples=bootstrap_samples,
            rng=rng,
        )
        if not effects.empty:
            effects.insert(2, "scenario", scenario)
            rows.append(effects)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    # Correct across the complete scenario-level family within each experiment.
    out["scenario_family_holm_pvalue"] = np.nan
    for experiment, idx in out.groupby("experiment").groups.items():
        out.loc[idx, "scenario_family_holm_pvalue"] = holm_adjust(out.loc[idx, "pvalue"].to_numpy(float))
    return out


def value_of_information(frame: pd.DataFrame, metric="mean_outage_probability") -> pd.DataFrame:
    """Summarize the P1->P2->P3->P4 information ladder for nominal/core settings."""
    _require_columns(frame, ["experiment", "setting_id", "planner", metric])
    subset = frame[
        (frame["planner"].isin(["P1", "P2", "P3", "P4"]))
        & (frame["experiment"] == "core")
    ]
    if subset.empty:
        return pd.DataFrame()
    return (
        subset.groupby(["setting_id", "planner"], as_index=False)
        .agg(mean=(metric, "mean"), std=(metric, "std"), n=(metric, "size"))
    )


def reliability_mobility_pareto(frame: pd.DataFrame) -> pd.DataFrame:
    """Return Pareto-efficient planner/settings for outage vs negative progress."""
    _require_columns(frame, ["experiment", "setting_id", "planner", "mean_outage_probability", "progress_m"])
    grouped = (
        frame.groupby(["experiment", "setting_id", "planner"], as_index=False)
        .agg(outage=("mean_outage_probability", "mean"), progress=("progress_m", "mean"))
    )
    result = []
    for experiment, group in grouped.groupby("experiment", sort=False):
        values = np.column_stack([group["outage"].to_numpy(float), group["progress"].to_numpy(float)])
        group = group.copy()
        group["pareto_efficient"] = pareto_mask(values, minimize=[True, False])
        result.append(group)
    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()


def compute_frontier(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate reliability and compute cost without inventing a scalar utility."""
    _require_columns(frame, ["experiment", "setting_id", "planner", "mean_outage_probability", "mean_planning_time_s"])
    grouped = (
        frame.groupby(["experiment", "setting_id", "planner"], as_index=False)
        .agg(
            outage=("mean_outage_probability", "mean"),
            planning_time_s=("mean_planning_time_s", "mean"),
            p95_planning_time_s=("p95_planning_time_s", "mean"),
        )
    )
    result = []
    for experiment, group in grouped.groupby("experiment", sort=False):
        values = group[["outage", "planning_time_s"]].to_numpy(float)
        group = group.copy()
        group["pareto_efficient"] = pareto_mask(values, minimize=[True, True])
        result.append(group)
    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()


def prediction_break_even(effects: pd.DataFrame, metric="mean_outage_probability") -> pd.DataFrame:
    """Extract P1->P2 shift conditions and flag where predictive planning loses advantage."""
    if effects.empty:
        return pd.DataFrame()
    subset = effects[
        (effects["experiment"].isin(["shift", "blackout"]))
        & (effects["baseline"] == "P1")
        & (effects["candidate"] == "P2")
        & (effects["metric"] == metric)
    ].copy()
    if subset.empty:
        return subset
    subset["predictive_advantage"] = subset["mean_delta"] < 0.0
    subset["ci_supports_advantage"] = subset["ci_high"] < 0.0
    subset["cluster_ci_supports_advantage"] = subset["cluster_ci_high"] < 0.0
    return subset


def feasibility_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate diagnostic rejection fractions; these are not inferential samples."""
    columns = [
        "candidate_evaluations", "candidate_road_rejections", "candidate_speed_rejections",
        "candidate_static_rejections", "candidate_dynamic_rejections", "candidate_feasible",
        "no_candidate_steps", "steps",
    ]
    _require_columns(frame, ["experiment", "setting_id", "scenario", "planner", *columns])
    rows = []
    for keys, group in frame.groupby(["experiment", "setting_id", "scenario", "planner"], sort=False):
        total = float(group["candidate_evaluations"].sum())
        steps = float(group["steps"].sum())
        row = dict(zip(["experiment", "setting_id", "scenario", "planner"], keys))
        row["candidate_evaluations"] = int(total)
        for column, label in (
            ("candidate_road_rejections", "road_rejection_fraction"),
            ("candidate_speed_rejections", "speed_rejection_fraction"),
            ("candidate_static_rejections", "static_rejection_fraction"),
            ("candidate_dynamic_rejections", "dynamic_rejection_fraction"),
            ("candidate_feasible", "feasible_candidate_fraction"),
        ):
            row[label] = float(group[column].sum() / total) if total else np.nan
        row["no_candidate_step_fraction"] = float(group["no_candidate_steps"].sum() / steps) if steps else np.nan
        rows.append(row)
    return pd.DataFrame(rows)
