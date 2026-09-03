"""Replay real CMHT target motion through the Stage-9 planner stack.

Target motion comes from real CMHT annotation tracklets. Ego motion is generated
by the repository's candidate-motion planner, so this is a data-driven replay
benchmark, NOT a real-world closed-loop vehicle experiment. Connectivity is
computed by the configured geometry surrogate unless a frozen calibrated
PC-FMCW predictor is substituted later.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_predictor import constant_velocity
from iscai.prediction.trajectory_dataset import make_windows
from iscai.connectivity.predictor import GeometryLinkPredictor
from iscai.planning.planners import (
    MobilityOnlyPlanner, ReactiveConnectivityPlanner,
    PredictiveConnectivityPlanner, OracleConnectivityPlanner,
)
from iscai.planning.risk_aware_planner import RiskAwarePredictivePlanner


def _target_states(xy, dt):
    xy = np.asarray(xy, float)
    out = np.zeros((len(xy), 4), float)
    out[:, :2] = xy
    if len(xy) > 1:
        vel = np.gradient(xy, dt, axis=0)
        out[:, 2] = np.arctan2(vel[:, 1], vel[:, 0])
        out[:, 3] = np.linalg.norm(vel, axis=1)
    return out


def _initial_ego(history, dt, gap=12.0):
    p = np.asarray(history[-1], float)
    v = (history[-1] - history[-2]) / dt
    speed = float(np.linalg.norm(v))
    yaw = float(np.arctan2(v[1], v[0])) if speed > 1e-6 else 0.0
    return np.array([p[0] - gap*np.cos(yaw), p[1] - gap*np.sin(yaw), yaw, max(speed, 1.0)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, required=True)
    ap.add_argument("--history", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--dt", type=float, default=0.1)
    ap.add_argument("--sigma-m", type=float, default=0.75,
                    help="P3 uncertainty scale; replace with calibrated Transformer sigma for final experiments")
    ap.add_argument("--max-windows", type=int, default=500)
    ap.add_argument("--output", type=Path, default=Path("results/cmht_planner_replay.csv"))
    args = ap.parse_args()

    rows = extract_object_positions(args.labels)
    windows = make_windows(rows, history=args.history, horizon=args.horizon)
    if not windows:
        raise SystemExit("No contiguous CMHT windows found")
    windows = windows[:args.max_windows]

    link = GeometryLinkPredictor()
    planners = {
        "P0": MobilityOnlyPlanner(link),
        "P1": ReactiveConnectivityPlanner(link),
        "P2": PredictiveConnectivityPlanner(link),
        "P3": RiskAwarePredictivePlanner(link, mc_samples=128),
        "P4": OracleConnectivityPlanner(link),
    }

    records = []
    for wi, sample in enumerate(windows):
        hist = np.asarray(sample["history"], float)
        truth_xy = np.asarray(sample["future"], float)
        pred_xy = constant_velocity(hist, args.horizon, args.dt)
        truth = _target_states(truth_xy, args.dt)
        pred = _target_states(pred_xy, args.dt)
        ego0 = _initial_ego(hist, args.dt)
        reference_speed = ego0[3]
        p3_pred = {"mean_xy": pred_xy, "sigma_xy": np.full_like(pred_xy, args.sigma_m)}

        for name, planner in planners.items():
            target = p3_pred if name == "P3" else (truth if name == "P4" else pred)
            tic = time.perf_counter()
            result = planner.plan(ego0, target, obstacles=[], reference_speed=reference_speed)
            runtime_ms = 1e3 * (time.perf_counter() - tic)
            if result.candidate is None:
                records.append({"window": wi, "object_id": sample["object_id"], "planner": name,
                                "feasible": False, "score": np.inf, "runtime_ms": runtime_ms})
                continue
            realized = link.predict(result.candidate, truth[:len(result.candidate.states)])
            snr = np.asarray(realized.snr_db, float)
            records.append({
                "window": wi, "object_id": sample["object_id"], "planner": name,
                "feasible": True, "score": result.score, "runtime_ms": runtime_ms,
                "mean_snr_db": float(np.mean(snr)), "p05_snr_db": float(np.percentile(snr, 5)),
                "outage_rate": float(np.mean(snr < link.outage_threshold_db)),
                "terminal_x_m": float(result.candidate.states[-1, 0]),
                "terminal_y_m": float(result.candidate.states[-1, 1]),
            })

    df = pd.DataFrame(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    summary = df.groupby("planner", as_index=False).agg(
        n=("window", "count"), feasible_rate=("feasible", "mean"),
        mean_snr_db=("mean_snr_db", "mean"), p05_snr_db=("p05_snr_db", "mean"),
        outage_rate=("outage_rate", "mean"), runtime_ms=("runtime_ms", "mean"),
    )
    summary.to_csv(args.output.with_name(args.output.stem + "_summary.csv"), index=False)
    print(summary.to_string(index=False))
    print("Scientific status: real CMHT target motion + simulated ego planning + geometry link surrogate.")


if __name__ == "__main__":
    main()
