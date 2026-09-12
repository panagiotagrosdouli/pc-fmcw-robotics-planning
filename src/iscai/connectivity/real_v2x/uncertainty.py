from __future__ import annotations
import numpy as np

class ResidualConformalCalibrator:
    """Split-conformal symmetric residual interval for regression."""
    def __init__(self, alpha=0.1):
        if not 0 < alpha < 1: raise ValueError("alpha must be in (0,1)")
        self.alpha = float(alpha); self.radius_ = None
    def fit(self, y_true, y_pred):
        r = np.abs(np.asarray(y_true, float) - np.asarray(y_pred, float))
        n = len(r)
        if n == 0: raise ValueError("empty calibration set")
        q = min(1.0, np.ceil((n + 1) * (1 - self.alpha)) / n)
        self.radius_ = float(np.quantile(r, q, method="higher")); return self
    def interval(self, mean):
        if self.radius_ is None: raise RuntimeError("calibrator not fitted")
        m = np.asarray(mean, float); return m - self.radius_, m + self.radius_
    def violation_probability_proxy(self, mean, threshold, direction="above"):
        """Conservative interval-based risk flag, not a calibrated probability."""
        lo, hi = self.interval(mean)
        if direction == "above": return (hi > threshold).astype(float)
        return (lo < threshold).astype(float)
