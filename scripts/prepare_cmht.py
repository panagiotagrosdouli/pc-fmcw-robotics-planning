"""Prepare CMHT frame labels into a compact trajectory table.

Usage:
    python scripts/prepare_cmht.py --labels /path/to/label --output data/processed/cmht_tracks.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.data.cmht_loader import extract_object_positions


parser = argparse.ArgumentParser()
parser.add_argument("--labels", required=True)
parser.add_argument("--output", default="data/processed/cmht_tracks.csv")
parser.add_argument("--class-name", default=None)
args = parser.parse_args()

rows = extract_object_positions(args.labels, class_name=args.class_name)
df = pd.DataFrame(rows, columns=["frame", "x", "y", "z", "object_id", "class"])
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f"Wrote {len(df)} labeled object observations to {out}")
