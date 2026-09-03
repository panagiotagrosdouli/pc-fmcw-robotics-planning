"""Frozen, provenance-aware link predictor for measured/calibrated link data.

This module deliberately avoids calling a model 'PC-FMCW' unless its metadata
explicitly establishes that provenance. It provides the same planner-facing
forecast fields used by the default link predictor so P1/P2/P3/P4 can share it.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np


@dataclass
class LinkForecast:
    snr_db: np.ndarray
    ber: np.ndarray
    outage_probability: np.ndarray
    goodput: np.ndarray
    survival_probability: float


class CalibratedGeometryLinkPredictor:
    REQUIRED_METADATA = ("source", "measurement_type", "calibration_date")

    def __init__(self, metadata, *, reference_snr_db, pathloss_exponent,
                 beam_sigma_rad, outage_threshold_db=8.0, ber_slope=1.0,
                 data_rate=1e9):
        missing = [k for k in self.REQUIRED_METADATA if not metadata.get(k)]
        if missing:
            raise ValueError(f"Missing calibration provenance fields: {missing}")
        self.metadata = dict(metadata)
        self.reference_snr_db = float(reference_snr_db)
        self.pathloss_exponent = float(pathloss_exponent)
        self.beam_sigma_rad = float(beam_sigma_rad)
        self.outage_threshold_db = float(outage_threshold_db)
        self.ber_slope = float(ber_slope)
        self.data_rate = float(data_rate)

    @classmethod
    def from_json(cls, path):
        cfg = json.loads(Path(path).read_text())
        return cls(cfg["metadata"], **cfg["parameters"])

    def predict(self, candidate, target_states, link_history=None):
        ego = np.asarray(candidate.states if hasattr(candidate, "states") else candidate, float)
        target = np.asarray(target_states, float)
        n = min(len(ego), len(target))
        ego = ego[:n]
        target = target[:n]
        delta = target[:, :2] - ego[:, :2]
        d = np.maximum(np.linalg.norm(delta, axis=1), 1.0)
        los = np.arctan2(delta[:, 1], delta[:, 0])
        heading_error = np.arctan2(np.sin(los - ego[:, 2]), np.cos(los - ego[:, 2]))
        snr = (self.reference_snr_db
               - 10.0 * self.pathloss_exponent * np.log10(d)
               - 4.343 * (heading_error / self.beam_sigma_rad) ** 2)
        outage = (snr < self.outage_threshold_db).astype(float)
        ber = 0.5 / (1.0 + np.exp(self.ber_slope * (snr - self.outage_threshold_db)))
        goodput = self.data_rate * (1.0 - np.clip(ber, 0.0, 1.0))
        survival = float(np.prod(1.0 - outage))
        return LinkForecast(snr, ber, outage, goodput, survival)
