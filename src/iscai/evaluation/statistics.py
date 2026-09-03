"""Paired statistical utilities for experiment reporting."""

from __future__ import annotations

import numpy as np
from scipy.stats import wilcoxon


def paired_bootstrap_delta(a, b, *, samples=10000, confidence=0.95, rng=0):
    """Bootstrap paired mean difference b-a and return estimate + CI."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("a and b must be paired 1D arrays with identical shape")
    if len(a) == 0:
        raise ValueError("empty paired arrays")
    d = b - a
    gen = np.random.default_rng(rng)
    idx = gen.integers(0, len(d), size=(samples, len(d)))
    boot = d[idx].mean(axis=1)
    alpha = 1.0 - confidence
    return {
        "mean_delta": float(d.mean()),
        "ci_low": float(np.quantile(boot, alpha / 2)),
        "ci_high": float(np.quantile(boot, 1 - alpha / 2)),
    }


def paired_wilcoxon(a, b):
    """Two-sided paired Wilcoxon signed-rank test with robust all-zero handling."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("a and b must be paired 1D arrays with identical shape")
    d = b - a
    if np.allclose(d, 0.0):
        return {"statistic": 0.0, "pvalue": 1.0}
    res = wilcoxon(a, b, alternative="two-sided", zero_method="wilcox")
    return {"statistic": float(res.statistic), "pvalue": float(res.pvalue)}
