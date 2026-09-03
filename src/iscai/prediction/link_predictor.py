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
    """Configurable geometry surrogate with directional beam sensitivity.

    This is a research prototype surrogate, not a replacement for the PC-FMCW PHY.
    """

    def __init__(
        self,
        reference_snr_db=20.0,
        reference_distance=10.0,
        min_snr_db=8.0,
        data_rate=1e9,
        beam_sigma_rad=0.12,
    ):
        self.reference_snr_db = reference_snr_db
        self.reference_distance = reference_distance
        self.min_snr_db = min_snr_db
        self.data_rate = data_rate
        self.beam_sigma_rad = beam_sigma_rad

    def predict(self, ego_trajectory, target_prediction, link_history=None):
        ego = np.asarray(ego_trajectory.states if hasattr(ego_trajectory, "states") else ego_trajectory)
        target = np.asarray(target_prediction)
        n = min(len(ego), len(target))
        ego = ego[:n]
        target = target[:n]

        delta = target[:, :2] - ego[:, :2]
        distance = np.maximum(np.linalg.norm(delta, axis=1), 0.1)
        bearing = np.arctan2(delta[:, 1], delta[:, 0])
        ego_yaw = ego[:, 2]
        angle_error = np.arctan2(np.sin(bearing - ego_yaw), np.cos(bearing - ego_yaw))

        distance_snr = self.reference_snr_db - 20.0 * np.log10(distance / self.reference_distance)
        angular_gain = np.exp(-0.5 * (angle_error / self.beam_sigma_rad) ** 2)
        snr = distance_snr + 10.0 * np.log10(np.maximum(angular_gain, 1e-6))

        ber = 0.5 * np.exp(-np.maximum(snr, 0.0) / 3.0)
        outage = (snr < self.min_snr_db).astype(float)
        goodput = self.data_rate * (1.0 - np.clip(ber, 0.0, 1.0))
        survival = float(np.prod(1.0 - outage))
        return LinkForecast(snr, ber, outage, goodput, survival)
