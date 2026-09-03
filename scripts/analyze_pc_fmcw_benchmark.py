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


def paired_vectors(df, a, b, metric):
    keys = ["scenario", "seed"]
    left = df[df.planner == a][keys + [metric]].rename(columns={metric: "a"})
    right = df[df.planner == b][keys + [metric]].rename(columns={metric: "b"})
    merged = left.merge(right, on=keys, how="inner", validate="one_to_one")
    expected = df[df.planner == a][keys].drop_duplicates().merge(
        df[df.planner == b][keys].drop_duplicates(), on=keys, how="inner"
    )
    if len(merged) != len(expected):
        raise ValueError(f"incomplete pairing for {a} vs {b}, metric={metric}")
    return merged["a"].to_numpy(float), merged["b"].to_numpy(float), len(merged)


def analyze(df, bootstrap_samples=5000):
    required = {"planner", "scenario", "seed", *METRICS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    rows = []
    for a, b in PAIRINGS:
        for metric in METRICS:
            va, vb, n = paired_vectors(df, a, b, metric)
            # Infinite TTC is the physically meaningful value for non-closing
            # trajectories, but finite statistical tests cannot operate on it.
            # Cap only for the inferential calculation at the episode duration;
            # the raw benchmark CSV retains +inf and therefore remains auditable.
            if metric == "min_realized_ttc_s":
                cap = float(df["duration_s"].max()) if "duration_s" in df else 1e6
                va = np.where(np.isfinite(va), va, cap)
                vb = np.where(np.isfinite(vb), vb, cap)
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
