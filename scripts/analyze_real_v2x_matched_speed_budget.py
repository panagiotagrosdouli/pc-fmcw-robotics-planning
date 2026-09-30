#!/usr/bin/env python3
"""Fixed-intervention-budget evaluation for matched-speed replay.

This avoids converting seconds of mobility cost into an arbitrary millisecond QoS
weight. A policy may select SLOW for at most a declared fraction of supported query
locations. Ranking is based on predicted communication gain; the matched oracle ranks
using measured donor gain and is nondeployable.

Outputs are development diagnostics until donor-run dependence is handled explicitly.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def choose_mask(
    g: pd.DataFrame,
    score_col: str,
    budget: float,
    support_required: bool = False,
) -> np.ndarray:
    n = len(g)
    k = int(np.floor(float(budget) * n))
    if budget > 0 and k == 0 and n > 0:
        k = 1
    eligible = np.ones(n, dtype=bool)
    if support_required:
        eligible &= g["slow_train_supported"].astype(bool).to_numpy()
        eligible &= g["fast_train_supported"].astype(bool).to_numpy()
    score = g[score_col].to_numpy(float)
    eligible &= np.isfinite(score)
    # The intervention budget is a maximum, not a requirement: never slow when the
    # estimated communication gain is non-positive.
    eligible &= score > 0
    idx = np.where(eligible)[0]
    if len(idx) == 0 or k <= 0:
        return np.zeros(n, dtype=bool)
    ranked = idx[np.argsort(-score[idx], kind="stable")]
    chosen = ranked[: min(k, len(ranked))]
    mask = np.zeros(n, dtype=bool)
    mask[chosen] = True
    return mask


def evaluate(g: pd.DataFrame, slow_mask: np.ndarray) -> dict:
    fast = g["measured_fast_delay_ms"].to_numpy(float)
    slow = g["measured_slow_delay_ms"].to_numpy(float)
    y = np.where(slow_mask, slow, fast)
    return {
        "n": int(len(y)),
        "mean_matched_delay_ms": float(np.mean(y)),
        "p95_matched_delay_ms": float(np.quantile(y, 0.95)),
        "slow_fraction": float(np.mean(slow_mask)),
        "mean_delay_gain_vs_fast_ms": float(np.mean(fast) - np.mean(y)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/real_v2x_matched_speed")
    ap.add_argument("--budgets", default="0.01,0.05,0.10")
    args = ap.parse_args()

    root = Path(args.input)
    d = pd.read_csv(root / "comparison_contexts.csv")
    budgets = [float(x) for x in args.budgets.split(",")]

    rows = []
    for run_id, g0 in d.groupby("query_run_id", sort=False):
        g = g0.reset_index(drop=True)
        for budget in budgets:
            policies = {
                "FAST": np.zeros(len(g), dtype=bool),
                "PRED_BUDGET": choose_mask(
                    g, "pred_fast_minus_slow_gain_ms", budget, support_required=False
                ),
                "PRED_SUPPORT_BUDGET": choose_mask(
                    g, "pred_fast_minus_slow_gain_ms", budget, support_required=True
                ),
                "ORACLE_BUDGET": choose_mask(
                    g, "measured_fast_minus_slow_gain_ms", budget, support_required=False
                ),
            }
            for mode, mask in policies.items():
                m = evaluate(g, mask)
                rows.append({
                    "query_run_id": run_id,
                    "budget": budget,
                    "mode": mode,
                    **m,
                })

    per_run = pd.DataFrame(rows)
    per_run.to_csv(root / "budget_run_metrics.csv", index=False)

    summary = per_run.groupby(["budget", "mode"]).agg(
        query_runs=("query_run_id", "nunique"),
        mean_delay_ms=("mean_matched_delay_ms", "mean"),
        mean_p95_delay_ms=("p95_matched_delay_ms", "mean"),
        mean_slow_fraction=("slow_fraction", "mean"),
        mean_gain_vs_fast_ms=("mean_delay_gain_vs_fast_ms", "mean"),
    ).reset_index()
    summary.to_csv(root / "budget_summary.csv", index=False)

    effects = []
    for budget in budgets:
        x = per_run[per_run["budget"] == budget]
        pivot = x.pivot(index="query_run_id", columns="mode", values="mean_matched_delay_ms")
        for mode in ("PRED_BUDGET", "PRED_SUPPORT_BUDGET", "ORACLE_BUDGET"):
            delta = (pivot[mode] - pivot["FAST"]).dropna()
            effects.append({
                "budget": budget,
                "comparison": f"{mode}-FAST",
                "n_query_runs": int(len(delta)),
                "mean_delta_ms": float(delta.mean()),
                "min_run_delta_ms": float(delta.min()),
                "max_run_delta_ms": float(delta.max()),
                "favorable_query_runs": int((delta < 0).sum()),
                "unfavorable_query_runs": int((delta > 0).sum()),
                "inference_status": (
                    "development descriptive only; shared donor-run dependence remains"
                ),
            })
    pd.DataFrame(effects).to_csv(root / "budget_effects_development.csv", index=False)

    print(summary.to_string(index=False))
    print(pd.DataFrame(effects).to_string(index=False))


if __name__ == "__main__":
    main()
