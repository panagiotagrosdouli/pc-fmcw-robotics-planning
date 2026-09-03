"""Paper-grade paired analysis of CMHT planner replay results.

Consumes ``cmht_planner_replay.csv`` produced on identical CMHT windows for
P0-P4. It never fabricates missing planners or measurements.
"""
from __future__ import annotations
import argparse
import sys
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.evaluation.statistics import paired_bootstrap_delta, paired_wilcoxon, holm_adjust, pareto_mask

METRICS = {
    "outage_rate": True,
    "mean_snr_db": False,
    "p05_snr_db": False,
    "runtime_ms": True,
}


def paired_records(df, metric):
    good = df[df["feasible"].astype(bool) & df[metric].notna()].copy()
    out = []
    for a, b in combinations(sorted(good.planner.unique()), 2):
        wide = good[good.planner.isin([a, b])].pivot_table(
            index=["window", "object_id", "link_model"], columns="planner", values=metric, aggfunc="first"
        ).dropna()
        if not {a, b}.issubset(wide.columns) or wide.empty:
            continue
        av, bv = wide[a].to_numpy(float), wide[b].to_numpy(float)
        boot = paired_bootstrap_delta(av, bv)
        wil = paired_wilcoxon(av, bv)
        out.append({
            "metric": metric, "planner_a": a, "planner_b": b, "n_pairs": len(wide),
            "mean_a": float(av.mean()), "mean_b": float(bv.mean()),
            "delta_b_minus_a": boot["mean_delta"], "ci95_low": boot["ci_low"],
            "ci95_high": boot["ci_high"], "wilcoxon_statistic": wil["statistic"],
            "pvalue": wil["pvalue"],
        })
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("results/cmht_planner_replay.csv"))
    p.add_argument("--output-dir", type=Path, default=Path("results/cmht_planner_analysis"))
    args = p.parse_args()
    if not args.input.exists():
        raise SystemExit(f"Replay results not found: {args.input}")
    df = pd.read_csv(args.input)
    required = {"window", "object_id", "planner", "feasible", "link_model"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing replay columns: {sorted(missing)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for metric in METRICS:
        if metric in df.columns:
            records.extend(paired_records(df, metric))
    stats = pd.DataFrame(records)
    if not stats.empty:
        stats["pvalue_holm"] = np.nan
        for metric, idx in stats.groupby("metric").groups.items():
            stats.loc[idx, "pvalue_holm"] = holm_adjust(stats.loc[idx, "pvalue"].to_numpy(float))
        stats["significant_0p05_holm"] = stats["pvalue_holm"] < 0.05
    stats.to_csv(args.output_dir / "paired_statistics.csv", index=False)

    summary = df[df.feasible.astype(bool)].groupby(["planner", "link_model"], as_index=False).agg(
        n_windows=("window", "count"), outage_rate=("outage_rate", "mean"),
        mean_snr_db=("mean_snr_db", "mean"), p05_snr_db=("p05_snr_db", "mean"),
        runtime_ms=("runtime_ms", "mean"),
    )
    if not summary.empty:
        vals = summary[["outage_rate", "runtime_ms"]].to_numpy(float)
        summary["pareto_outage_runtime"] = pareto_mask(vals, minimize=[True, True])
    summary.to_csv(args.output_dir / "planner_summary_pareto.csv", index=False)

    if not summary.empty:
        plt.figure(figsize=(7, 5))
        for _, r in summary.iterrows():
            marker = "o" if r.get("pareto_outage_runtime", False) else "x"
            plt.scatter(r.runtime_ms, r.outage_rate, marker=marker)
            plt.annotate(r.planner, (r.runtime_ms, r.outage_rate))
        plt.xlabel("Mean planning runtime (ms)")
        plt.ylabel("Mean outage rate")
        plt.title("CMHT replay: outage-runtime Pareto trade-off")
        plt.tight_layout()
        plt.savefig(args.output_dir / "pareto_outage_runtime.png", dpi=220)
        plt.close()

    print(summary.to_string(index=False))
    print(f"Saved paired statistics and Pareto analysis to {args.output_dir}")

if __name__ == "__main__":
    main()
