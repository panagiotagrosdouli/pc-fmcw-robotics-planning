"""Prospective identifiability scenarios for active self-calibration."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from iscai.simulation.scenario import (
    Scenario,
    following_lateral_offset,
    intersection_turn,
    lane_choice,
    overtake,
)

from .link_model import LatentLinkParameters


@dataclass(frozen=True)
class CalibrationScenario:
    name: str
    scenario: Scenario
    true_parameters: LatentLinkParameters
    prior_axes: dict
    mechanism: str


def _rename(base: Scenario, name: str) -> Scenario:
    return Scenario(
        name=name,
        ego_state=np.asarray(base.ego_state, dtype=float).copy(),
        target_states=np.asarray(base.target_states, dtype=float).copy(),
        obstacles=list(base.obstacles),
        reference_speed=float(base.reference_speed),
    )


def _straight_decision_irrelevant(steps: int, dt: float) -> Scenario:
    t = np.arange(steps, dtype=float) * dt
    target = np.zeros((steps, 4), dtype=float)
    target[:, 0] = 28.0 + 10.0 * t
    target[:, 1] = 0.0
    target[:, 3] = 10.0
    return Scenario(
        name="E_decision_irrelevant_uncertainty",
        ego_state=np.array([0.0, 0.0, 0.0, 10.0]),
        target_states=target,
        obstacles=[],
        reference_speed=10.0,
    )


def make_identifiability_scenarios(steps: int = 31, dt: float = 0.1):
    """Return the six declared mechanism scenarios A--F.

    Latent values are modeled simulator truth, not measured optical parameters.
    Priors are intentionally small grids and may differ by mechanism scenario.
    """
    broad = {
        "alpha_loss_values": (0.85, 1.0, 1.15),
        "delta_beam_values_rad": (-0.04, 0.0, 0.04),
        "k_angular_values": (0.75, 1.0, 1.25),
    }
    narrow = {
        "alpha_loss_values": (0.97, 1.0, 1.03),
        "delta_beam_values_rad": (-0.01, 0.0, 0.01),
        "k_angular_values": (0.95, 1.0, 1.05),
    }
    return [
        CalibrationScenario(
            "A_angular_bias",
            _rename(following_lateral_offset(steps=steps, dt=dt), "A_angular_bias"),
            LatentLinkParameters(alpha_loss=1.0, delta_beam_rad=0.04, k_angular=1.0),
            broad,
            "boresight mismatch with directional motion sensitivity",
        ),
        CalibrationScenario(
            "B_distance_loss_mismatch",
            _rename(overtake(steps=steps, dt=dt), "B_distance_loss_mismatch"),
            LatentLinkParameters(alpha_loss=1.15, delta_beam_rad=0.0, k_angular=1.0),
            broad,
            "distance-loss mismatch",
        ),
        CalibrationScenario(
            "C_combined_ambiguity",
            _rename(intersection_turn(steps=steps, dt=dt), "C_combined_ambiguity"),
            LatentLinkParameters(alpha_loss=1.15, delta_beam_rad=-0.04, k_angular=0.75),
            broad,
            "multiple latent effects with geometry-dependent distinguishability",
        ),
        CalibrationScenario(
            "D_model_already_accurate",
            _rename(overtake(steps=steps, dt=dt), "D_model_already_accurate"),
            LatentLinkParameters(),
            narrow,
            "nominal truth and narrow prior; useful information should be limited",
        ),
        CalibrationScenario(
            "E_decision_irrelevant_uncertainty",
            _straight_decision_irrelevant(steps, dt),
            LatentLinkParameters(alpha_loss=1.15, delta_beam_rad=0.04, k_angular=1.25),
            broad,
            "broad parameter uncertainty but a mobility-dominant common decision",
        ),
        CalibrationScenario(
            "F_decision_critical_uncertainty",
            _rename(lane_choice(steps=steps, dt=dt), "F_decision_critical_uncertainty"),
            LatentLinkParameters(alpha_loss=0.85, delta_beam_rad=0.04, k_angular=1.25),
            broad,
            "competing safe trajectories whose communication ranking can change",
        ),
    ]
