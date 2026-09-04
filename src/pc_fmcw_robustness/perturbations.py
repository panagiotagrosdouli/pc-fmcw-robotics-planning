"""Predictive-information perturbations for distribution-shift experiments."""

from __future__ import annotations

import numpy as np


def perturb_prediction(
    values,
    *,
    bias: float = 0.0,
    noise_scale: float = 1.0,
    rng: np.random.Generator | None = None,
):
    """Apply additive bias and scalable zero-mean noise to predictive values.

    The function is deliberately generic so experiments can perturb SNR,
    path-loss, or another scalar prediction channel without changing ground
    truth. noise_scale=1 leaves the stochastic scale unchanged when no
    external residual samples are provided; values are returned with bias.
    """
    array = np.asarray(values, dtype=float)
    if not np.isfinite(bias):
        raise ValueError("bias must be finite")
    if not np.isfinite(noise_scale) or noise_scale < 0.0:
        raise ValueError("noise_scale must be finite and non-negative")
    if noise_scale == 1.0:
        return array + float(bias)
    generator = rng if rng is not None else np.random.default_rng()
    scale = np.nanstd(array)
    if not np.isfinite(scale) or scale == 0.0:
        scale = 1.0
    extra = generator.normal(0.0, abs(noise_scale - 1.0) * scale, size=array.shape)
    return array + float(bias) + extra


def delayed_history(values, delay_steps: int):
    """Return a causal history delayed by an integer number of samples."""
    array = np.asarray(values)
    delay = int(delay_steps)
    if delay < 0:
        raise ValueError("delay_steps must be non-negative")
    if delay == 0:
        return array.copy()
    if array.shape[0] <= delay:
        return array[:0].copy()
    return array[:-delay].copy()
