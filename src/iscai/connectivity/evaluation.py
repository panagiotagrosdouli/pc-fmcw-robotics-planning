"""Connectivity metrics for planner experiments."""

from __future__ import annotations

import numpy as np


def outage_rate(snr_db, threshold_db=8.0) -> float:
    snr = np.asarray(snr_db, dtype=float)
    return float(np.mean(snr < threshold_db)) if snr.size else float("nan")


def mean_snr(snr_db) -> float:
    snr = np.asarray(snr_db, dtype=float)
    return float(np.mean(snr)) if snr.size else float("nan")


def worst_percentile_snr(snr_db, q=5.0) -> float:
    snr = np.asarray(snr_db, dtype=float)
    return float(np.percentile(snr, q)) if snr.size else float("nan")
