"""Uncertainty-aware connectivity risk costs.

The Monte-Carlo path can use the same ``LinkPredictor`` instance as P1/P2 so
planner comparisons do not silently change the channel model.  The historical
``risk_cost`` function is retained for the frozen P3 baseline.  Additional
primitives below implement CVaR, chance constraints, and adaptive weighting for
the separately versioned research framework.
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
    if int(samples) < 1:
        raise ValueError("samples must be >= 1")

    noise = rng.normal(size=(int(samples), *mean_xy.shape)) * sigma_xy[None, ...]
    target = mean_xy[None, ...] + noise

    if link_predictor is None:
        from iscai.connectivity.trajectory_link import predict_snr_db
        ego_xy = np.broadcast_to(ego_states[:, :2], target.shape)
        return predict_snr_db(ego_xy, target)

    out = np.empty((int(samples), len(mean_xy)), dtype=float)
    trajectory = SimpleNamespace(states=ego_states)
    for i in range(int(samples)):
        out[i] = np.asarray(link_predictor.predict(trajectory, target[i]).snr_db, dtype=float)
    return out


def outage_risk(snr_samples, threshold_db=8.0):
    """Per-horizon-step empirical outage probability."""
    snr = np.asarray(snr_samples, dtype=float)
    if snr.ndim != 2 or snr.shape[0] < 1:
        raise ValueError("snr_samples must have shape (samples, horizon)")
    return np.mean(snr < float(threshold_db), axis=0)


def risk_cost(snr_samples, threshold_db=8.0, risk_power=2.0):
    """Historical P3 outage-risk objective retained unchanged in semantics."""
    risk = outage_risk(snr_samples, threshold_db)
    return float(np.mean(risk ** float(risk_power)))


def empirical_cvar(values, alpha=0.9):
    """Empirical upper-tail CVaR for adverse cost samples.

    ``alpha`` is the retained quantile threshold.  For example, alpha=0.9
    averages the worst 10 percent of sampled costs (including ties at VaR).
    """
    x = np.asarray(values, dtype=float).reshape(-1)
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("values must contain at least one finite sample")
    alpha = float(alpha)
    if not 0.0 <= alpha < 1.0:
        raise ValueError("alpha must satisfy 0 <= alpha < 1")
    var = float(np.quantile(x, alpha))
    tail = x[x >= var]
    return float(np.mean(tail))


def sample_outage_costs(snr_samples, threshold_db=8.0):
    """Return one horizon-averaged outage cost per Monte-Carlo draw."""
    snr = np.asarray(snr_samples, dtype=float)
    if snr.ndim != 2 or snr.shape[0] < 1:
        raise ValueError("snr_samples must have shape (samples, horizon)")
    return np.mean(snr < float(threshold_db), axis=1).astype(float)


def cvar_connectivity_cost(snr_samples, threshold_db=8.0, alpha=0.9,
                           expected_weight=1.0, cvar_weight=1.0):
    """Expected outage loss plus upper-tail CVaR of sampled outage loss."""
    losses = sample_outage_costs(snr_samples, threshold_db)
    return float(
        float(expected_weight) * np.mean(losses)
        + float(cvar_weight) * empirical_cvar(losses, alpha)
    )


def chance_violation_probability(snr_samples, threshold_db=8.0):
    """Worst-horizon empirical probability of violating the SNR threshold."""
    step_risk = outage_risk(snr_samples, threshold_db)
    return float(np.max(step_risk)) if step_risk.size else 0.0


def adaptive_connectivity_weight(outage_probability, base_weight=1.0,
                                 max_weight=4.0, activation_threshold=0.1):
    """Smoothly increase connectivity importance as predicted outage rises."""
    p = float(np.clip(outage_probability, 0.0, 1.0))
    base = float(base_weight)
    maximum = float(max_weight)
    threshold = float(activation_threshold)
    if not np.isfinite(base) or not np.isfinite(maximum) or base < 0.0 or maximum < base:
        raise ValueError("weights must satisfy finite 0 <= base_weight <= max_weight")
    if not 0.0 <= threshold < 1.0:
        raise ValueError("activation_threshold must satisfy 0 <= threshold < 1")
    if p <= threshold:
        return base
    fraction = (p - threshold) / (1.0 - threshold)
    return float(base + fraction * (maximum - base))
