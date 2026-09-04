"""Risk primitives for connectivity-aware planning experiments."""

from __future__ import annotations

import numpy as np


def cvar(cost_samples, alpha: float = 0.9) -> float:
    """Return empirical CVaR of high (adverse) costs at confidence level alpha."""
    values = np.asarray(cost_samples, dtype=float)
    if values.size == 0:
        raise ValueError("cost_samples must be non-empty")
    if not 0.0 <= alpha < 1.0:
        raise ValueError("alpha must satisfy 0 <= alpha < 1")
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("cost_samples must contain a finite value")
    q = np.quantile(values, alpha)
    tail = values[values >= q]
    return float(np.mean(tail))


def chance_violation_probability(snr_samples_db, threshold_db: float) -> float:
    """Estimate P(SNR < threshold) from predictive samples."""
    values = np.asarray(snr_samples_db, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("snr_samples_db must contain a finite value")
    return float(np.mean(values < float(threshold_db)))


def adaptive_connectivity_weight(
    outage_probability: float,
    base_weight: float,
    max_weight: float,
    activation_threshold: float,
) -> float:
    """Smoothly increase connectivity weight as predicted outage risk rises."""
    p = float(np.clip(outage_probability, 0.0, 1.0))
    base = float(base_weight)
    maximum = float(max_weight)
    threshold = float(activation_threshold)
    if base < 0.0 or maximum < base:
        raise ValueError("weights must satisfy 0 <= base_weight <= max_weight")
    if not 0.0 <= threshold < 1.0:
        raise ValueError("activation_threshold must satisfy 0 <= threshold < 1")
    if p <= threshold:
        return base
    fraction = (p - threshold) / (1.0 - threshold)
    return float(base + fraction * (maximum - base))
