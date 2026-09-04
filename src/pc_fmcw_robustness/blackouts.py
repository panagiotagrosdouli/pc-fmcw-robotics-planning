"""Controlled communication-blackout profiles for stress testing."""

from __future__ import annotations

import numpy as np


def blackout_mask(kind: str, n_steps: int, *, period: int = 10) -> np.ndarray:
    """Return a boolean mask indicating degraded-link timesteps."""
    n = int(n_steps)
    if n < 0:
        raise ValueError("n_steps must be non-negative")
    mask = np.zeros(n, dtype=bool)
    if kind == "sudden_blockage":
        mask[n // 2 :] = True
    elif kind == "persistent_nlos":
        mask[:] = True
    elif kind == "intermittent_link":
        p = max(int(period), 2)
        mask[np.arange(n) % p >= p // 2] = True
    elif kind == "rapid_degradation":
        if n:
            threshold = max(n // 3, 1)
            mask[threshold:] = True
    else:
        raise ValueError(f"unknown blackout kind: {kind}")
    return mask


def apply_snr_blackout(snr_db, kind: str, *, attenuation_db: float = 20.0, period: int = 10):
    """Apply deterministic attenuation to selected timesteps."""
    values = np.asarray(snr_db, dtype=float).copy()
    mask = blackout_mask(kind, len(values), period=period)
    values[mask] -= float(attenuation_db)
    return values
