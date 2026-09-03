"""Build a machine-readable real trajectory table from CMHT JSON labels.

Input is the extracted CMHT ``label`` directory. Output is CSV and contains
only positions that are explicitly present in the published annotations.
No synthetic samples are generated here.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.data.cmht_loader import extract_object_positions


def main():
    p = argparse.ArgumentParser()
    p.add_argument("label_dir")
    p.add_argument("--output", default="data/processed/cmht_trajectories.csv")
    p.add_argument("--class", dest="class_name", default=None)
    args = p.parse_args()

    rows = extract_object_positions(args.label_dir, class_name=args.class_name)
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["frame", "x", "y", "z", "object_id", "class"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} real annotation rows to {out}")


if __name__ == "__main__":
    main()
