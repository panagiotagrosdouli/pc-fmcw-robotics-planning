#!/usr/bin/env python3
"""Locked two-way acquisition-run bootstrap for matched-speed decision evidence.

The estimator resamples query acquisition runs and donor acquisition runs
independently. Donor-weighted matched outcomes are reconstructed inside each
replicate from donor_contributions.csv. Deployable policy rankings remain frozen;
the measured oracle ranking is recomputed inside each replicate and is interpreted
only as a support-bounded upper-bound diagnostic.

This script implements docs/PAPER2_CONFIRMATORY_FREEZE_2026-09-30.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


POLICIES = ("FAST", "PRED_BUDGET", "MARGIN_BUDGET", "ORACLE_BUDGET")


def _choose_mask(score: np.ndarray, budget: float, support: np.ndarray | None = None) -> np.ndarray:
    n = len(score)
    k = int(np.floor(float(budget) * n))
    if budget > 0 and k == 0 and n > 0:
        k = 1
    eligible = np.isfinite(score) & (score > 0)
    if support is not None:
        eligible &= support
    idx = np.flatnonzero(eligible)
    out = np.zeros(n, dtype=bool)
    if k <= 0 or len(idx) == 0:
        return out
    ranked = idx[np.argsort(-score[idx], kind="stable")]
    out[ranked[: min(k, len(ranked))]] = True
    return out


def _multinomial_counts(rng: np.random.Generator, n: int) -> np.ndarray:
    # Equivalent to sampling n cluster IDs with replacement.
    return rng.multinomial(n, np.full(n, 1.0 / n))


def _build_donor_matrices(
    contexts: pd.DataFrame,
    contrib: pd.DataFrame,
    slow: float,
    fast: float,
):
    donor_runs = sorted(contrib["donor_run_id"].astype(str).unique().tolist())
    donor_index = {r: i for i, r in enumerate(donor_runs)}
    key_to_context = {
        (str(r.query_run_id), int(r.query_index)): i
        for i, r in contexts[["query_run_id", "query_index"]].reset_index(drop=True).iterrows()
    }
    n = len(contexts)
    d = len(donor_runs)
    num_slow = np.zeros((n, d), dtype=float)
    den_slow = np.zeros((n, d), dtype=float)
    num_fast = np.zeros((n, d), dtype=float)
    den_fast = np.zeros((n, d), dtype=float)

    for row in contrib.itertuples(index=False):
        key = (str(row.query_run_id), int(row.query_index))
        i = key_to_context.get(key)
        if i is None:
            continue
        j = donor_index[str(row.donor_run_id)]
        speed = float(row.action_speed_kmh)
        if np.isclose(speed, slow):
            num_slow[i, j] += float(row.donor_delay_ms)
            den_slow[i, j] += 1.0
        elif np.isclose(speed, fast):
            num_fast[i, j] += float(row.donor_delay_ms)
            den_fast[i, j] += 1.0

    return donor_runs, num_slow, den_slow, num_fast, den_fast


def _outcome(num: np.ndarray, den: np.ndarray, donor_counts: np.ndarray) -> np.ndarray:
    numerator = num @ donor_counts
    denominator = den @ donor_counts
    out = np.full(len(numerator), np.nan, dtype=float)
    ok = denominator > 0
    out[ok] = numerator[ok] / denominator[ok]
    return out


def _evaluate_once(
    contexts: pd.DataFrame,
    query_runs: list[str],
    query_counts: np.ndarray,
    slow_y: np.ndarray,
    fast_y: np.ndarray,
    budget: float,
):
    pred_gain = contexts["pred_fast_minus_slow_gain_ms"].to_numpy(float)
    margin_gain = contexts["margin_pred_gain_ms"].to_numpy(float)
    support = (
        contexts["slow_train_supported"].astype(bool).to_numpy()
        & contexts["fast_train_supported"].astype(bool).to_numpy()
    )
    qid = contexts["query_run_id"].astype(str).to_numpy()

    run_policy_means: dict[str, dict[str, float]] = {}
    run_valid_counts: dict[str, int] = {}

    for run in query_runs:
        base = qid == run
        valid = base & np.isfinite(slow_y) & np.isfinite(fast_y)
        idx = np.flatnonzero(valid)
        if len(idx) == 0:
            continue

        s = slow_y[idx]
        f = fast_y[idx]
        pred = pred_gain[idx]
        margin = margin_gain[idx]
        sup = support[idx]
        oracle_gain = f - s

        masks = {
            "FAST": np.zeros(len(idx), dtype=bool),
            "PRED_BUDGET": _choose_mask(pred, budget, None),
            "MARGIN_BUDGET": _choose_mask(margin, budget, sup),
            "ORACLE_BUDGET": _choose_mask(oracle_gain, budget, None),
        }

        run_policy_means[run] = {}
        for mode, mask in masks.items():
            y = np.where(mask, s, f)
            run_policy_means[run][mode] = float(np.mean(y))
        run_valid_counts[run] = int(len(idx))

    weighted: dict[str, float] = {}
    used_weight = 0
    used_runs = 0
    valid_contexts = 0
    for i, run in enumerate(query_runs):
        count = int(query_counts[i])
        if count <= 0 or run not in run_policy_means:
            continue
        used_weight += count
        used_runs += 1
        valid_contexts += run_valid_counts[run] * count

    if used_weight == 0:
        return None

    for mode in POLICIES:
        total = 0.0
        for i, run in enumerate(query_runs):
            count = int(query_counts[i])
            if count <= 0 or run not in run_policy_means:
                continue
            total += count * run_policy_means[run][mode]
        weighted[mode] = total / used_weight

    effects = {
        "oracle_minus_fast_ms": weighted["ORACLE_BUDGET"] - weighted["FAST"],
        "pred_minus_oracle_ms": weighted["PRED_BUDGET"] - weighted["ORACLE_BUDGET"],
        "pred_minus_fast_ms": weighted["PRED_BUDGET"] - weighted["FAST"],
        "margin_minus_fast_ms": weighted["MARGIN_BUDGET"] - weighted["FAST"],
        "margin_minus_oracle_ms": weighted["MARGIN_BUDGET"] - weighted["ORACLE_BUDGET"],
    }
    return {
        "policy_means": weighted,
        "effects": effects,
        "used_query_cluster_weight": int(used_weight),
        "used_unique_query_runs": int(used_runs),
        "valid_contexts_weighted": int(valid_contexts),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/paper2_confirmatory")
    ap.add_argument("--budget", type=float, default=0.10)
    ap.add_argument("--bootstrap", type=int, default=5000)
    ap.add_argument("--bootstrap-seed", type=int, default=20260930)
    args = ap.parse_args()

    root = Path(args.input)
    contexts = pd.read_csv(root / "comparison_contexts.csv").reset_index(drop=True)
    contrib = pd.read_csv(root / "donor_contributions.csv")

    speeds = sorted(contrib["action_speed_kmh"].astype(float).unique().tolist())
    if len(speeds) != 2:
        raise ValueError(f"expected exactly two actions, found {speeds}")
    slow, fast = min(speeds), max(speeds)

    query_runs = sorted(contexts["query_run_id"].astype(str).unique().tolist())
    if len(query_runs) < 2:
        raise ValueError("at least two query acquisition runs are required")

    donor_runs, num_slow, den_slow, num_fast, den_fast = _build_donor_matrices(
        contexts, contrib, slow, fast
    )
    if len(donor_runs) < 2:
        raise ValueError("at least two donor acquisition runs are required")

    # Point estimate: every observed acquisition run has weight one.
    donor_ones = np.ones(len(donor_runs), dtype=int)
    query_ones = np.ones(len(query_runs), dtype=int)
    slow_point = _outcome(num_slow, den_slow, donor_ones)
    fast_point = _outcome(num_fast, den_fast, donor_ones)
    point = _evaluate_once(
        contexts, query_runs, query_ones, slow_point, fast_point, args.budget
    )
    if point is None:
        raise RuntimeError("locked point estimate has no valid query runs")

    rng = np.random.default_rng(args.bootstrap_seed)
    effect_names = list(point["effects"].keys())
    draws = {k: [] for k in effect_names}
    coverage_rows = []

    for b in range(args.bootstrap):
        donor_counts = _multinomial_counts(rng, len(donor_runs))
        query_counts = _multinomial_counts(rng, len(query_runs))

        slow_y = _outcome(num_slow, den_slow, donor_counts)
        fast_y = _outcome(num_fast, den_fast, donor_counts)
        res = _evaluate_once(
            contexts, query_runs, query_counts, slow_y, fast_y, args.budget
        )
        if res is None:
            continue
        for k in effect_names:
            value = float(res["effects"][k])
            if np.isfinite(value):
                draws[k].append(value)
        coverage_rows.append({
            "replicate": b,
            "used_query_cluster_weight": res["used_query_cluster_weight"],
            "used_unique_query_runs": res["used_unique_query_runs"],
            "valid_contexts_weighted": res["valid_contexts_weighted"],
            "nonzero_donor_runs": int(np.sum(donor_counts > 0)),
        })

    summary_rows = []
    for k in effect_names:
        arr = np.asarray(draws[k], dtype=float)
        if len(arr) == 0:
            raise RuntimeError(f"no finite bootstrap draws for {k}")
        point_value = float(point["effects"][k])
        summary_rows.append({
            "estimand": k,
            "point_estimate_ms": point_value,
            "bootstrap_replicates_requested": int(args.bootstrap),
            "bootstrap_replicates_valid": int(len(arr)),
            "ci95_lo_ms": float(np.quantile(arr, 0.025)),
            "ci95_hi_ms": float(np.quantile(arr, 0.975)),
            "prob_less_than_zero": float(np.mean(arr < 0)),
            "prob_greater_than_zero": float(np.mean(arr > 0)),
        })

    pd.DataFrame(summary_rows).to_csv(root / "confirmatory_two_way_bootstrap.csv", index=False)
    pd.DataFrame(coverage_rows).to_csv(root / "confirmatory_bootstrap_coverage.csv", index=False)

    policy_rows = [
        {"mode": k, "point_mean_delay_ms": float(v)}
        for k, v in point["policy_means"].items()
    ]
    pd.DataFrame(policy_rows).to_csv(root / "confirmatory_policy_point_estimates.csv", index=False)

    meta = {
        "protocol": "PAPER2_CONFIRMATORY_FREEZE_2026-09-30",
        "budget": args.budget,
        "bootstrap_replicates": args.bootstrap,
        "bootstrap_seed": args.bootstrap_seed,
        "query_runs": query_runs,
        "donor_runs": donor_runs,
        "n_query_runs": len(query_runs),
        "n_donor_runs": len(donor_runs),
        "n_contexts": int(len(contexts)),
        "slow_speed_kmh": slow,
        "fast_speed_kmh": fast,
        "oracle_interpretation": (
            "Support-bounded measured upper-bound diagnostic; donor outcomes are used "
            "for ranking and evaluation within a bootstrap replicate, so it is not "
            "an unbiased deployable-policy performance estimate."
        ),
        "inference_boundary": (
            "Two-way acquisition-run bootstrap resamples query and donor clusters. "
            "Finite-run observational replay remains non-causal."
        ),
    }
    (root / "confirmatory_metadata.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )

    print("=== Locked point policy means ===")
    print(pd.DataFrame(policy_rows).to_string(index=False))
    print("\n=== Two-way acquisition-run bootstrap ===")
    print(pd.DataFrame(summary_rows).to_string(index=False))
    print("\n=== Coverage ===")
    cov = pd.DataFrame(coverage_rows)
    print(cov.describe().to_string())


if __name__ == "__main__":
    main()
