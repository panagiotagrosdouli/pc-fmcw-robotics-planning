#!/usr/bin/env python3
"""Generate the compact Paper-1 LaTeX result table from archived evidence."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

LABELS = {
    "mean_outage_probability": "Outage probability",
    "mean_snr_db": "Mean SNR (dB)",
    "min_snr_db": "Minimum SNR (dB)",
    "mean_ber_model": "Modeled BER",
    "mean_goodput_bps_model": "Goodput (Mbit/s)",
}


def compact(value: float) -> str:
    return f"{value:.4g}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = list(csv.DictReader(args.input.open(newline="", encoding="utf-8")))
    rows = [row for row in rows if row["comparison"] == "P2-P1"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        "Endpoint & Effect & 95\\% CI & $p_H$ \\\\",
        r"\midrule",
    ]
    for row in rows:
        scale = 1e-6 if row["metric"] == "mean_goodput_bps_model" else 1.0
        effect = float(row["mean_seed_delta_b_minus_a"]) * scale
        low = float(row["ci95_low"]) * scale
        high = float(row["ci95_high"]) * scale
        lines.append(
            f"{LABELS[row['metric']]} & {compact(effect)} & "
            f"[{compact(low)}, {compact(high)}] & {float(row['holm_p']):.2g} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    args.out.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
