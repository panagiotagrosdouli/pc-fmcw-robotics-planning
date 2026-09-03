"""CMHT autonomous-driving dataset utilities.

Supports the extracted frame-by-frame release: radar/LiDAR PCD, GPS/IMU TXT,
3D tracklet JSON labels, and per-sensor timestamps. Large files stay outside Git.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def read_pcd_xyzv(path: str | Path) -> np.ndarray:
    """Read an ASCII PCD containing x,y,z,v fields."""
    path = Path(path)
    lines = path.read_text(errors="ignore").splitlines()
    data_idx = next(i for i, line in enumerate(lines) if line.strip().lower().startswith("data "))
    if lines[data_idx].strip().lower() != "data ascii":
        raise ValueError(f"Only ASCII PCD is supported by this lightweight loader: {path}")
    rows = [np.fromstring(line, sep=" ") for line in lines[data_idx + 1:] if line.strip()]
    return np.vstack(rows) if rows else np.empty((0, 4), dtype=float)


def read_timestamp_file(path: str | Path) -> np.ndarray:
    values = []
    for line in Path(path).read_text(errors="ignore").splitlines():
        line = line.strip()
        if line:
            try:
                values.append(float(line.split()[0]))
            except ValueError:
                continue
    return np.asarray(values, dtype=float)


def timestamp_map(path: str | Path, frames=None) -> dict[int, float]:
    """Map frame indices to timestamps without inventing alignment.

    If ``frames`` is omitted, timestamps are assigned to zero-based frame
    indices in file order. If supplied, it must have exactly one frame index
    per timestamp; this is useful when a release provides an explicit frame
    ordering. Timestamps must be finite and strictly increasing.
    """
    ts = read_timestamp_file(path)
    if ts.size == 0:
        raise ValueError(f"No numeric timestamps found in {path}")
    if not np.all(np.isfinite(ts)) or np.any(np.diff(ts) <= 0):
        raise ValueError("CMHT timestamps must be finite and strictly increasing")
    if frames is None:
        frames = np.arange(len(ts), dtype=int)
    else:
        frames = np.asarray(frames, dtype=int)
        if len(frames) != len(ts):
            raise ValueError("frames and timestamps must have identical length")
        if len(np.unique(frames)) != len(frames):
            raise ValueError("frame indices must be unique")
    return {int(frame): float(t) for frame, t in zip(frames, ts)}


def read_label(path: str | Path) -> list[dict]:
    """Return the frame's 3D tracklet objects as dictionaries."""
    obj = json.loads(Path(path).read_text())
    if isinstance(obj, list):
        return obj
    for key in ("objects", "labels", "tracklets", "detections"):
        if key in obj and isinstance(obj[key], list):
            return obj[key]
    return [obj] if isinstance(obj, dict) else []


def extract_object_positions(label_dir: str | Path, object_id=None, class_name=None, timestamps=None):
    """Build a frame-indexed position table from CMHT JSON labels.

    By default returns [frame, x, y, z, object_id, class]. If ``timestamps`` is
    supplied as a frame->time mapping, returns [frame, timestamp, x, y, z,
    object_id, class] and skips frames absent from that mapping. This explicit
    join prevents silently treating annotation frame numbers as physical time.
    """
    rows = []
    for path in sorted(Path(label_dir).glob("*.json")):
        try:
            frame = int(path.stem)
        except ValueError:
            continue
        if timestamps is not None and frame not in timestamps:
            continue
        for item in read_label(path):
            oid = item.get("id", item.get("object_id", item.get("track_id")))
            cls = item.get("class", item.get("classification", item.get("label", "unknown")))
            if object_id is not None and oid != object_id:
                continue
            if class_name is not None and str(cls).lower() != str(class_name).lower():
                continue
            pos = item.get("position", item.get("center", item.get("location")))
            if isinstance(pos, dict):
                x, y, z = pos.get("x"), pos.get("y"), pos.get("z", 0.0)
            elif isinstance(pos, (list, tuple)) and len(pos) >= 2:
                vals = list(pos) + [0.0]
                x, y, z = vals[:3]
            else:
                x, y, z = item.get("x"), item.get("y"), item.get("z", 0.0)
            if x is None or y is None:
                continue
            base = [frame, float(x), float(y), float(z or 0.0), oid, str(cls)]
            if timestamps is None:
                rows.append(base)
            else:
                rows.append([frame, float(timestamps[frame]), *base[1:]])
    return rows
