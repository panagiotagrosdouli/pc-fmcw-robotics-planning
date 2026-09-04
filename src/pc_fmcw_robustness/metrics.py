"""Publication metrics for reliability-mobility and compute-performance analysis."""

from __future__ import annotations

import math


def relative_improvement(baseline: float, candidate: float, *, lower_is_better: bool = True) -> float:
    """Return signed relative improvement, positive when candidate is better."""
    b = float(baseline)
    c = float(candidate)
    if not math.isfinite(b) or not math.isfinite(c):
        raise ValueError("metric values must be finite")
    if b == 0.0:
        raise ValueError("baseline must be non-zero")
    return (b - c) / abs(b) if lower_is_better else (c - b) / abs(b)


def compute_efficiency(performance_gain: float, runtime_s: float) -> float:
    """Normalize a performance gain by planning runtime."""
    runtime = float(runtime_s)
    if not math.isfinite(runtime) or runtime <= 0.0:
        raise ValueError("runtime_s must be finite and positive")
    return float(performance_gain) / runtime
