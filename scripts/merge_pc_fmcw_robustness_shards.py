"""Merge independently generated robustness seed artifacts.

The paper workflow executes one robustness sweep per seed. This utility merges
those episode-level CSVs into one dataset without changing any measurements.
It also writes a compact aggregate summary for inspection and plotting.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

METRICS = [
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
]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--expected-seeds", type=int, default=20)
    args = p.parse_args()

    paths = sorted(args.input_root.glob("robustness-seed-*/episodes.csv"))
    if len(paths) != args.expected_seeds:
        raise SystemExit(
            f"expected {args.expected_seeds} robustness episode files, found {len(paths)}"
        )

    frames = []
    for path in paths:
        frame = pd.read_csv(path)
        if "seed" not in frame.columns:
            raise SystemExit(f"missing seed column in {path}")
        frames.append(frame)

    episodes = pd.concat(frames, ignore_index=True)
    seeds = sorted(episodes["seed"].astype(int).unique().tolist())
    if len(seeds) != args.expected_seeds:
        raise SystemExit(f"expected {args.expected_seeds} unique seeds, found {seeds}")

    required = {"sweep_parameter", "sweep_value", "planner", *METRICS}
    missing = required - set(episodes.columns)
    if missing:
        raise SystemExit(f"merged episodes missing columns: {sorted(missing)}")

    group_cols = ["sweep_parameter", "sweep_value", "planner"]
    summary = episodes.groupby(group_cols, as_index=False)[METRICS].mean()
    counts = episodes.groupby(group_cols, as_index=False).size().rename(columns={"size": "episodes"})
    summary = counts.merge(summary, on=group_cols, how="inner", validate="one_to_one")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    episodes.to_csv(args.output_dir / "episodes.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    (args.output_dir / "MERGE_INFO.txt").write_text(
        f"robustness seed artifacts: {len(paths)}\n"
        f"unique seeds: {seeds}\n"
        f"merged episode rows: {len(episodes)}\n",
        encoding="utf-8",
    )
    print(f"merged {len(paths)} seed artifacts into {len(episodes)} episode rows")


if __name__ == "__main__":
    main()
