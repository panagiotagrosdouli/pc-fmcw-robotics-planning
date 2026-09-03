"""Uncertainty-aware connectivity risk cost.

The Monte-Carlo path can use the same ``LinkPredictor`` instance as P1/P2 so
planner comparisons do not silently change the channel model.
"""

from __future__ import annotations

from types import SimpleNamespace
import numpy as np


def snr_samples_from_prediction(mean_xy, sigma_xy, ego_states, *, samples=128,
                                rng=None, link_predictor=None):
    """Sample future target positions and return SNR samples per horizon step.

    ``ego_states`` may be (H,2) positions or full planner states (H,>=3). If a
    ``link_predictor`` is supplied, each Monte-Carlo sample is evaluated by its
    normal ``predict`` interface. Otherwise the legacy geometry baseline is used.
    """
    rng = np.random.default_rng(rng)
    mean_xy = np.asarray(mean_xy, dtype=float)
    sigma_xy = np.asarray(sigma_xy, dtype=float)
    ego_states = np.asarray(ego_states, dtype=float)
    if mean_xy.shape != sigma_xy.shape or mean_xy.ndim != 2 or mean_xy.shape[1] != 2:
        raise ValueError("mean_xy and sigma_xy must have shape (H,2)")
    if len(ego_states) != len(mean_xy):
        raise ValueError("ego_states and target prediction must share the horizon")

    noise = rng.normal(size=(samples, *mean_xy.shape)) * sigma_xy[None, ...]
    target = mean_xy[None, ...] + noise

    if link_predictor is None:
        from iscai.connectivity.trajectory_link import predict_snr_db
        ego_xy = np.broadcast_to(ego_states[:, :2], target.shape)
        return predict_snr_db(ego_xy, target)

    out = np.empty((samples, len(mean_xy)), dtype=float)
    trajectory = SimpleNamespace(states=ego_states)
    for i in range(samples):
        out[i] = np.asarray(link_predictor.predict(trajectory, target[i]).snr_db, dtype=float)
    return out


def outage_risk(snr_samples, threshold_db=8.0):
    snr = np.asarray(snr_samples, dtype=float)
    return np.mean(snr < threshold_db, axis=0)


def risk_cost(snr_samples, threshold_db=8.0, risk_power=2.0):
    risk = outage_risk(snr_samples, threshold_db)
    return float(np.mean(risk ** risk_power))
