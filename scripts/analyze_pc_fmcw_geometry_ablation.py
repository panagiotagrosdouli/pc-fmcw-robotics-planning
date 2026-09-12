#!/usr/bin/env python3
"""Analyze whether the predictive-vs-reactive effect depends on angular link geometry.

Scenarios are repeated within each simulation seed. To avoid treating those scenario rows
as independent replicates, the P2-P1 episode effects are averaged within each seed first;
inference is then performed across independent seeds.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.evaluation.statistics import holm_adjust

METRICS = (
    "mean_outage_probability",
    "mean_snr_db",
    "mean_ber_model",
    "mean_goodput_bps_model",
)


def bootstrap_mean(x, samples, seed=2026):
    x = np.asarray(x, float)
    if len(x) == 0:
        raise ValueError("empty effect vector")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(samples, len(x)))
    vals = x[idx].mean(axis=1)
    return float(x.mean()), float(np.quantile(vals, .025)), float(np.quantile(vals, .975))


def signed_test(x):
    x = np.asarray(x, float)
    if np.allclose(x, 0.0):
        return 1.0
    try:
        return float(wilcoxon(x, alternative="two-sided", zero_method="wilcox").pvalue)
    except ValueError:
        return 1.0


def variant_seed_effects(d, variant):
    q = d[d.link_variant == variant]
    keys = ["scenario", "seed"]
    p1 = q[q.planner == "P1"][keys + list(METRICS)].set_index(keys)
    p2 = q[q.planner == "P2"][keys + list(METRICS)].set_index(keys)
    joined = p1.join(p2, lsuffix="_p1", rsuffix="_p2", how="inner", validate="one_to_one")
    if len(joined) == 0:
        raise ValueError(f"no paired P1/P2 episodes for {variant}")
    episode = pd.DataFrame(index=joined.index)
    for metric in METRICS:
        episode[metric] = joined[f"{metric}_p2"] - joined[f"{metric}_p1"]
    # Each seed contributes one effect equal to its mean over the common scenario set.
    seed_effects = episode.reset_index().groupby("seed", as_index=True)[list(METRICS)].mean()
    return seed_effects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/pc_fmcw_geometry_ablation/episodes.csv")
    ap.add_argument("--output-dir", default="results/pc_fmcw_geometry_ablation")
    ap.add_argument("--bootstrap", type=int, default=10000)
    args = ap.parse_args()
    if args.bootstrap < 1:
        raise SystemExit("--bootstrap must be >= 1")
    d = pd.read_csv(args.input)

    effect_frames = {
        variant: variant_seed_effects(d, variant)
        for variant in ("directional", "distance_only")
    }
    seed_table = []
    for variant, frame in effect_frames.items():
        for seed, r in frame.iterrows():
            for metric in METRICS:
                seed_table.append({
                    "link_variant": variant,
                    "seed": int(seed),
                    "metric": metric,
                    "p2_minus_p1_effect": float(r[metric]),
                })
    pd.DataFrame(seed_table).to_csv(
        Path(args.output_dir) / "seed_level_geometry_effects.csv", index=False
    )

    rows = []
    for variant, effects in effect_frames.items():
        for metric in METRICS:
            x = effects[metric].to_numpy(float)
            mean, lo, hi = bootstrap_mean(x, args.bootstrap)
            rows.append({
                "analysis": "P2-P1 within link variant",
                "link_variant": variant,
                "metric": metric,
                "n_independent_seeds": len(x),
                "mean_effect": mean,
                "ci95_low": lo,
                "ci95_high": hi,
                "wilcoxon_p": signed_test(x),
            })

    # Paired difference-in-differences at seed level.
    directional = effect_frames["directional"]
    distance_only = effect_frames["distance_only"]
    common_seeds = directional.index.intersection(distance_only.index)
    for metric in METRICS:
        interaction = (
            directional.loc[common_seeds, metric].to_numpy(float)
            - distance_only.loc[common_seeds, metric].to_numpy(float)
        )
        mean, lo, hi = bootstrap_mean(interaction, args.bootstrap)
        rows.append({
            "analysis": "interaction: directional(P2-P1) - distance_only(P2-P1)",
            "link_variant": "interaction",
            "metric": metric,
            "n_independent_seeds": len(interaction),
            "mean_effect": mean,
            "ci95_low": lo,
            "ci95_high": hi,
            "wilcoxon_p": signed_test(interaction),
        })

    out = pd.DataFrame(rows)
    out["holm_p"] = np.nan
    for analysis, idx in out.groupby("analysis").groups.items():
        ids = list(idx)
        out.loc[ids, "holm_p"] = holm_adjust(out.loc[ids, "wilcoxon_p"].to_numpy(float))

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out.to_csv(outdir / "paired_geometry_effects.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
