#!/usr/bin/env python3
"""Mechanism ablation for the PC-FMCW-informed planning link.

Compares the default distance+angular surrogate against a distance-only surrogate while
holding planner, scenarios, seeds and all non-link settings fixed. This is an exploratory
mechanism analysis, not optical-channel validation.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.connectivity.pc_fmcw_bridge import (
    OpticalGeometryAssumptions,
    PCFMCWPlanningLinkPredictor,
)
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings, run_benchmark


def predictor(variant: str):
    if variant == "directional":
        geometry = OpticalGeometryAssumptions()
    elif variant == "distance_only":
        geometry = OpticalGeometryAssumptions(beam_sigma_rad=1e6)
    else:
        raise ValueError(variant)
    return PCFMCWPlanningLinkPredictor(geometry=geometry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-start", type=int, default=2000)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--output-dir", default="results/pc_fmcw_geometry_ablation")
    ap.add_argument("--mc-samples", type=int, default=32)
    ap.add_argument("--planning-safety-margin-m", type=float, default=0.0)
    args = ap.parse_args()
    if args.seeds < 1:
        raise SystemExit("--seeds must be >= 1")
    if args.planning_safety_margin_m < 0:
        raise SystemExit("--planning-safety-margin-m must be >= 0")

    settings = BenchmarkSettings(
        p3_mc_samples=args.mc_samples,
        planning_safety_margin_m=args.planning_safety_margin_m,
    )
    seeds = range(args.seed_start, args.seed_start + args.seeds)
    rows = []
    provenance = {}
    for variant in ("directional", "distance_only"):
        link = predictor(variant)
        provenance[variant] = {
            **link.provenance(),
            "geometry": link.geometry.__dict__,
        }
        for row in run_benchmark(seeds=seeds, settings=settings, link_predictor=link):
            rows.append({"link_variant": variant, **row})

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "episodes.csv", index=False)
    summary = df.groupby(["link_variant", "planner"], as_index=False).agg(
        episodes=("seed", "size"),
        outage=("mean_outage_probability", "mean"),
        snr_db=("mean_snr_db", "mean"),
        ber=("mean_ber_model", "mean"),
        goodput_bps=("mean_goodput_bps_model", "mean"),
        progress_m=("progress_m", "mean"),
        collision_rate=("collision_indicator", "mean"),
    )
    summary.to_csv(out / "summary.csv", index=False)
    manifest = {
        "study": "PC-FMCW-informed optical-geometry mechanism ablation",
        "seed_start": args.seed_start,
        "seed_count": args.seeds,
        "settings": settings.__dict__,
        "variants": provenance,
        "claim_boundary": (
            "Controlled analytical mechanism ablation. The directional and distance-only "
            "links are simulation surrogates, not measured optical channels."
        ),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
