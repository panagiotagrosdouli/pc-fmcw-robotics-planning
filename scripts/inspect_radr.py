"""Inspect a downloaded Rad-R directory without loading large arrays."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iscai.data.radr_loader import print_inventory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect Rad-R HDF5 contents")
    parser.add_argument("root", nargs="?", default="data/raw/radr")
    args = parser.parse_args()
    print_inventory(args.root)
