#!/usr/bin/env python3
"""Analyze whether the predictive-vs-reactive effect depends on angular link geometry."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.evaluation.statistics import paired_bootstrap_delta, holm_adjust

METRICS = (
    "mean_outage_probability",
    "mean_snr_db",
    "mean_ber_model",
    "mean_goodput_bps_model",
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/pc_fmcw_geometry_ablation/episodes.csv")
    ap.add_argument("--output-dir", default="results/pc_fmcw_geometry_ablation")
    ap.add_argument("--bootstrap", type=int, default=10000)
    args = ap.parse_args()
    d = pd.read_csv(args.input)
    keys = ["scenario", "seed"]
    rows = []

    # For each link variant, compute the paired predictive-vs-reactive P2-P1 effect.
    effect_frames = {}
    for variant in ("directional", "distance_only"):
        q = d[d.link_variant == variant]
        p1 = q[q.planner == "P1"][keys + list(METRICS)].set_index(keys)
        p2 = q[q.planner == "P2"][keys + list(METRICS)].set_index(keys)
        joined = p1.join(p2, lsuffix="_p1", rsuffix="_p2", how="inner", validate="one_to_one")
        effects = pd.DataFrame(index=joined.index)
        for metric in METRICS:
            effects[metric] = joined[f"{metric}_p2"] - joined[f"{metric}_p1"]
            x = joined[f"{metric}_p1"].to_numpy(float)
            y = joined[f"{metric}_p2"].to_numpy(float)
            boot = paired_bootstrap_delta(x, y, samples=args.bootstrap, rng=2026)
            try:
                p = float(wilcoxon(y - x).pvalue) if np.any((y - x) != 0) else 1.0
            except ValueError:
                p = 1.0
            rows.append({
                "analysis": "P2-P1 within link variant",
                "link_variant": variant,
                "metric": metric,
                "n_pairs": len(joined),
                "mean_effect": boot["mean_delta"],
                "ci95_low": boot["ci_low"],
                "ci95_high": boot["ci_high"],
                "wilcoxon_p": p,
            })
        effect_frames[variant] = effects

    # Difference-in-differences: does removing angular loss change the P2-P1 effect?
    a = effect_frames["directional"]
    b = effect_frames["distance_only"]
    common = a.index.intersection(b.index)
    for metric in METRICS:
        directional = a.loc[common, metric].to_numpy(float)
        distance_only = b.loc[common, metric].to_numpy(float)
        interaction = directional - distance_only
        rng = np.random.default_rng(2026)
        draws = np.array([
            rng.choice(interaction, size=len(interaction), replace=True).mean()
            for _ in range(args.bootstrap)
        ])
        try:
            p = float(wilcoxon(interaction).pvalue) if np.any(interaction != 0) else 1.0
        except ValueError:
            p = 1.0
        rows.append({
            "analysis": "interaction: directional(P2-P1) - distance_only(P2-P1)",
            "link_variant": "interaction",
            "metric": metric,
            "n_pairs": len(interaction),
            "mean_effect": float(np.mean(interaction)),
            "ci95_low": float(np.quantile(draws, .025)),
            "ci95_high": float(np.quantile(draws, .975)),
            "wilcoxon_p": p,
        })

    out = pd.DataFrame(rows)
    # Treat the four communication endpoints within each analysis family as one family.
    out["holm_p"] = np.nan
    for analysis, idx in out.groupby("analysis").groups.items():
        out.loc[list(idx), "holm_p"] = holm_adjust(out.loc[list(idx), "wilcoxon_p"].to_numpy(float))

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out.to_csv(outdir / "paired_geometry_effects.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
