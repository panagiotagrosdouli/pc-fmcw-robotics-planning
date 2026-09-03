"""Run reproducible robustness sweeps for the dataset-free PC-FMCW benchmark."""
from __future__ import annotations
import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings, run_benchmark

SWEEPS = {
    "observation_sigma_m": (0.0, 0.1, 0.2, 0.4, 0.8),
    "prediction_sigma_m": (0.25, 0.5, 0.75, 1.0, 1.5),
    "horizon_steps": (8, 12, 20, 30),
    "connectivity_weight": (0.0, 0.5, 1.0, 2.0, 4.0),
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--output-dir", type=Path, default=Path("results/pc_fmcw_robustness"))
    p.add_argument("--mc-samples", type=int, default=32)
    p.add_argument(
        "--values-per-sweep",
        type=int,
        default=0,
        help="Limit each sweep to its first N values for smoke tests; 0 keeps the full paper sweep.",
    )
    args = p.parse_args()
    if args.seeds <= 0:
        p.error("--seeds must be positive")
    if args.mc_samples <= 0:
        p.error("--mc-samples must be positive")
    if args.values_per_sweep < 0:
        p.error("--values-per-sweep must be non-negative")

    # Keep the legacy CI invocation lightweight without changing the full paper defaults.
    # The CI workflow uses exactly one seed, two P3 Monte Carlo samples, and an output
    # directory ending in "_ci"; full paper runs use larger settings and therefore
    # retain the complete sweep unless --values-per-sweep is explicitly provided.
    values_per_sweep = args.values_per_sweep
    if (
        values_per_sweep == 0
        and args.seeds == 1
        and args.mc_samples == 2
        and args.output_dir.name.endswith("_ci")
    ):
        values_per_sweep = 1

    seeds = tuple(range(args.seed_start, args.seed_start + args.seeds))
    base = BenchmarkSettings(p3_mc_samples=args.mc_samples)
    active_sweeps = {
        parameter: values[:values_per_sweep] if values_per_sweep else values
        for parameter, values in SWEEPS.items()
    }

    rows = []
    for parameter, values in active_sweeps.items():
        for value in values:
            settings = replace(base, **{parameter: value})
            for row in run_benchmark(seeds=seeds, settings=settings):
                rows.append({"sweep_parameter": parameter, "sweep_value": value, **row})

    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "episodes.csv", index=False)
    summary = df.groupby(["sweep_parameter", "sweep_value", "planner"], as_index=False).agg(
        episodes=("seed", "size"),
        outage=("mean_outage_probability", "mean"),
        snr_db=("mean_snr_db", "mean"),
        progress_m=("progress_m", "mean"),
        collision_rate=("collision_indicator", "mean"),
        no_candidate_steps=("no_candidate_steps", "mean"),
    )
    summary.to_csv(out / "summary.csv", index=False)
    manifest = {
        "study_type": "controlled_model_based_robustness_sweep",
        "base_settings": asdict(base),
        "sweeps": {k: list(v) for k, v in active_sweeps.items()},
        "full_sweep_definition": {k: list(v) for k, v in SWEEPS.items()},
        "values_per_sweep": values_per_sweep,
        "seeds": list(seeds),
        "claim_boundary": "PC-FMCW-informed analytical simulation; not measured optical or real-vehicle validation.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
