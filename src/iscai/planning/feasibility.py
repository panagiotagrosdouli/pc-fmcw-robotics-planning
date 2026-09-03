"""Hard safety and feasibility filters."""

import numpy as np


def check_road_bounds(states: np.ndarray, lane_half_width: float = 1.75) -> bool:
    return bool(np.all(np.abs(states[:, 1]) <= lane_half_width))


def check_speed(states: np.ndarray, min_speed: float = 0.0, max_speed: float = 30.0) -> bool:
    return bool(np.all((states[:, 3] >= min_speed) & (states[:, 3] <= max_speed)))


def check_obstacles(states: np.ndarray, obstacles: np.ndarray, min_clearance: float = 2.0) -> bool:
    """Check Euclidean clearance from point obstacles [x, y]."""
    if len(obstacles) == 0:
        return True
    distances = np.linalg.norm(states[:, None, :2] - obstacles[None, :, :2], axis=-1)
    return bool(np.all(distances >= min_clearance))


def filter_feasible(candidates, obstacles=None, lane_half_width=1.75, min_clearance=2.0):
    obstacles = np.empty((0, 2)) if obstacles is None else np.asarray(obstacles, dtype=float)
    feasible = []
    for candidate in candidates:
        ok = (
            check_road_bounds(candidate.states, lane_half_width)
            and check_speed(candidate.states)
            and check_obstacles(candidate.states, obstacles, min_clearance)
        )
        candidate.feasible = ok
        if ok:
            feasible.append(candidate)
    return feasible
