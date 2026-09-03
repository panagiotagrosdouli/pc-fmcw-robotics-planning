"""Download the public Rad-R v1.0 dataset outside the Git repository.

The dataset is large; keep it under data/raw/radr locally and do not commit it.

Usage:
    python scripts/download_radr.py --output data/raw/radr
    python scripts/download_radr.py --output data/raw/radr --include synced_hdf5 training_cache.h5
"""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

REPO_ID = "radr-anon-2026/radr"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw/radr"))
    parser.add_argument(
        "--include",
        nargs="*",
        default=None,
        help="Optional HF file/folder patterns. Default downloads the public dataset snapshot.",
    )
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        local_dir=str(args.output),
        allow_patterns=args.include,
    )
    print(f"Rad-R downloaded to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
