#!/usr/bin/env python3
"""Route-constrained measured-support replay for P0-P3 communication-aware decisions.

This is deliberately NOT presented as closed-loop vehicle validation. At each held-out
CICV5G sample, the decision proxy ranks several future samples on the same measured
route. Future delay is never exposed to P0-P3; it is used only after selection as a
measured outcome. The experiment therefore tests whether a causal QoS predictor has
decision value while avoiding fabricated QoS labels at arbitrary unmeasured positions.

QoS-map/support queries are batched per held-out run and offset. The recorded decision
time therefore measures lightweight score/rank execution after the predictor has supplied
its horizon forecasts, while a separate preprocessing time records batched map/support
inference. Neither number is called real-time capability without an explicit budget.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from iscai.connectivity.real_v2x.datasets import (
    add_run_metadata, blocked_run_split, discover_cicv5g_files, load_cicv5g_file,
)
from iscai.connectivity.real_v2x.predictors import ConditionedSpatialKNNPredictor
from iscai.connectivity.real_v2x.support import SpatialSupportModel
from iscai.connectivity.real_v2x.uncertainty import ResidualConformalCalibrator

CONTEXT = ("network", "direction", "nominal_speed_kmh")

def pairs(df, h):
    rows = []
    for run, g in df.groupby("run_id", sort=False):
        g = g.sort_values("pub_time_ms").reset_index(drop=True)
        if len(g) <= h:
            continue
        fut = g.iloc[h:].copy().reset_index(drop=True)
        cur = g.iloc[:-h].reset_index(drop=True)
        fut["current_delay_ms"] = cur.delay_ms.to_numpy(float)
        rows.append(fut)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

def key_tuple(key):
    if not isinstance(key, tuple):
        key = (key,)
    return tuple(None if pd.isna(v) else v for v in key)

def choose_weight(y, persistence, spatial):
    grid = np.linspace(0.0, 1.0, 41)
    losses = [np.mean(np.abs(y - (w * persistence + (1.0 - w) * spatial))) for w in grid]
    return float(grid[int(np.argmin(losses))])

def calibrate_for_offset(cal, spatial_model, h, alpha):
    ca = pairs(cal, h)
    spatial = spatial_model.predict(ca)
    work = ca[list(CONTEXT)].copy()
    work["y"] = ca.delay_ms.to_numpy(float)
    work["p"] = ca.current_delay_ms.to_numpy(float)
    work["m"] = spatial
    weights = {}
    for key, g in work.groupby(list(CONTEXT), dropna=False):
        weights[key_tuple(key)] = choose_weight(
            g.y.to_numpy(float), g.p.to_numpy(float), g.m.to_numpy(float)
        ) if len(g) >= 100 else 1.0
    pred = np.empty(len(ca), float)
    for key, idxs in ca.groupby(list(CONTEXT), dropna=False, sort=False).groups.items():
        pos = np.asarray([ca.index.get_loc(i) for i in idxs], dtype=int)
        w = float(weights.get(key_tuple(key), 1.0))
        pred[pos] = w * ca.current_delay_ms.to_numpy(float)[pos] + (1.0 - w) * spatial[pos]
    calibrator = ResidualConformalCalibrator(alpha).fit(ca.delay_ms.to_numpy(float), pred)
    return weights, calibrator

def horizon_forecasts(g, offsets, spatial, support, calibration):
    """Batch all predictor/support queries for one run without using future QoS as input."""
    max_h = max(offsets)
    n = len(g) - max_h
    if n <= 0:
        return {}, 0.0
    current_delay = g.delay_ms.to_numpy(float)[:n]
    result = {}
    start = time.perf_counter_ns()
    for h in offsets:
        future = g.iloc[h:h+n].copy().reset_index(drop=True)
        map_pred = np.asarray(spatial.predict(future), float)
        weights, calibrator = calibration[h]
        w = np.ones(n, float)
        for key, idxs in future.groupby(list(CONTEXT), dropna=False, sort=False).groups.items():
            pos = np.asarray(list(idxs), dtype=int)
            w[pos] = float(weights.get(key_tuple(key), 1.0))
        pred = w * current_delay + (1.0 - w) * map_pred
        _, hi = calibrator.interval(pred)
        sup = support.evaluate(future)
        result[h] = {
            "pred": pred,
            "upper": np.asarray(hi, float),
            "supported": np.asarray(sup["supported"], bool),
            "nearest": np.asarray(sup["nearest_distance_m"], float),
            "truth": future.delay_ms.to_numpy(float),
            "mobility": abs(h - int(np.median(offsets))) / max(int(np.median(offsets)), 1),
        }
    elapsed_ms = (time.perf_counter_ns() - start) / 1e6
    return result, elapsed_ms

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/cicv5g")
    ap.add_argument("--output", default="results/real_v2x_replay")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--nominal-horizon", type=int, default=20)
    ap.add_argument("--offset-factors", default="0.5,1.0,1.5")
    ap.add_argument("--delay-threshold-ms", type=float, default=50.0)
    ap.add_argument("--comm-weight", type=float, default=0.35)
    ap.add_argument("--risk-weight", type=float, default=0.20)
    ap.add_argument("--mobility-weight", type=float, default=0.15)
    ap.add_argument("--unsupported-penalty", type=float, default=0.50)
    ap.add_argument("--support-radius-m", type=float, default=1.0)
    ap.add_argument("--support-min-neighbors", type=int, default=5)
    ap.add_argument("--alpha", type=float, default=0.1)
    args = ap.parse_args()

    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    files = discover_cicv5g_files(args.data)
    df = pd.concat([add_run_metadata(load_cicv5g_file(p), p) for p in files], ignore_index=True)
    train, cal, test, split = blocked_run_split(df, seed=args.seed)

    spatial = ConditionedSpatialKNNPredictor("delay_ms", 20, min_group_samples=100).fit(train)
    support = SpatialSupportModel(
        radius_m=args.support_radius_m, min_neighbors=args.support_min_neighbors
    ).fit(train)

    nominal = int(args.nominal_horizon)
    offsets = sorted(set(max(1, int(round(nominal * f))) for f in
                         [float(x) for x in args.offset_factors.split(",")]))
    calibration = {}
    for h in offsets:
        weights, calibrator = calibrate_for_offset(cal, spatial, h, args.alpha)
        calibration[h] = (weights, calibrator)

    rows = []
    decision_us = []
    inference_ms = []
    candidate_count = 0
    for run_id, g0 in test.groupby("run_id", sort=False):
        g = g0.sort_values("pub_time_ms").reset_index(drop=True)
        forecasts, infer_ms = horizon_forecasts(g, offsets, spatial, support, calibration)
        inference_ms.append(infer_ms)
        if not forecasts:
            continue
        n = len(next(iter(forecasts.values()))["pred"])
        candidate_count += n * len(offsets)
        for t in range(n):
            start = time.perf_counter_ns()
            candidates = []
            for h in offsets:
                f = forecasts[h]
                candidates.append({
                    "h": h, "pred": float(f["pred"][t]), "upper": float(f["upper"][t]),
                    "supported": bool(f["supported"][t]), "nearest_train_m": float(f["nearest"][t]),
                    "mobility": abs(h - nominal) / max(nominal, 1),
                    "truth_delay": float(f["truth"][t]),
                })

            selected = {}
            for mode in ("P0", "P1", "P2", "P3"):
                scored = []
                for c in candidates:
                    if mode in ("P0", "P1"):
                        score = args.mobility_weight * c["mobility"]
                    else:
                        score = (args.mobility_weight * c["mobility"]
                                 + args.comm_weight * min(c["pred"] / 100.0, 2.0))
                        if mode == "P3":
                            score += args.risk_weight * float(c["upper"] > args.delay_threshold_ms)
                            score += args.unsupported_penalty * float(not c["supported"])
                    scored.append((score, c))
                selected[mode] = min(scored, key=lambda z: (z[0], abs(z[1]["h"] - nominal)))
            decision_us.append((time.perf_counter_ns() - start) / 1000.0)

            for mode, (score, chosen) in selected.items():
                rows.append({
                    "run_id": run_id, "t_index": t, "mode": mode, "score": score,
                    "chosen_horizon_steps": chosen["h"], "nominal_horizon_steps": nominal,
                    "changed_from_nominal": chosen["h"] != nominal,
                    "measured_delay_ms": chosen["truth_delay"],
                    "delay_violation": chosen["truth_delay"] > args.delay_threshold_ms,
                    "predicted_delay_ms": chosen["pred"], "predicted_upper_ms": chosen["upper"],
                    "selected_supported": chosen["supported"],
                    "nearest_train_m": chosen["nearest_train_m"],
                    "mobility_deviation": chosen["mobility"],
                })

    decisions = pd.DataFrame(rows)
    decisions.to_csv(out / "decisions.csv", index=False)
    per_run = decisions.groupby(["run_id", "mode"]).agg(
        n=("delay_violation", "size"),
        mean_measured_delay_ms=("measured_delay_ms", "mean"),
        violation_fraction=("delay_violation", "mean"),
        changed_fraction=("changed_from_nominal", "mean"),
        unsupported_fraction=("selected_supported", lambda s: float(np.mean(~s.astype(bool)))),
        mean_mobility_deviation=("mobility_deviation", "mean"),
    ).reset_index()
    per_run.to_csv(out / "run_metrics.csv", index=False)
    summary = per_run.groupby("mode").agg(
        runs=("run_id", "nunique"), mean_delay_ms=("mean_measured_delay_ms", "mean"),
        mean_violation_fraction=("violation_fraction", "mean"),
        mean_changed_fraction=("changed_fraction", "mean"),
        mean_unsupported_fraction=("unsupported_fraction", "mean"),
        mean_mobility_deviation=("mean_mobility_deviation", "mean"),
    ).reset_index()
    summary.to_csv(out / "summary.csv", index=False)
    total_infer_ms = float(np.sum(inference_ms)) if inference_ms else 0.0
    meta = {
        "seed": args.seed, "offsets": offsets, "nominal_horizon": nominal,
        "delay_threshold_ms": args.delay_threshold_ms,
        "threshold_status": "experimental operating point; not a universal standard",
        "support_radius_m": args.support_radius_m,
        "support_min_neighbors": args.support_min_neighbors,
        "candidate_queries": candidate_count,
        "batched_qos_support_inference_ms_total": total_infer_ms,
        "batched_qos_support_inference_us_per_candidate": 1000.0 * total_infer_ms / max(candidate_count, 1),
        "decision_scoring_us_mean": float(np.mean(decision_us)) if decision_us else None,
        "decision_scoring_us_p95": float(np.percentile(decision_us, 95)) if decision_us else None,
        "claim_boundary": "Route-constrained offline measured replay; future measured QoS is outcome-only. Timing is measured software execution on the CI host, not a certified real-time guarantee.",
        "split": split,
    }
    (out / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))
    print(json.dumps({k:v for k,v in meta.items() if k != "split"}, indent=2))

if __name__ == "__main__":
    main()
