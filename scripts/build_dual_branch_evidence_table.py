#!/usr/bin/env python3
"""Build a paper-facing evidence table without mixing incompatible QoS units.

The script reads already-produced within-branch statistical outputs and writes a single
CSV/Markdown evidence table. It never computes an optical-vs-5G effect size; it only
places supported within-branch findings side by side.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def fmt(v, digits=4):
    if pd.isna(v):
        return "NA"
    return f"{float(v):.{digits}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pc-effects", default="results/paper/benchmark/paired_effects.csv")
    ap.add_argument("--v2x-effects", default="results/real_v2x_replay/paired_planner_effects.csv")
    ap.add_argument("--output-dir", default="results/dual_branch")
    args = ap.parse_args()

    pc_path = Path(args.pc_effects)
    v2x_path = Path(args.v2x_effects)
    if not pc_path.exists():
        raise SystemExit(f"missing PC-FMCW effects: {pc_path}")
    if not v2x_path.exists():
        raise SystemExit(f"missing V2X effects: {v2x_path}")

    pc = pd.read_csv(pc_path)
    vx = pd.read_csv(v2x_path)
    rows = []

    pc_targets = [
        ("mean_outage_probability", "PC-FMCW modeled outage", "P1", "P2"),
        ("mean_snr_db", "PC-FMCW modeled SNR", "P1", "P2"),
        ("mean_ber_model", "PC-FMCW modeled BER", "P1", "P2"),
        ("mean_goodput_bps_model", "PC-FMCW modeled goodput", "P1", "P2"),
    ]
    for metric, label, a, b in pc_targets:
        q = pc[(pc.metric == metric) & (pc.planner_a == a) & (pc.planner_b == b)]
        if len(q) != 1:
            continue
        r = q.iloc[0]
        rows.append({
            "branch": "PC-FMCW-informed model-based",
            "endpoint": label,
            "comparison": f"{b}-{a}",
            "effect": r.mean_delta_b_minus_a,
            "ci95_low": r.ci95_low,
            "ci95_high": r.ci95_high,
            "raw_p": r.wilcoxon_p,
            "holm_p": r.holm_p,
            "evidence_type": "controlled modeled optical-link output",
            "interpretation_boundary": "not measured optical-hardware validation",
        })

    v2x_targets = [
        ("mean_measured_delay_ms", "Measured V2X delay", "P2-P1"),
        ("violation_fraction", "Measured V2X >threshold fraction", "P2-P1"),
        ("unsupported_fraction", "Unsupported-selection fraction", "P3-P2"),
        ("mean_mobility_deviation", "Mobility deviation", "P3-P2"),
    ]
    for metric, label, comp in v2x_targets:
        q = vx[(vx.metric == metric) & (vx.comparison == comp)]
        if len(q) != 1:
            continue
        r = q.iloc[0]
        rows.append({
            "branch": "Field-measured V2X replay",
            "endpoint": label,
            "comparison": comp,
            "effect": r.mean_delta,
            "ci95_low": r.ci95_lo,
            "ci95_high": r.ci95_hi,
            "raw_p": r.wilcoxon_p,
            "holm_p": r.holm_p if "holm_p" in vx.columns else float("nan"),
            "evidence_type": "field-measured communication outcome under offline route replay",
            "interpretation_boundary": "not arbitrary off-route or closed-loop vehicle validation",
        })

    out = pd.DataFrame(rows)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out.to_csv(outdir / "evidence_table.csv", index=False)

    md = [
        "# Cross-branch evidence table",
        "",
        "Effects are within-branch only; incompatible optical and 5G quantities are not numerically pooled.",
        "",
        "| Branch | Endpoint | Comparison | Effect | 95% CI | Raw p | Holm p | Evidence boundary |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for _, r in out.iterrows():
        md.append(
            f"| {r.branch} | {r.endpoint} | {r.comparison} | {fmt(r.effect)} | "
            f"[{fmt(r.ci95_low)}, {fmt(r.ci95_high)}] | {fmt(r.raw_p)} | "
            f"{fmt(r.holm_p)} | {r.interpretation_boundary} |"
        )
    (outdir / "evidence_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
