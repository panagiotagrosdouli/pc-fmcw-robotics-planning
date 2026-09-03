"""Rad-R dataset discovery and HDF5 loading utilities.

The loader deliberately does not assume a fixed Rad-R file layout. It inspects
HDF5 groups/datasets first, then exposes small, explicit helpers for arrays.
Large raw radar files should remain outside Git and be referenced through
DATA_ROOT.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import h5py
import numpy as np


@dataclass(frozen=True)
class DatasetItem:
    path: Path
    kind: str
    shape: tuple[int, ...] | None
    dtype: str | None


def discover(root: str | Path) -> list[DatasetItem]:
    """Recursively discover HDF5 datasets under *root*."""
    root = Path(root)
    items: list[DatasetItem] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".h5", ".hdf5", ".hdf"}:
            continue
        with h5py.File(path, "r") as f:
            def visitor(name, obj):
                if isinstance(obj, h5py.Dataset):
                    items.append(DatasetItem(path, name, tuple(obj.shape), str(obj.dtype)))
            f.visititems(visitor)
    return items


def iter_files(root: str | Path) -> Iterator[Path]:
    root = Path(root)
    yield from (p for p in sorted(root.rglob("*")) if p.suffix.lower() in {".h5", ".hdf5", ".hdf"})


def read_dataset(file_path: str | Path, dataset_path: str, *, start=None, stop=None) -> np.ndarray:
    """Read one HDF5 dataset, optionally selecting the first axis range."""
    with h5py.File(file_path, "r") as f:
        ds = f[dataset_path]
        if start is None and stop is None:
            return np.asarray(ds)
        return np.asarray(ds[start:stop])


def print_inventory(root: str | Path) -> None:
    """Print a compact inventory suitable for a first dataset inspection."""
    for item in discover(root):
        print(f"{item.path} :: {item.kind} :: shape={item.shape} :: dtype={item.dtype}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    args = parser.parse_args()
    print_inventory(args.root)
