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


def straight_lane_with_offset_event(steps=31, dt=0.1):
    """Two-vehicle scenario where lateral repositioning changes link geometry."""
    t = np.arange(steps) * dt
    ego = np.array([0.0, 0.0, 0.0, 10.0], dtype=float)
    target = np.zeros((steps, 4), dtype=float)
    target[:, 0] = 18.0 + 8.0 * t
    target[:, 1] = 0.9 * np.sin(0.7 * t)
    target[:, 2] = 0.0
    target[:, 3] = 8.0
    return Scenario(
        name="following_lateral_offset",
        ego_state=ego,
        target_states=target,
        obstacles=[],
        reference_speed=10.0,
    )


def lane_choice_event(steps=31, dt=0.1):
    """Scenario with an obstacle in the center and two lateral alternatives."""
    t = np.arange(steps) * dt
    ego = np.array([0.0, 0.0, 0.0, 10.0], dtype=float)
    target = np.zeros((steps, 4), dtype=float)
    target[:, 0] = 20.0 + 8.0 * t
    target[:, 1] = 1.2
    target[:, 3] = 8.0
    obstacles = [(18.0, 0.0, 1.0), (24.0, 0.0, 1.0)]
    return Scenario("lane_choice", ego, target, obstacles, 10.0)


def make_primary_scenarios():
    return [straight_lane_with_offset_event(), lane_choice_event()]
