#!/usr/bin/env python3
"""Generate a manuscript-facing Part B report strictly from frozen-run artifacts."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

PRIMARY_METRICS = [
    "mean_outage_probability",
    "mean_snr_db",
    "min_snr_db",
    "mean_ber_model",
    "mean_goodput_bps_model",
]
PRIMARY_COMPARISONS = [("P1", "P2"), ("P2", "P3"), ("P2", "P4")]


def f(v, digits=6):
    return "NA" if pd.isna(v) else f"{float(v):.{digits}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default="results/part_b_final")
    ap.add_argument("--output", default="results/part_b_final/CONFIRMATORY_REPORT.md")
    args = ap.parse_args()
    root = Path(args.input_dir)
    episodes = pd.read_csv(root / "episodes.csv")
    effects = pd.read_csv(root / "paired_effects.csv")
    scen = pd.read_csv(root / "diagnostics" / "scenario_safety_prediction.csv")
    planner_diag = pd.read_csv(root / "diagnostics" / "planner_safety_prediction.csv")
    manifest = json.loads((root / "manifest.json").read_text())

    seed_values = sorted(episodes.seed.unique().tolist())
    lines = [
        "# Part B final-v1 confirmatory report",
        "",
        "This report is generated only from the frozen confirmatory artifacts. It does not import historical baseline numbers.",
        "",
        "## Provenance",
        "",
        f"- Seed count: {len(seed_values)}",
        f"- Seed range: {seed_values[0]}..{seed_values[-1]}",
        f"- Claim boundary: {manifest.get('claim_boundary', 'controlled model-based simulation')}",
        "",
        "## Planner means",
        "",
    ]
    means = episodes.groupby("planner", as_index=False).agg(
        outage=("mean_outage_probability", "mean"),
        snr_db=("mean_snr_db", "mean"),
        min_snr_db=("min_snr_db", "mean"),
        ber=("mean_ber_model", "mean"),
        goodput_bps=("mean_goodput_bps_model", "mean"),
        progress_m=("progress_m", "mean"),
        path_length_m=("path_length_m", "mean"),
        collision_rate=("collision_indicator", "mean"),
        no_candidate_steps=("no_candidate_steps", "mean"),
    )
    lines += [
        "| Planner | Outage | SNR dB | Min SNR dB | BER | Goodput bps | Progress m | Path length m | Collision rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in means.iterrows():
        lines.append(
            f"| {r.planner} | {f(r.outage)} | {f(r.snr_db)} | {f(r.min_snr_db)} | {f(r.ber)} | "
            f"{f(r.goodput_bps, 1)} | {f(r.progress_m, 3)} | {f(r.path_length_m, 3)} | {f(r.collision_rate, 3)} |"
        )

    lines += ["", "## Predeclared communication comparisons", ""]
    lines += [
        "| Comparison | Metric | Mean delta (B-A) | 95% CI | Raw p | Holm p |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for a, b in PRIMARY_COMPARISONS:
        for metric in PRIMARY_METRICS:
            q = effects[(effects.planner_a == a) & (effects.planner_b == b) & (effects.metric == metric)]
            if len(q) != 1:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {b}-{a} | {metric} | {f(r.mean_delta_b_minus_a)} | "
                f"[{f(r.ci95_low)}, {f(r.ci95_high)}] | {f(r.wilcoxon_p)} | {f(r.holm_p)} |"
            )

    lines += [
        "",
        "## Safety/feasibility gate",
        "",
        "Safety outcomes are diagnostic/gating evidence, not automatically part of the communication claim.",
        "",
        "| Planner | Episodes | Collision rate | Mean no-candidate steps | Prediction ADE m | Prediction FDE m |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in planner_diag.iterrows():
        lines.append(
            f"| {r.planner} | {int(r.episodes)} | {f(r.collision_rate,3)} | {f(r.mean_no_candidate_steps,3)} | "
            f"{f(r.prediction_ade_m,3)} | {f(r.prediction_fde_m,3)} |"
        )

    lines += [
        "",
        "## Scenario diagnostic warning",
        "",
        "The existence of a planner-level mean does not license a safety claim. Scenario-level collision/no-candidate behavior must be inspected, especially if failures cluster in a small subset of scenarios.",
        "",
        "## Claim rules",
        "",
        "- A communication effect is called confirmatory only for the predeclared P2-P1, P3-P2 or P4-P2 comparison and the five predeclared communication metrics.",
        "- Holm-adjusted p-values are reported with paired bootstrap confidence intervals; practical effect size remains necessary even when p is small.",
        "- No optical measurement, hardware, or real-road claim follows from this run.",
        "- If the 50-seed result disagrees with the historical 20-seed baseline, the confirmatory result takes precedence for final-v1 claims.",
        "- Negative P3/P4 results are retained.",
        "",
        "## Scenario coverage",
        "",
    ]
    for scenario in sorted(scen.scenario.unique()):
        lines.append(f"- {scenario}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
