"""Trajectory-conditioned future link prediction interface."""

from dataclasses import dataclass
import numpy as np


@dataclass
class LinkForecast:
    snr_db: np.ndarray
    ber: np.ndarray
    outage_probability: np.ndarray
    goodput: np.ndarray
    survival_probability: float


class LinkPredictor:
    """Minimal configurable geometry surrogate; replace/freeze with the PC-FMCW predictor."""

    def __init__(self, reference_snr_db=20.0, reference_distance=10.0, min_snr_db=8.0, data_rate=1e9):
        self.reference_snr_db = reference_snr_db
        self.reference_distance = reference_distance
        self.min_snr_db = min_snr_db
        self.data_rate = data_rate

    def predict(self, ego_trajectory, target_prediction, link_history=None):
        ego = np.asarray(ego_trajectory.states if hasattr(ego_trajectory, "states") else ego_trajectory)
        target = np.asarray(target_prediction)
        n = min(len(ego), len(target))
        distance = np.linalg.norm(ego[:n, :2] - target[:n, :2], axis=1)
        distance = np.maximum(distance, 0.1)
        snr = self.reference_snr_db - 20.0 * np.log10(distance / self.reference_distance)
        ber = 0.5 * np.exp(-np.maximum(snr, 0.0) / 3.0)
        outage = (snr < self.min_snr_db).astype(float)
        goodput = self.data_rate * (1.0 - np.clip(ber, 0.0, 1.0))
        survival = float(np.prod(1.0 - outage))
        return LinkForecast(snr, ber, outage, goodput, survival)
