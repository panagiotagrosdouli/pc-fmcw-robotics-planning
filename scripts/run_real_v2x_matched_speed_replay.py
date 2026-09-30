#!/usr/bin/env python3
"""Matched field replay for communication-aware longitudinal speed decisions.

The experiment uses the repeated 30/50-km/h CICV5G W2S/S2W field runs as a
motion-conditioned outcome library.

Evidence roles are disjoint:
  * train runs fit a speed-conditioned spatial QoS predictor;
  * donor runs provide measured outcomes for candidate speeds;
  * query runs provide decision locations/contexts only.

At one query location, a deployable policy scores 30 and 50 km/h using only the
training-fitted predictor. The chosen speed is evaluated afterward using measured
delay from donor runs with the same network/direction/speed and within a spatial
caliper. Donor outcomes are never exposed during policy selection.

This is matched field replay, not a randomized physical intervention. Run/time
confounding remains a limitation and is reported explicitly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.connectivity.real_v2x.datasets import (
    add_run_metadata,
    discover_cicv5g_files,
    load_cicv5g_file,
)
from iscai.connectivity.real_v2x.matched_replay import (
    CrossRunSpeedMatcher,
    stratified_run_split,
)
from iscai.connectivity.real_v2x.predictors import ConditionedSpatialKNNPredictor


def spatial_thin(g: pd.DataFrame, spacing_m: float) -> pd.DataFrame:
    """Keep ordered query points separated by at least spacing_m along the trace."""
    if g.empty or spacing_m <= 0:
        return g
    g = g.sort_values("pub_time_ms", kind="stable").reset_index(drop=True)
    keep = [0]
    last = g.loc[0, ["utm_x_m", "utm_y_m"]].to_numpy(float)
    for i in range(1, len(g)):
        p = g.loc[i, ["utm_x_m", "utm_y_m"]].to_numpy(float)
        if float(np.linalg.norm(p - last)) >= spacing_m:
            keep.append(i)
            last = p
    return g.iloc[keep].copy()


def mobility_costs(speeds: list[float], segment_m: float) -> dict[float, float]:
    times = {s: segment_m / max(s / 3.6, 1e-6) for s in speeds}
    lo, hi = min(times.values()), max(times.values())
    if hi <= lo:
        return {s: 0.0 for s in speeds}
    return {s: (times[s] - lo) / (hi - lo) for s in speeds}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/cicv5g")
    ap.add_argument("--output", default="results/real_v2x_matched_speed")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--speeds", default="30,50")
    ap.add_argument("--caliper-m", type=float, default=2.0)
    ap.add_argument("--k-donors", type=int, default=5)
    ap.add_argument("--query-spacing-m", type=float, default=5.0)
    ap.add_argument("--segment-m", type=float, default=50.0)
    ap.add_argument("--delay-scale-ms", type=float, default=100.0)
    ap.add_argument("--comm-weight", type=float, default=1.0)
    ap.add_argument("--mobility-weight", type=float, default=0.15)
    ap.add_argument("--min-predicted-gain-ms", type=float, default=0.5)
    args = ap.parse_args()

    speeds = sorted({float(x) for x in args.speeds.split(",")})
    if len(speeds) != 2:
        raise ValueError("this first matched-speed protocol requires exactly two speeds")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    files = discover_cicv5g_files(args.data)
    df = pd.concat(
        [add_run_metadata(load_cicv5g_file(p), p) for p in files],
        ignore_index=True,
    )
    df = df[df["nominal_speed_kmh"].isin(speeds)].copy()

    train, donor, query, split = stratified_run_split(df, seed=args.seed)
    if train.empty or donor.empty or query.empty:
        raise RuntimeError("stratified split produced an empty evidence role")

    predictor = ConditionedSpatialKNNPredictor(
        target="delay_ms",
        n_neighbors=20,
        min_group_samples=100,
    ).fit(train)

    donor_matcher = CrossRunSpeedMatcher(
        caliper_m=args.caliper_m,
        k_donors=args.k_donors,
    ).fit(donor)

    # Training support is used only as a deployable support diagnostic. The measured
    # delay returned by this matcher is never used for action selection.
    train_support = CrossRunSpeedMatcher(
        caliper_m=args.caliper_m,
        k_donors=args.k_donors,
    ).fit(train)

    mobility = mobility_costs(speeds, args.segment_m)
    fast, slow = max(speeds), min(speeds)

    rows: list[dict] = []
    eligible_queries = 0

    for run_id, g0 in query.groupby("run_id", sort=False):
        g = spatial_thin(g0, args.query_spacing_m)
        for _, q in g.iterrows():
            measured = {s: donor_matcher.match(q, s) for s in speeds}
            if any(measured[s] is None for s in speeds):
                continue

            candidate_frames = []
            for s in speeds:
                c = q.to_frame().T.copy()
                c["nominal_speed_kmh"] = s
                c["velocity_mps"] = s / 3.6
                candidate_frames.append(c)
            cand_df = pd.concat(candidate_frames, ignore_index=True)
            preds = predictor.predict(cand_df)
            pred = {s: float(preds[i]) for i, s in enumerate(speeds)}
            support = {s: train_support.match(q, s) is not None for s in speeds}

            pred_score = {
                s: args.comm_weight * np.clip(pred[s] / args.delay_scale_ms, 0.0, 2.0)
                + args.mobility_weight * mobility[s]
                for s in speeds
            }
            oracle_score = {
                s: args.comm_weight * np.clip(measured[s].delay_ms / args.delay_scale_ms, 0.0, 2.0)
                + args.mobility_weight * mobility[s]
                for s in speeds
            }

            pred_choice = min(speeds, key=lambda s: (pred_score[s], -s))
            oracle_choice = min(speeds, key=lambda s: (oracle_score[s], -s))

            # Conservative deployable variant: only deviate from FAST when both speed
            # candidates have training support and the predicted delay gain is material.
            predicted_delay_gain = pred[fast] - pred[slow]
            supported_choice = fast
            if all(support.values()) and predicted_delay_gain >= args.min_predicted_gain_ms:
                supported_choice = pred_choice

            modes = {
                "FAST": fast,
                "SLOW": slow,
                "PRED": pred_choice,
                "PRED_SUPPORT": supported_choice,
                "ORACLE_MATCHED": oracle_choice,
            }
            eligible_queries += 1

            for mode, chosen_speed in modes.items():
                m = measured[chosen_speed]
                rows.append({
                    "query_run_id": run_id,
                    "network": q["network"],
                    "direction": q["direction"],
                    "query_nominal_speed_kmh": float(q["nominal_speed_kmh"]),
                    "utm_x_m": float(q["utm_x_m"]),
                    "utm_y_m": float(q["utm_y_m"]),
                    "mode": mode,
                    "chosen_speed_kmh": chosen_speed,
                    "changed_from_fast": bool(chosen_speed != fast),
                    "predicted_delay_ms": pred[chosen_speed],
                    "measured_matched_delay_ms": m.delay_ms,
                    "matched_delay_std_ms": m.delay_std_ms,
                    "nearest_donor_m": m.nearest_distance_m,
                    "mean_donor_m": m.mean_distance_m,
                    "n_donors": m.n_donors,
                    "n_donor_runs": m.n_donor_runs,
                    "train_supported_30": bool(support[slow]),
                    "train_supported_50": bool(support[fast]),
                    "mobility_cost": mobility[chosen_speed],
                    "decision_score": (
                        oracle_score[chosen_speed]
                        if mode == "ORACLE_MATCHED"
                        else pred_score[chosen_speed]
                    ),
                })

    decisions = pd.DataFrame(rows)
    if decisions.empty:
        raise RuntimeError("no matched query locations satisfy the donor caliper")
    decisions.to_csv(out / "decisions.csv", index=False)

    per_run = decisions.groupby(["query_run_id", "mode"]).agg(
        n=("measured_matched_delay_ms", "size"),
        mean_matched_delay_ms=("measured_matched_delay_ms", "mean"),
        p95_matched_delay_ms=("measured_matched_delay_ms", lambda x: float(np.quantile(x, 0.95))),
        mean_mobility_cost=("mobility_cost", "mean"),
        changed_from_fast_fraction=("changed_from_fast", "mean"),
        mean_nearest_donor_m=("nearest_donor_m", "mean"),
        mean_donor_runs=("n_donor_runs", "mean"),
    ).reset_index()
    per_run.to_csv(out / "run_metrics.csv", index=False)

    summary = per_run.groupby("mode").agg(
        query_runs=("query_run_id", "nunique"),
        mean_delay_ms=("mean_matched_delay_ms", "mean"),
        mean_p95_delay_ms=("p95_matched_delay_ms", "mean"),
        mean_mobility_cost=("mean_mobility_cost", "mean"),
        changed_from_fast_fraction=("changed_from_fast_fraction", "mean"),
        mean_nearest_donor_m=("mean_nearest_donor_m", "mean"),
        mean_donor_runs=("mean_donor_runs", "mean"),
    ).reset_index()
    summary.to_csv(out / "summary.csv", index=False)

    metadata = {
        "seed": args.seed,
        "speeds_kmh": speeds,
        "caliper_m": args.caliper_m,
        "k_donors": args.k_donors,
        "query_spacing_m": args.query_spacing_m,
        "segment_m": args.segment_m,
        "delay_scale_ms": args.delay_scale_ms,
        "comm_weight": args.comm_weight,
        "mobility_weight": args.mobility_weight,
        "min_predicted_gain_ms": args.min_predicted_gain_ms,
        "eligible_query_locations": eligible_queries,
        "split": split,
        "claim_boundary": (
            "Cross-run matched field replay under exact network/direction/speed and "
            "spatial-caliper overlap. Donor outcomes are measured and hidden during "
            "selection, but runs are observational/repeated experiments rather than "
            "randomized speed interventions; causal speed effects are not claimed."
        ),
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(summary.to_string(index=False))
    print(json.dumps({k: v for k, v in metadata.items() if k != "split"}, indent=2))


if __name__ == "__main__":
    main()
