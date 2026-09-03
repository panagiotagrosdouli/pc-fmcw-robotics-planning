"""Windowing utilities for real trajectory tables."""

from __future__ import annotations

import numpy as np


def make_windows(rows, history=8, horizon=12):
    """Create history/future windows from rows sorted by frame.

    Expected columns: frame, x, y, z, object_id, class.
    Windows are only emitted for contiguous frame indices of one object.
    """
    by_id = {}
    for row in rows:
        by_id.setdefault(row[4], []).append(row)

    samples = []
    for object_id, seq in by_id.items():
        seq = sorted(seq, key=lambda r: r[0])
        for i in range(len(seq) - history - horizon + 1):
            block = seq[i:i + history + horizon]
            frames = np.asarray([r[0] for r in block])
            if not np.all(np.diff(frames) == 1):
                continue
            xy = np.asarray([[r[1], r[2]] for r in block], dtype=float)
            samples.append({
                "object_id": object_id,
                "history": xy[:history],
                "future": xy[history:],
            })
    return samples
