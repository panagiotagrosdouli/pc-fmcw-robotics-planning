"""Hard safety and feasibility filters."""

import numpy as np


def check_road_bounds(states: np.ndarray, lane_half_width: float = 1.75) -> bool:
    return bool(np.all(np.abs(states[:, 1]) <= lane_half_width))


def check_speed(states: np.ndarray, min_speed: float = 0.0, max_speed: float = 30.0) -> bool:
    return bool(np.all((states[:, 3] >= min_speed) & (states[:, 3] <= max_speed)))


def check_obstacles(states: np.ndarray, obstacles: np.ndarray, min_clearance: float = 1.5) -> bool:
    """Check clearance from obstacles represented as [x, y] or [x, y, radius]."""
    if len(obstacles) == 0:
        return True
    obs = np.asarray(obstacles, dtype=float)
    distances = np.linalg.norm(states[:, None, :2] - obs[None, :, :2], axis=-1)
    radii = obs[:, 2] if obs.shape[1] >= 3 else np.zeros(len(obs))
    clearance = distances - radii[None, :]
    return bool(np.all(clearance >= min_clearance))


def filter_feasible(candidates, obstacles=None, lane_half_width=1.75, min_clearance=1.5):
    obstacles = np.empty((0, 3)) if obstacles is None else np.asarray(obstacles, dtype=float)
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
