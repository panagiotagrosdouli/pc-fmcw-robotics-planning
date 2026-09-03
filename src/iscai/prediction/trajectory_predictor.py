"""Lightweight trajectory prediction baselines for real CMHT tracklets."""

from __future__ import annotations

import numpy as np


def constant_velocity(history_xy: np.ndarray, horizon: int, dt: float) -> np.ndarray:
    """Predict future x,y positions using a least-squares constant-velocity fit."""
    history_xy = np.asarray(history_xy, dtype=float)
    if history_xy.ndim != 2 or history_xy.shape[1] != 2 or len(history_xy) < 2:
        raise ValueError("history_xy must have shape (N, 2) with N >= 2")
    n = len(history_xy)
    t = np.arange(n, dtype=float) * dt
    tf = np.arange(1, horizon + 1, dtype=float) * dt + t[-1]
    out = np.empty((horizon, 2), dtype=float)
    for axis in range(2):
        slope, intercept = np.polyfit(t, history_xy[:, axis], 1)
        out[:, axis] = intercept + slope * tf
    return out


def constant_acceleration(history_xy: np.ndarray, horizon: int, dt: float) -> np.ndarray:
    """Predict using a quadratic least-squares fit when enough history exists."""
    history_xy = np.asarray(history_xy, dtype=float)
    if len(history_xy) < 3:
        return constant_velocity(history_xy, horizon, dt)
    n = len(history_xy)
    t = np.arange(n, dtype=float) * dt
    tf = np.arange(1, horizon + 1, dtype=float) * dt + t[-1]
    out = np.empty((horizon, 2), dtype=float)
    for axis in range(2):
        coeff = np.polyfit(t, history_xy[:, axis], 2)
        out[:, axis] = np.polyval(coeff, tf)
    return out
