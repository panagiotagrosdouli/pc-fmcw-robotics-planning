#!/usr/bin/env python3
"""Build Paper 1 diagnostic/publication assets from PC-FMCW result artifacts.

V1 outputs are deliberately labelled exploratory. The script can be reused with a
future V2 confirmatory directory after the hard safety gate passes.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def save(fig, out: Path, stem: str):
    out.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("benchmark_dir", type=Path, help="directory containing confirmatory_seed_level_effects.csv and scenario_summary.csv")
    ap.add_argument("--geometry-dir", type=Path, default=None, help="directory containing paired_geometry_effects.csv")
    ap.add_argument("--out", type=Path, default=Path("manuscripts/paper1_pc_fmcw/generated"))
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    effects = pd.read_csv(args.benchmark_dir / "confirmatory_seed_level_effects.csv")
    scenario = pd.read_csv(args.benchmark_dir / "scenario_summary.csv")
    safety_path = args.benchmark_dir / "diagnostics" / "scenario_safety_prediction.csv"
    safety = pd.read_csv(safety_path) if safety_path.exists() else None

    p21 = effects[(effects["comparison"] == "P2-P1") & effects["metric"].isin(["mean_outage_probability", "mean_snr_db", "mean_ber_model", "mean_goodput_bps_model"])].copy()
    # Scale unlike endpoints for a readable effect-size panel; exact values stay in tables.
    labels = {"mean_outage_probability":"Outage", "mean_snr_db":"SNR (dB)", "mean_ber_model":"BER", "mean_goodput_bps_model":"Goodput (Mbps)"}
    vals=[]
    for _, r in p21.iterrows():
        v=float(r["mean_seed_delta_b_minus_a"])
        if r["metric"] == "mean_goodput_bps_model": v /= 1e6
        vals.append(v)
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    ax.bar([labels[x] for x in p21["metric"]], vals)
    ax.axhline(0, linewidth=1)
    ax.set_ylabel("P2-P1 effect (endpoint units)")
    ax.tick_params(axis="x", rotation=20)
    save(fig, out, "fig_v1_p2_p1_effects_exploratory")

    # Safety audit: maximum collision rate and no-candidate burden by scenario.
    agg = scenario.groupby("scenario", as_index=False).agg(collision_rate=("collision_rate","max"), no_candidate_steps=("no_candidate_steps","max"))
    fig, ax = plt.subplots(figsize=(5.0, 2.8))
    ax.bar(agg["scenario"], agg["collision_rate"])
    ax.set_ylabel("V1 collision rate")
    ax.tick_params(axis="x", rotation=25)
    save(fig, out, "fig_v1_safety_collision")
    fig, ax = plt.subplots(figsize=(5.0, 2.8))
    ax.bar(agg["scenario"], agg["no_candidate_steps"])
    ax.set_ylabel("Max mean no-candidate steps")
    ax.tick_params(axis="x", rotation=25)
    save(fig, out, "fig_v1_no_candidate")

    effects.to_csv(out / "table_v1_seed_level_effects.csv", index=False)
    scenario.to_csv(out / "table_v1_scenario_summary.csv", index=False)
    (out / "table_v1_seed_level_effects.tex").write_text(effects.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))
    (out / "table_v1_scenario_summary.tex").write_text(scenario.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))
    if safety is not None:
        safety.to_csv(out / "table_v1_safety_diagnostics.csv", index=False)

    if args.geometry_dir is not None:
        geom = pd.read_csv(args.geometry_dir / "paired_geometry_effects.csv")
        g = geom[(geom["analysis"] == "P2-P1 within link variant") & geom["metric"].isin(["mean_outage_probability","mean_snr_db"])].copy()
        fig, ax = plt.subplots(figsize=(4.6, 2.8))
        # two metrics use separate panels/files to avoid mixing incomparable units
        for metric, stem, ylabel in [("mean_outage_probability","fig_geometry_outage","P2-P1 outage effect"),("mean_snr_db","fig_geometry_snr","P2-P1 SNR effect (dB)")]:
            d=g[g["metric"]==metric]
            f, a=plt.subplots(figsize=(4.0,2.6))
            a.bar(d["link_variant"], d["mean_effect"])
            a.axhline(0, linewidth=1)
            a.set_ylabel(ylabel)
            save(f,out,stem)
        geom.to_csv(out / "table_v1_geometry_effects.csv", index=False)
        (out / "table_v1_geometry_effects.tex").write_text(geom.to_latex(index=False, float_format=lambda x: f"{x:.4g}"))


if __name__ == "__main__":
    main()
