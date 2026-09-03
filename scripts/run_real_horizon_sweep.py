"""Run a real-data trajectory-prediction horizon sweep on CMHT annotations.

This is a real-target-motion benchmark, not a real-world closed-loop driving test.
It evaluates CV and CA on contiguous CMHT annotation windows at multiple future
horizons and writes per-window and summary CSVs plus a paper-ready figure.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_predictor import constant_acceleration, constant_velocity
from iscai.prediction.trajectory_metrics import ade, fde
from iscai.evaluation.statistics import paired_bootstrap_delta, paired_wilcoxon


def contiguous_windows(rows, history, horizon):
    by_id = {}
    for row in rows:
        by_id.setdefault(row[4], []).append(row)
    for oid, seq in by_id.items():
        seq = sorted(seq, key=lambda r: r[0])
        for i in range(history, len(seq) - horizon + 1):
            block = seq[i-history:i+horizon]
            frames = np.asarray([r[0] for r in block])
            if np.all(np.diff(frames) == 1):
                hist = np.asarray([[r[1], r[2]] for r in seq[i-history:i]], float)
                fut = np.asarray([[r[1], r[2]] for r in seq[i:i+horizon]], float)
                yield oid, int(seq[i][0]), hist, fut


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--history-s", type=float, default=1.0)
    p.add_argument("--dt", type=float, default=0.1)
    p.add_argument("--horizons", type=float, nargs="+", default=[0.5, 1.0, 2.0, 3.0, 5.0])
    p.add_argument("--output-dir", type=Path, default=Path("results/real_horizon_sweep"))
    args = p.parse_args()

    rows = extract_object_positions(args.labels)
    history = max(3, int(round(args.history_s / args.dt)))
    records = []
    for hs in args.horizons:
        horizon = max(1, int(round(hs / args.dt)))
        for oid, start_frame, hist, truth in contiguous_windows(rows, history, horizon):
            for name, fn in (("CV", constant_velocity), ("CA", constant_acceleration)):
                pred = fn(hist, horizon, args.dt)
                records.append({
                    "object_id": oid,
                    "start_frame": start_frame,
                    "model": name,
                    "horizon_s": hs,
                    "ADE_m": ade(pred, truth),
                    "FDE_m": fde(pred, truth),
                })

    df = pd.DataFrame(records)
    if df.empty:
        raise SystemExit("No contiguous CMHT windows were found for the requested horizons.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output_dir / "per_window.csv", index=False)

    summary = df.groupby(["model", "horizon_s"], as_index=False).agg(
        n_windows=("FDE_m", "count"),
        ADE_mean_m=("ADE_m", "mean"),
        ADE_median_m=("ADE_m", "median"),
        FDE_mean_m=("FDE_m", "mean"),
        FDE_median_m=("FDE_m", "median"),
        FDE_p95_m=("FDE_m", lambda x: np.percentile(x, 95)),
    )
    summary.to_csv(args.output_dir / "summary.csv", index=False)

    tests = []
    for hs in sorted(df.horizon_s.unique()):
        wide = df[df.horizon_s == hs].pivot_table(
            index=["object_id", "start_frame"], columns="model", values="FDE_m", aggfunc="first"
        ).dropna()
        if {"CV", "CA"}.issubset(wide.columns) and len(wide):
            boot = paired_bootstrap_delta(wide["CV"].to_numpy(), wide["CA"].to_numpy())
            wil = paired_wilcoxon(wide["CV"].to_numpy(), wide["CA"].to_numpy())
            tests.append({"horizon_s": hs, "n_pairs": len(wide), **boot, **wil})
    pd.DataFrame(tests).to_csv(args.output_dir / "paired_tests_CA_minus_CV.csv", index=False)

    plt.figure(figsize=(7, 5))
    for model, g in summary.groupby("model"):
        g = g.sort_values("horizon_s")
        plt.plot(g["horizon_s"], g["FDE_mean_m"], marker="o", label=model)
    plt.xlabel("Prediction horizon (s)")
    plt.ylabel("Mean FDE (m)")
    plt.title("CMHT real-target trajectory prediction horizon sweep")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output_dir / "fde_vs_horizon.png", dpi=220)
    plt.close()

    print(summary.to_string(index=False))
    print(f"Saved real-data horizon benchmark to {args.output_dir}")


if __name__ == "__main__":
    main()
