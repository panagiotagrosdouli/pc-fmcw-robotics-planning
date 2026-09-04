#!/usr/bin/env python3
"""Merge setting-sharded research-framework artifacts with integrity checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


EPISODE_KEY = ["experiment", "setting_id", "scenario", "planner", "seed"]
TRACE_KEY = ["experiment", "setting_id", "scenario", "planner", "seed", "step"]


def _find(root: Path, name: str):
    return sorted(p for p in root.rglob(name) if p.is_file())


def _read_concat(paths):
    if not paths:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)


def _validate_unique(frame: pd.DataFrame, key, label):
    missing = [c for c in key if c not in frame.columns]
    if missing:
        raise ValueError(f"{label} shards missing key columns: {missing}")
    dup = frame.duplicated(key, keep=False)
    if dup.any():
        examples = frame.loc[dup, key].head(10).to_dict("records")
        raise ValueError(f"duplicate {label} experimental units after merge: {examples}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-settings", type=int, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.input_root)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    episode_paths = _find(root, "episodes.csv")
    trace_paths = _find(root, "trajectories.csv")
    manifest_paths = _find(root, "manifest.json")
    if not episode_paths:
        raise SystemExit("no episodes.csv shards found")

    episodes = _read_concat(episode_paths)
    _validate_unique(episodes, EPISODE_KEY, "episode")
    setting_count = episodes[["experiment", "setting_id"]].drop_duplicates().shape[0]
    if args.expected_settings is not None and setting_count != args.expected_settings:
        raise ValueError(f"expected {args.expected_settings} settings, found {setting_count}")
    episodes = episodes.sort_values(EPISODE_KEY).reset_index(drop=True)
    episodes.to_csv(output / "episodes.csv", index=False)

    if trace_paths:
        traces = _read_concat(trace_paths)
        _validate_unique(traces, TRACE_KEY, "trajectory")
        traces = traces.sort_values(TRACE_KEY).reset_index(drop=True)
        traces.to_csv(output / "trajectories.csv", index=False)

    metric_columns = [
        "mean_outage_probability", "mean_snr_db", "mean_goodput_bps_model",
        "progress_m", "collision_indicator", "no_candidate_steps",
        "mean_planning_time_s", "p95_planning_time_s", "candidate_evaluations",
    ]
    summary = (
        episodes.groupby(["experiment", "setting_id", "planner"], as_index=False)[metric_columns]
        .mean(numeric_only=True)
    )
    summary.to_csv(output / "summary.csv", index=False)

    manifests = [json.loads(path.read_text()) for path in manifest_paths]
    commits = sorted({m.get("git_commit") for m in manifests})
    protocols = sorted({m.get("protocol_version") for m in manifests})
    if len(commits) != 1:
        raise ValueError(f"shards came from multiple commits: {commits}")
    if protocols != ["research-framework-v1"]:
        raise ValueError(f"unexpected protocol versions: {protocols}")
    merged_manifest = {
        "protocol_version": "research-framework-v1",
        "git_commit": commits[0],
        "setting_count": int(setting_count),
        "episode_count": int(len(episodes)),
        "shard_count": int(len(episode_paths)),
        "source_manifests": manifests,
    }
    (output / "manifest.json").write_text(json.dumps(merged_manifest, indent=2, sort_keys=True))
    (output / "commit_sha.txt").write_text(str(commits[0]) + "\n")
    print(f"merged {len(episode_paths)} shards, {setting_count} settings, {len(episodes)} episodes")


if __name__ == "__main__":
    main()
