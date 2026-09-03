"""Calibration metrics for probabilistic trajectory prediction."""

from __future__ import annotations

import numpy as np


def gaussian_coverage(pred_mean, pred_sigma, truth, k=1.0):
    """Fraction of future x/y coordinates inside +/- k sigma."""
    mean = np.asarray(pred_mean, dtype=float)
    sigma = np.asarray(pred_sigma, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if mean.shape != sigma.shape or mean.shape != truth.shape:
        raise ValueError("mean, sigma and truth must have identical shape")
    sigma = np.maximum(sigma, 1e-9)
    return float(np.mean(np.abs(truth - mean) <= k * sigma))


def gaussian_nll_numpy(pred_mean, pred_sigma, truth):
    """Average diagonal-Gaussian negative log likelihood, including constants."""
    mean = np.asarray(pred_mean, dtype=float)
    sigma = np.maximum(np.asarray(pred_sigma, dtype=float), 1e-9)
    truth = np.asarray(truth, dtype=float)
    if mean.shape != sigma.shape or mean.shape != truth.shape:
        raise ValueError("mean, sigma and truth must have identical shape")
    z2 = ((truth - mean) / sigma) ** 2
    return float(np.mean(0.5 * z2 + np.log(sigma) + 0.5 * np.log(2.0 * np.pi)))


def sharpness(pred_sigma):
    """Mean predictive standard deviation in metres."""
    sigma = np.asarray(pred_sigma, dtype=float)
    return float(np.mean(sigma))
