"""Communication-model stressors for closed-loop robustness experiments.

The wrappers in this module keep ground-truth and planning models explicitly
separate. A planning predictor can be biased or mismatched while realized link
metrics are still evaluated by an unmodified reference predictor. Time-indexed
blackout profiles can also be applied deterministically and reproducibly.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import numpy as np

from iscai.connectivity.pc_fmcw_bridge import (
    OpticalGeometryAssumptions,
    PCFMCWPlanningLinkPredictor,
)
from iscai.prediction.link_predictor import LinkForecast


@dataclass(frozen=True)
class LinkStressProfile:
    kind: str = "none"
    attenuation_db: float = 20.0
    start_fraction: float = 0.5
    period_steps: int = 10
    duty_cycle: float = 0.5
    degradation_span_steps: int = 10

    def __post_init__(self):
        if self.kind not in {"none", "sudden_blockage", "persistent_nlos", "intermittent_link", "rapid_degradation"}:
            raise ValueError(f"unknown link stress kind: {self.kind}")
        if not np.isfinite(self.attenuation_db) or self.attenuation_db < 0.0:
            raise ValueError("attenuation_db must be finite and non-negative")
        if not 0.0 <= self.start_fraction <= 1.0:
            raise ValueError("start_fraction must be in [0,1]")
        if self.period_steps < 1:
            raise ValueError("period_steps must be >= 1")
        if not 0.0 <= self.duty_cycle <= 1.0:
            raise ValueError("duty_cycle must be in [0,1]")
        if self.degradation_span_steps < 1:
            raise ValueError("degradation_span_steps must be >= 1")

    def attenuation(self, absolute_steps, episode_steps=None):
        steps = np.asarray(absolute_steps, dtype=int)
        out = np.zeros(steps.shape, dtype=float)
        if self.kind == "none" or steps.size == 0:
            return out
        total = int(episode_steps) if episode_steps is not None else int(np.max(steps) + 1)
        total = max(total, 1)
        start = int(round(self.start_fraction * max(total - 1, 0)))
        if self.kind == "persistent_nlos":
            out[:] = self.attenuation_db
        elif self.kind == "sudden_blockage":
            out[steps >= start] = self.attenuation_db
        elif self.kind == "intermittent_link":
            phase = np.mod(steps, self.period_steps)
            active = phase < max(1, int(round(self.period_steps * self.duty_cycle)))
            out[active] = self.attenuation_db
        elif self.kind == "rapid_degradation":
            progress = np.clip((steps - start + 1) / float(self.degradation_span_steps), 0.0, 1.0)
            out = self.attenuation_db * progress
        return out


def _forecast_from_snr(snr_db, base_predictor):
    snr = np.asarray(snr_db, dtype=float)
    geometry = getattr(base_predictor, "geometry", OpticalGeometryAssumptions())
    reference = getattr(base_predictor, "reference", None)
    threshold = float(getattr(geometry, "outage_threshold_db", 8.0))
    softness = max(float(getattr(geometry, "outage_softness_db", 2.0)), 1e-12)
    z = np.clip((threshold - snr) / softness, -60.0, 60.0)
    outage = 1.0 / (1.0 + np.exp(-z))
    snr_linear = 10.0 ** (snr / 10.0)
    ber = 0.5 * np.exp(-np.maximum(snr_linear, 0.0))
    data_rate = float(getattr(reference, "data_rate_bps", 1e9))
    goodput = data_rate * (1.0 - np.clip(ber, 0.0, 1.0))
    survival = float(np.prod(1.0 - np.clip(outage, 0.0, 1.0)))
    return LinkForecast(snr, ber, outage, goodput, survival)


class TimeIndexedStressedLinkPredictor:
    """Apply a deterministic future-aware attenuation profile to a base link model."""

    def __init__(self, base_predictor, profile: LinkStressProfile, episode_steps=None):
        self.base_predictor = base_predictor
        self.profile = profile
        self.episode_steps = None if episode_steps is None else int(episode_steps)
        self.current_step = 0

    def set_step(self, step):
        self.current_step = int(step)

    def predict(self, ego_trajectory, target_prediction, link_history=None):
        forecast = self.base_predictor.predict(ego_trajectory, target_prediction, link_history)
        n = len(forecast.snr_db)
        absolute = self.current_step + np.arange(n, dtype=int)
        attenuation = self.profile.attenuation(absolute, self.episode_steps)
        return _forecast_from_snr(np.asarray(forecast.snr_db, dtype=float) - attenuation, self.base_predictor)

    def provenance(self):
        base = self.base_predictor.provenance() if hasattr(self.base_predictor, "provenance") else {}
        return {
            **base,
            "stress_profile": self.profile.kind,
            "stress_attenuation_db": self.profile.attenuation_db,
            "stress_information": "future_profile_visible",
        }


class ReactiveTimeIndexedStressedLinkPredictor(TimeIndexedStressedLinkPredictor):
    """Reactive stress model that exposes only the current attenuation state.

    Every point in the planner's candidate horizon is scored with the attenuation
    observed at ``current_step``. This prevents a reactive baseline from receiving
    privileged knowledge of a future scheduled blockage while preserving the same
    underlying link model and realized stress profile.
    """

    def predict(self, ego_trajectory, target_prediction, link_history=None):
        forecast = self.base_predictor.predict(ego_trajectory, target_prediction, link_history)
        n = len(forecast.snr_db)
        current = self.profile.attenuation(np.asarray([self.current_step]), self.episode_steps)
        attenuation = float(current[0]) if current.size else 0.0
        return _forecast_from_snr(np.asarray(forecast.snr_db, dtype=float) - attenuation, self.base_predictor)

    def provenance(self):
        base = self.base_predictor.provenance() if hasattr(self.base_predictor, "provenance") else {}
        return {
            **base,
            "stress_profile": self.profile.kind,
            "stress_attenuation_db": self.profile.attenuation_db,
            "stress_information": "current_state_only",
        }


def make_mismatched_pc_fmcw_predictor(
    base_predictor=None,
    *,
    reference_snr_bias_db=0.0,
    pathloss_scale=1.0,
    beam_sigma_scale=1.0,
    outage_threshold_bias_db=0.0,
):
    """Create a planner-only PC-FMCW model mismatch from a reference predictor."""
    base = base_predictor or PCFMCWPlanningLinkPredictor()
    if not isinstance(base, PCFMCWPlanningLinkPredictor):
        raise TypeError("model mismatch currently requires PCFMCWPlanningLinkPredictor")
    if pathloss_scale <= 0.0 or beam_sigma_scale <= 0.0:
        raise ValueError("pathloss_scale and beam_sigma_scale must be positive")
    g = base.geometry
    geometry = replace(
        g,
        reference_snr_db=float(g.reference_snr_db) + float(reference_snr_bias_db),
        pathloss_exponent=float(g.pathloss_exponent) * float(pathloss_scale),
        beam_sigma_rad=float(g.beam_sigma_rad) * float(beam_sigma_scale),
        outage_threshold_db=float(g.outage_threshold_db) + float(outage_threshold_bias_db),
    )
    return PCFMCWPlanningLinkPredictor(reference=base.reference, geometry=geometry)
