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


def holm_adjust(pvalues):
    """Holm step-down family-wise error correction."""
    p = np.asarray(pvalues, dtype=float)
    if p.ndim != 1:
        raise ValueError("pvalues must be one-dimensional")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("pvalues must lie in [0, 1]")
    m = len(p)
    if m == 0:
        return p.copy()
    order = np.argsort(p)
    ranked = p[order]
    adjusted_ranked = np.maximum.accumulate((m - np.arange(m)) * ranked)
    adjusted_ranked = np.clip(adjusted_ranked, 0.0, 1.0)
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = adjusted_ranked
    return adjusted


def pareto_mask(values, minimize=None):
    """Return mask of non-dominated rows for multi-objective values.

    ``minimize`` is a boolean vector indicating objective direction. When omitted,
    all objectives are minimized.
    """
    x = np.asarray(values, dtype=float)
    if x.ndim != 2:
        raise ValueError("values must have shape (N, D)")
    if minimize is None:
        minimize = np.ones(x.shape[1], dtype=bool)
    minimize = np.asarray(minimize, dtype=bool)
    if minimize.shape != (x.shape[1],):
        raise ValueError("minimize must have length D")
    z = x.copy()
    z[:, ~minimize] *= -1.0
    keep = np.ones(len(z), dtype=bool)
    for i in range(len(z)):
        if not keep[i]:
            continue
        dominates_i = np.all(z <= z[i], axis=1) & np.any(z < z[i], axis=1)
        if np.any(dominates_i):
            keep[i] = False
    return keep
