"""Paired statistical analysis for the dataset-free PC-FMCW robotics benchmark."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.evaluation.statistics import paired_bootstrap_delta, paired_wilcoxon, holm_adjust

PAIRINGS = (("P1", "P2"), ("P2", "P3"), ("P0", "P2"), ("P2", "P4"))
METRICS = (
    "mean_outage_probability",
    "mean_snr_db",
    "mean_ber_model",
    "mean_goodput_bps_model",
    "path_length_m",
    "progress_m",
    "min_target_distance_m",
    "min_realized_ttc_s",
    "collision_indicator",
    "no_candidate_steps",
)


def _paired_rows(df, a, b, columns):
    keys = ["scenario", "seed"]
    left = df[df.planner == a][keys + columns].rename(columns={c: f"{c}_a" for c in columns})
    right = df[df.planner == b][keys + columns].rename(columns={c: f"{c}_b" for c in columns})
    merged = left.merge(right, on=keys, how="inner", validate="one_to_one")
    expected = df[df.planner == a][keys].drop_duplicates().merge(
        df[df.planner == b][keys].drop_duplicates(), on=keys, how="inner"
    )
    if len(merged) != len(expected):
        raise ValueError(f"incomplete pairing for {a} vs {b}")
    if len(merged) == 0:
        raise ValueError(f"no paired episodes for {a} vs {b}")
    return merged


def paired_vectors(df, a, b, metric):
    merged = _paired_rows(df, a, b, [metric])
    return merged[f"{metric}_a"].to_numpy(float), merged[f"{metric}_b"].to_numpy(float), len(merged)


def paired_ttc_vectors(df, a, b):
    if "duration_s" not in df.columns:
        raise ValueError("duration_s is required for TTC censoring")
    merged = _paired_rows(df, a, b, ["min_realized_ttc_s", "duration_s"])
    va = merged["min_realized_ttc_s_a"].to_numpy(float)
    vb = merged["min_realized_ttc_s_b"].to_numpy(float)
    da = merged["duration_s_a"].to_numpy(float)
    db = merged["duration_s_b"].to_numpy(float)
    if (np.isnan(va) | np.isneginf(va)).any() or (np.isnan(vb) | np.isneginf(vb)).any():
        raise ValueError(f"invalid TTC values for {a} vs {b}: only finite values or +inf are allowed")
    if not (np.all(np.isfinite(da)) and np.all(np.isfinite(db))) or np.any(da <= 0.0) or np.any(db <= 0.0):
        raise ValueError("paired duration_s values must be positive and finite")
    if not np.allclose(da, db, rtol=0.0, atol=1e-12):
        raise ValueError(f"paired duration_s mismatch for {a} vs {b}")
    va = np.where(np.isposinf(va), da, va)
    vb = np.where(np.isposinf(vb), db, vb)
    return va, vb, len(merged)


def analyze(df, bootstrap_samples=5000):
    if bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be >= 1")
    required = {"planner", "scenario", "seed", *METRICS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    duplicate_keys = df.duplicated(["planner", "scenario", "seed"], keep=False)
    if duplicate_keys.any():
        raise ValueError("duplicate planner/scenario/seed episode rows are not allowed")
    expected_planners = {planner for pair in PAIRINGS for planner in pair}
    missing_planners = expected_planners - set(df["planner"].astype(str))
    if missing_planners:
        raise ValueError(f"missing planners required for paired analysis: {sorted(missing_planners)}")
    rows = []
    for a, b in PAIRINGS:
        for metric in METRICS:
            if metric == "min_realized_ttc_s":
                va, vb, n = paired_ttc_vectors(df, a, b)
            else:
                va, vb, n = paired_vectors(df, a, b, metric)
            if not (np.all(np.isfinite(va)) and np.all(np.isfinite(vb))):
                raise ValueError(f"non-finite values for {a} vs {b}, metric={metric}")
            boot = paired_bootstrap_delta(va, vb, samples=bootstrap_samples, rng=7)
            wil = paired_wilcoxon(va, vb)
            rows.append({
                "planner_a": a,
                "planner_b": b,
                "metric": metric,
                "n_pairs": n,
                "mean_a": float(np.mean(va)),
                "mean_b": float(np.mean(vb)),
                "mean_delta_b_minus_a": boot["mean_delta"],
                "ci95_low": boot["ci_low"],
                "ci95_high": boot["ci_high"],
                "wilcoxon_p": wil["pvalue"],
            })
    out = pd.DataFrame(rows)
    out["holm_p"] = holm_adjust(out["wilcoxon_p"].to_numpy(float))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/pc_fmcw_sim/episodes.csv"))
    p.add_argument("--output-dir", type=Path, default=Path("results/pc_fmcw_sim"))
    p.add_argument("--bootstrap-samples", type=int, default=5000)
    args = p.parse_args()
    if args.bootstrap_samples < 1:
        raise SystemExit("--bootstrap-samples must be >= 1")
    inp = ROOT / args.input
    outdir = ROOT / args.output_dir
    if not inp.exists():
        raise SystemExit(f"missing benchmark CSV: {inp}")
    df = pd.read_csv(inp)
    outdir.mkdir(parents=True, exist_ok=True)
    effects = analyze(df, args.bootstrap_samples)
    effects.to_csv(outdir / "paired_effects.csv", index=False)
    scenario_summary = df.groupby(["scenario", "planner"], as_index=False).agg(
        episodes=("seed", "size"),
        outage=("mean_outage_probability", "mean"),
        snr_db=("mean_snr_db", "mean"),
        path_length_m=("path_length_m", "mean"),
        progress_m=("progress_m", "mean"),
        min_realized_ttc_s=("min_realized_ttc_s", "mean"),
        collision_rate=("collision_indicator", "mean"),
        no_candidate_steps=("no_candidate_steps", "mean"),
    )
    scenario_summary.to_csv(outdir / "scenario_summary.csv", index=False)
    print(effects.to_string(index=False))


if __name__ == "__main__":
    main()
