#!/usr/bin/env python3
"""Run the versioned robotics-under-communication-uncertainty experiment matrix."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import platform
import subprocess

import pandas as pd

from iscai.simulation.research_benchmark import ResearchBenchmarkSettings
from iscai.simulation.research_experiments import (
    build_experiment_specs,
    load_research_config,
    run_experiment_specs,
)


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/research_framework.yaml")
    parser.add_argument("--mode", choices=["core", "horizon", "weight", "risk", "shift", "blackout", "compute", "all"], default="core")
    parser.add_argument("--setting-index", type=int, default=None, help="Run exactly one deterministic setting from the selected mode")
    parser.add_argument("--list-settings", action="store_true", help="Print setting indices/IDs as JSON and exit")
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--mc-samples", type=int, default=None)
    parser.add_argument("--output-dir", default="results/research_framework")
    parser.add_argument("--no-trajectories", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_research_config(args.config)
    n_seeds = int(cfg["benchmark"]["seeds"] if args.seeds is None else args.seeds)
    mc_samples = int(cfg["benchmark"]["mc_samples"] if args.mc_samples is None else args.mc_samples)
    if n_seeds < 1:
        raise SystemExit("--seeds must be >= 1")
    if mc_samples < 1:
        raise SystemExit("--mc-samples must be >= 1")
    if args.seed_start < 0:
        raise SystemExit("--seed-start must be >= 0")

    base = ResearchBenchmarkSettings(mc_samples=mc_samples)
    specs = build_experiment_specs(args.mode, config=cfg, base=base)
    if args.list_settings:
        print(json.dumps([
            {"index": i, "experiment": spec.experiment, "setting_id": spec.setting_id}
            for i, spec in enumerate(specs)
        ]))
        return
    if args.setting_index is not None:
        if args.setting_index < 0 or args.setting_index >= len(specs):
            raise SystemExit(f"--setting-index must be in [0,{len(specs)-1}]")
        specs = [specs[args.setting_index]]

    seeds = list(range(args.seed_start, args.seed_start + n_seeds))
    episodes, traces, specs_manifest = run_experiment_specs(specs, seeds)

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(episodes).to_csv(output / "episodes.csv", index=False)
    if not args.no_trajectories:
        pd.DataFrame(traces).to_csv(output / "trajectories.csv", index=False)

    episode_df = pd.DataFrame(episodes)
    metric_columns = [
        "mean_outage_probability", "mean_snr_db", "mean_goodput_bps_model",
        "progress_m", "collision_indicator", "no_candidate_steps",
        "mean_planning_time_s", "p95_planning_time_s", "candidate_evaluations",
    ]
    summary = (
        episode_df.groupby(["experiment", "setting_id", "planner"], as_index=False)[metric_columns]
        .mean(numeric_only=True)
    )
    summary.to_csv(output / "summary.csv", index=False)

    manifest = {
        "protocol_version": cfg["protocol_version"],
        "scientific_question": cfg["scientific_question"],
        "git_commit": _git_sha(),
        "python_version": platform.python_version(),
        "mode": args.mode,
        "setting_index": args.setting_index,
        "seeds": seeds,
        "base_settings": asdict(base),
        "experiment_specs": specs_manifest,
        "claim_boundary": {
            "simulation": True,
            "measured_optical_link": False,
            "oracle_is_deployable": False,
            "safety_claims_separate": True,
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (output / "commit_sha.txt").write_text(manifest["git_commit"] + "\n")
    print(f"wrote {len(episode_df)} episodes across {len(specs)} settings to {output}")


if __name__ == "__main__":
    main()
