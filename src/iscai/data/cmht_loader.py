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


def read_label(path: str | Path) -> list[dict]:
    """Return the frame's 3D tracklet objects as dictionaries."""
    obj = json.loads(Path(path).read_text())
    if isinstance(obj, list):
        return obj
    for key in ("objects", "labels", "tracklets", "detections"):
        if key in obj and isinstance(obj[key], list):
            return obj[key]
    return [obj] if isinstance(obj, dict) else []


def extract_object_positions(label_dir: str | Path, object_id=None, class_name=None):
    """Build a frame-indexed position table from CMHT JSON labels.

    Returns columns [frame, x, y, z, object_id, class]. Field aliases are handled
    conservatively because public releases may use slightly different JSON keys.
    """
    rows = []
    for path in sorted(Path(label_dir).glob("*.json")):
        try:
            frame = int(path.stem)
        except ValueError:
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
                x, y, z = pos[:3]
            else:
                x, y, z = item.get("x"), item.get("y"), item.get("z", 0.0)
            if x is None or y is None:
                continue
            rows.append([frame, float(x), float(y), float(z or 0.0), oid, str(cls)])
    return rows
