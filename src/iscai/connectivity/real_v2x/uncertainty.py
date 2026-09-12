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
    def interval(self, mean, support_distance=None):
        if self.radius_ is None: raise RuntimeError("calibrator not fitted")
        m = np.asarray(mean, float); return m - self.radius_, m + self.radius_
    def violation_probability_proxy(self, mean, threshold, direction="above"):
        """Conservative interval-based risk flag, not a calibrated probability."""
        lo, hi = self.interval(mean)
        if direction == "above": return (hi > threshold).astype(float)
        return (lo < threshold).astype(float)


class SupportConditionalConformalCalibrator:
    """Mondrian-style split conformal intervals stratified by spatial support distance.

    Bins are fixed before looking at test residuals. Sparse calibration bins fall back
    to the global split-conformal radius. The interval is a coverage device, not a
    calibrated probability distribution.
    """
    def __init__(self, alpha=0.1, bins=(0.0, 1.0, 5.0, 15.0, float("inf")), min_bin_samples=100):
        if not 0 < alpha < 1: raise ValueError("alpha must be in (0,1)")
        self.alpha=float(alpha); self.bins=np.asarray(bins,float); self.min_bin_samples=int(min_bin_samples)
        if len(self.bins)<2 or not np.all(np.diff(self.bins)>0): raise ValueError("bins must increase")
        self.global_radius_=None; self.radii_=None; self.counts_=None

    @staticmethod
    def _radius(residuals, alpha):
        r=np.asarray(residuals,float); n=len(r)
        if n==0: return np.nan
        q=min(1.0, np.ceil((n+1)*(1-alpha))/n)
        return float(np.quantile(r,q,method="higher"))

    def fit(self, y_true, y_pred, support_distance):
        r=np.abs(np.asarray(y_true,float)-np.asarray(y_pred,float)); d=np.asarray(support_distance,float)
        if len(r)!=len(d) or len(r)==0: raise ValueError("aligned non-empty calibration arrays required")
        self.global_radius_=self._radius(r,self.alpha); self.radii_=[]; self.counts_=[]
        idx=np.digitize(d,self.bins[1:-1],right=True)
        for b in range(len(self.bins)-1):
            rb=r[idx==b]; self.counts_.append(int(len(rb)))
            self.radii_.append(self._radius(rb,self.alpha) if len(rb)>=self.min_bin_samples else self.global_radius_)
        self.radii_=np.asarray(self.radii_,float); return self

    def radii(self, support_distance):
        if self.radii_ is None: raise RuntimeError("calibrator not fitted")
        d=np.asarray(support_distance,float); idx=np.digitize(d,self.bins[1:-1],right=True)
        return self.radii_[idx]

    def interval(self, mean, support_distance=None):
        if support_distance is None:
            if self.global_radius_ is None: raise RuntimeError("calibrator not fitted")
            r=self.global_radius_
        else:
            r=self.radii(support_distance)
        m=np.asarray(mean,float); return m-r,m+r
