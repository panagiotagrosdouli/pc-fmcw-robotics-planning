"""Prepare CMHT frame labels into a compact trajectory table.

A timestamp file is optional because releases/layouts differ. When supplied,
its ordered timestamps are explicitly joined to annotation frame indices; the
output then contains physical time and can support timing-aware experiments.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.data.cmht_loader import extract_object_positions, timestamp_map


parser = argparse.ArgumentParser()
parser.add_argument("--labels", required=True)
parser.add_argument("--timestamps", default=None, help="Ordered CMHT timestamp text file aligned to annotation frames")
parser.add_argument("--frame-start", type=int, default=0, help="First annotation frame represented by the timestamp file")
parser.add_argument("--output", default="data/processed/cmht_tracks.csv")
parser.add_argument("--class-name", default=None)
args = parser.parse_args()

ts = None
if args.timestamps:
    raw_lines = Path(args.timestamps).read_text(errors="ignore").splitlines()
    numeric_count = 0
    for line in raw_lines:
        try:
            float(line.strip().split()[0]); numeric_count += 1
        except (ValueError, IndexError):
            pass
    frames = range(args.frame_start, args.frame_start + numeric_count)
    ts = timestamp_map(args.timestamps, frames=frames)

rows = extract_object_positions(args.labels, class_name=args.class_name, timestamps=ts)
columns = ["frame", "timestamp", "x", "y", "z", "object_id", "class"] if ts is not None else ["frame", "x", "y", "z", "object_id", "class"]
df = pd.DataFrame(rows, columns=columns)
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
mode = "timestamp-aware" if ts is not None else "frame-indexed"
print(f"Wrote {len(df)} labeled object observations to {out} ({mode})")
