"""Lightweight trajectory prediction baselines for real CMHT tracklets."""

from __future__ import annotations

import numpy as np


def _times(n: int, dt: float | None, history_times=None, future_times=None, horizon=None):
    if history_times is None:
        if dt is None or dt <= 0:
            raise ValueError("positive dt is required when history_times is omitted")
        ht = np.arange(n, dtype=float) * dt
    else:
        ht = np.asarray(history_times, dtype=float)
        if ht.shape != (n,) or not np.all(np.isfinite(ht)) or np.any(np.diff(ht) <= 0):
            raise ValueError("history_times must be finite, strictly increasing, and match history length")
        ht = ht - ht[0]
    if future_times is None:
        if dt is None or dt <= 0:
            raise ValueError("positive dt is required when future_times is omitted")
        ft = ht[-1] + np.arange(1, int(horizon) + 1, dtype=float) * dt
    else:
        ft0 = np.asarray(future_times, dtype=float)
        if ft0.shape != (int(horizon),) or not np.all(np.isfinite(ft0)) or np.any(np.diff(ft0) <= 0):
            raise ValueError("future_times must be finite, strictly increasing, and match horizon")
        origin = float(np.asarray(history_times, dtype=float)[0])
        ft = ft0 - origin
        if np.any(ft <= ht[-1]):
            raise ValueError("future_times must occur after the final history timestamp")
    return ht, ft


def constant_velocity(history_xy: np.ndarray, horizon: int, dt: float | None = None, *, history_times=None, future_times=None) -> np.ndarray:
    """Least-squares CV prediction on uniform or explicitly measured time."""
    history_xy = np.asarray(history_xy, dtype=float)
    if history_xy.ndim != 2 or history_xy.shape[1] != 2 or len(history_xy) < 2:
        raise ValueError("history_xy must have shape (N, 2) with N >= 2")
    t, tf = _times(len(history_xy), dt, history_times, future_times, horizon)
    out = np.empty((horizon, 2), dtype=float)
    for axis in range(2):
        slope, intercept = np.polyfit(t, history_xy[:, axis], 1)
        out[:, axis] = intercept + slope * tf
    return out


def constant_acceleration(history_xy: np.ndarray, horizon: int, dt: float | None = None, *, history_times=None, future_times=None) -> np.ndarray:
    """Quadratic least-squares prediction on uniform or measured time."""
    history_xy = np.asarray(history_xy, dtype=float)
    if len(history_xy) < 3:
        return constant_velocity(history_xy, horizon, dt, history_times=history_times, future_times=future_times)
    t, tf = _times(len(history_xy), dt, history_times, future_times, horizon)
    out = np.empty((horizon, 2), dtype=float)
    for axis in range(2):
        coeff = np.polyfit(t, history_xy[:, axis], 2)
        out[:, axis] = np.polyval(coeff, tf)
    return out
