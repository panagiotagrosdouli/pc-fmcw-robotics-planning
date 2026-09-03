"""Trajectory-conditioned connectivity surrogate.

This module is intentionally separated from the robotics planner. The current
implementation is a transparent geometry baseline; it must not be reported as
measured PC-FMCW optical-link data. It provides a stable interface for replacing
this baseline with a frozen real-data predictor later.
"""

from __future__ import annotations

import numpy as np


def relative_geometry(ego_xy: np.ndarray, target_xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ego_xy = np.asarray(ego_xy, dtype=float)
    target_xy = np.asarray(target_xy, dtype=float)
    delta = target_xy - ego_xy
    distance = np.linalg.norm(delta, axis=-1)
    bearing = np.arctan2(delta[..., 1], delta[..., 0])
    return distance, bearing


def predict_snr_db(ego_xy: np.ndarray, target_xy: np.ndarray, *, beam_sigma_rad=0.20,
                   reference_snr_db=30.0, pathloss_exponent=2.0) -> np.ndarray:
    """Return a deterministic geometry-conditioned SNR baseline."""
    d, bearing = relative_geometry(ego_xy, target_xy)
    d = np.maximum(d, 1.0)
    angular_penalty = (bearing / beam_sigma_rad) ** 2
    return reference_snr_db - 10.0 * pathloss_exponent * np.log10(d) - 4.343 * angular_penalty


def outage_probability(snr_db: np.ndarray, threshold_db=8.0, softness_db=2.0) -> np.ndarray:
    x = (threshold_db - np.asarray(snr_db)) / max(softness_db, 1e-9)
    return 1.0 / (1.0 + np.exp(-x))
