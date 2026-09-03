"""Deterministic synthetic scenarios for connectivity-aware planning."""

from dataclasses import dataclass
import numpy as np


@dataclass
class Scenario:
    name: str
    ego_state: np.ndarray
    target_states: np.ndarray
    obstacles: list
    reference_speed: float


def straight_lane_with_offset_event(steps=41, dt=0.1):
    """Target changes lateral position; prediction creates a proactive geometry choice."""
    t = np.arange(steps) * dt
    ego = np.array([0.0, 0.0, 0.0, 10.0], dtype=float)
    target = np.zeros((steps, 4), dtype=float)
    target[:, 0] = 16.0 + 6.0 * t
    target[:, 1] = 1.4 * np.clip((t - 0.8) / 1.8, 0.0, 1.0)
    target[:, 2] = 0.0
    target[:, 3] = 6.0
    return Scenario(
        name="following_lateral_offset",
        ego_state=ego,
        target_states=target,
        obstacles=[],
        reference_speed=10.0,
    )


def lane_choice_event(steps=41, dt=0.1):
    """Obstacle forces a lateral choice while the target occupies the preferred link geometry."""
    ego = np.array([0.0, 0.0, 0.0, 10.0], dtype=float)
    t = np.arange(steps) * dt
    target = np.zeros((steps, 4), dtype=float)
    target[:, 0] = 18.0 + 7.0 * t
    target[:, 1] = 1.0
    target[:, 2] = 0.0
    target[:, 3] = 7.0
    obstacles = [(15.0, 0.0), (22.0, 0.0)]
    return Scenario("lane_choice", ego, target, obstacles, 10.0)


def make_primary_scenarios():
    return [straight_lane_with_offset_event(), lane_choice_event()]
