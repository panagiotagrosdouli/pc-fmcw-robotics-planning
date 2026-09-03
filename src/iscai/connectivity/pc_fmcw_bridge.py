"""PC-FMCW-to-robotics connectivity bridge.

The reference constants in :class:`PCFMCWReferenceParameters` are traced to
Module 0 of ``PanagiotaGr/ISCAI_pc_fmcw/notebooks/ISCAI_PC_FMCW.ipynb``.

This module deliberately separates *traced PC-FMCW waveform parameters* from
the *robotics link-budget assumptions*. The upstream notebook specifies the
carrier, chirp bandwidth/duration and 1-Gbit/s DPSK data rate, but it does not
provide a complete vehicle-to-vehicle optical link budget as a function of
range and pointing angle. Therefore the geometry-to-SNR law below remains a
simulation model and must not be reported as measured optical data.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from iscai.prediction.link_predictor import LinkForecast


@dataclass(frozen=True)
class PCFMCWReferenceParameters:
    """Waveform parameters traced to the upstream PC-FMCW notebook."""

    carrier_frequency_hz: float = 193.4e12
    chirp_bandwidth_hz: float = 10e9
    chirp_duration_s: float = 10e-6
    data_rate_bps: float = 1e9
    speed_of_light_mps: float = 299_792_458.0

    @property
    def chirp_slope_hz_per_s(self) -> float:
        return self.chirp_bandwidth_hz / self.chirp_duration_s

    @property
    def wavelength_m(self) -> float:
        return self.speed_of_light_mps / self.carrier_frequency_hz

    @property
    def symbol_duration_s(self) -> float:
        return 1.0 / self.data_rate_bps

    @property
    def range_resolution_m(self) -> float:
        """Ideal FMCW range resolution c/(2B)."""
        return self.speed_of_light_mps / (2.0 * self.chirp_bandwidth_hz)


@dataclass(frozen=True)
class OpticalGeometryAssumptions:
    """Explicit simulation assumptions not claimed as upstream measurements."""

    reference_snr_db: float = 20.0
    reference_distance_m: float = 10.0
    pathloss_exponent: float = 2.0
    beam_sigma_rad: float = 0.12
    outage_threshold_db: float = 8.0
    outage_softness_db: float = 2.0


class PCFMCWPlanningLinkPredictor:
    """Planner-compatible PC-FMCW-informed simulation link predictor.

    PC-FMCW provenance is limited to the waveform/data-rate constants. The
    range/angle link-budget terms are declared simulation assumptions until a
    validated optical propagation model or measurement calibration is supplied.
    """

    def __init__(
        self,
        reference: PCFMCWReferenceParameters | None = None,
        geometry: OpticalGeometryAssumptions | None = None,
    ) -> None:
        self.reference = reference or PCFMCWReferenceParameters()
        self.geometry = geometry or OpticalGeometryAssumptions()

    def predict(self, ego_trajectory, target_prediction, link_history=None) -> LinkForecast:
        del link_history
        ego = np.asarray(
            ego_trajectory.states if hasattr(ego_trajectory, "states") else ego_trajectory,
            dtype=float,
        )
        target = np.asarray(target_prediction, dtype=float)
        n = min(len(ego), len(target))
        if n == 0:
            empty = np.empty(0, dtype=float)
            return LinkForecast(empty, empty, empty, empty, 1.0)

        ego = ego[:n]
        target = target[:n]
        delta = target[:, :2] - ego[:, :2]
        distance = np.maximum(np.linalg.norm(delta, axis=1), 0.1)
        bearing = np.arctan2(delta[:, 1], delta[:, 0])
        angle_error = np.arctan2(
            np.sin(bearing - ego[:, 2]),
            np.cos(bearing - ego[:, 2]),
        )

        g = self.geometry
        distance_loss_db = 10.0 * g.pathloss_exponent * np.log10(
            distance / g.reference_distance_m
        )
        angular_gain = np.exp(-0.5 * (angle_error / g.beam_sigma_rad) ** 2)
        angular_loss_db = -10.0 * np.log10(np.maximum(angular_gain, 1e-12))
        snr_db = g.reference_snr_db - distance_loss_db - angular_loss_db

        # Smooth outage is useful for risk-sensitive planning. It is a modeling
        # choice, not an upstream measured outage curve.
        z = np.clip(
            (g.outage_threshold_db - snr_db) / max(g.outage_softness_db, 1e-12),
            -60.0,
            60.0,
        )
        outage = 1.0 / (1.0 + np.exp(-z))

        # DPSK-compatible analytical AWGN approximation used only as a modeled
        # communication metric; it is not a measured BER curve.
        snr_linear = 10.0 ** (snr_db / 10.0)
        ber = 0.5 * np.exp(-np.maximum(snr_linear, 0.0))
        goodput = self.reference.data_rate_bps * (1.0 - np.clip(ber, 0.0, 1.0))
        survival = float(np.prod(1.0 - np.clip(outage, 0.0, 1.0)))

        return LinkForecast(snr_db, ber, outage, goodput, survival)

    def provenance(self) -> dict:
        """Machine-readable claim boundary for experiment manifests."""
        return {
            "waveform_source": "PanagiotaGr/ISCAI_pc_fmcw Module 0",
            "waveform_parameters_traced": True,
            "optical_geometry_model": "simulation_assumption",
            "measured_optical_link": False,
            "real_world_validation": False,
        }
