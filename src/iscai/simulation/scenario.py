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


def _target(t, x0=18.0, speed=7.0, y=1.0):
    target = np.zeros((len(t), 4), dtype=float)
    target[:, 0] = x0 + speed * t
    target[:, 1] = y
    target[:, 3] = speed
    return target


def following_lateral_offset(steps=41, dt=0.1):
    t = np.arange(steps) * dt
    target = _target(t, x0=16.0, speed=6.0, y=0.0)
    target[:, 1] = 1.4 * np.clip((t - 0.8) / 1.8, 0.0, 1.0)
    return Scenario("following_lateral_offset", np.array([0., 0., 0., 10.]), target, [], 10.0)


def lane_choice(steps=41, dt=0.1):
    t = np.arange(steps) * dt
    target = _target(t, x0=18.0, speed=7.0, y=1.0)
    obstacles = [(15.0, 0.0, 1.0), (22.0, 0.0, 1.0)]
    return Scenario("lane_choice", np.array([0., 0., 0., 10.]), target, obstacles, 10.0)


def overtake(steps=51, dt=0.1):
    t = np.arange(steps) * dt
    target = _target(t, x0=14.0, speed=7.0, y=0.0)
    target[:, 1] = 0.35 * np.sin(0.5 * t)
    return Scenario("overtake", np.array([0., 0., 0., 9.]), target, [], 11.0)


def intersection_turn(steps=51, dt=0.1):
    t = np.arange(steps) * dt
    target = _target(t, x0=18.0, speed=6.0, y=0.8)
    turn = np.clip((t - 2.0) / 1.5, 0.0, 1.0)
    target[:, 1] = 0.8 - 1.6 * turn
    target[:, 2] = -0.35 * turn
    return Scenario("intersection_turn", np.array([0., 0., 0., 9.]), target, [], 9.0)


def occluding_cut_in(steps=51, dt=0.1):
    t = np.arange(steps) * dt
    target = _target(t, x0=20.0, speed=8.0, y=1.1)
    cut = np.clip((t - 1.2) / 1.2, 0.0, 1.0)
    target[:, 1] = 1.1 - 1.6 * cut
    obstacles = [(20.0, 0.0, 1.0), (26.0, -0.8, 1.0)]
    return Scenario("occluding_cut_in", np.array([0., 0., 0., 10.]), target, obstacles, 10.0)


def make_primary_scenarios():
    """Return the five scenario families used for the first experimental matrix."""
    return [following_lateral_offset(), lane_choice(), overtake(), intersection_turn(), occluding_cut_in()]
