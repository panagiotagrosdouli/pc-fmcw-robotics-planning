"""Uncertainty-aware connectivity risk cost."""

from __future__ import annotations

import numpy as np


def snr_samples_from_prediction(mean_xy, sigma_xy, ego_xy, *, samples=128, rng=None):
    """Sample future target positions and return SNR samples per horizon step."""
    from iscai.connectivity.trajectory_link import predict_snr_db
    rng = np.random.default_rng(rng)
    mean_xy = np.asarray(mean_xy, dtype=float)
    sigma_xy = np.asarray(sigma_xy, dtype=float)
    ego_xy = np.asarray(ego_xy, dtype=float)
    if mean_xy.shape != sigma_xy.shape or mean_xy.ndim != 2:
        raise ValueError("mean_xy and sigma_xy must have shape (H,2)")
    noise = rng.normal(size=(samples, *mean_xy.shape)) * sigma_xy[None, ...]
    target = mean_xy[None, ...] + noise
    ego = np.broadcast_to(ego_xy, target.shape)
    return predict_snr_db(ego, target)


def outage_risk(snr_samples, threshold_db=8.0):
    snr = np.asarray(snr_samples, dtype=float)
    return np.mean(snr < threshold_db, axis=0)


def risk_cost(snr_samples, threshold_db=8.0, risk_power=2.0):
    risk = outage_risk(snr_samples, threshold_db)
    return float(np.mean(risk ** risk_power))
