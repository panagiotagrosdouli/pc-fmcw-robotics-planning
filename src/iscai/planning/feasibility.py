"""Hard safety and feasibility filters."""

import numpy as np
from .dynamics import VehicleParams, rollout


def check_road_bounds(states: np.ndarray, lane_half_width: float = 1.75) -> bool:
    return bool(np.all(np.abs(states[:, 1]) <= lane_half_width))


def check_speed(states: np.ndarray, min_speed: float = 0.0, max_speed: float = 30.0) -> bool:
    return bool(np.all((states[:, 3] >= min_speed) & (states[:, 3] <= max_speed)))


def check_obstacles(states: np.ndarray, obstacles: np.ndarray, min_clearance: float = 1.5) -> bool:
    """Check clearance from static obstacles represented as [x, y] or [x, y, radius]."""
    if len(obstacles) == 0:
        return True
    obs = np.asarray(obstacles, dtype=float)
    distances = np.linalg.norm(states[:, None, :2] - obs[None, :, :2], axis=-1)
    radii = obs[:, 2] if obs.shape[1] >= 3 else np.zeros(len(obs))
    clearance = distances - radii[None, :]
    return bool(np.all(clearance >= min_clearance))


def check_static_stop_viability(states: np.ndarray, obstacles: np.ndarray,
                                params: VehicleParams, min_clearance: float = 1.5) -> bool:
    """Check the bounded straight-braking continuation from a candidate endpoint.

    This is a necessary static safety check for the lattice, not a proof of
    recursive feasibility against moving targets.
    """
    if len(obstacles) == 0:
        return True
    endpoint = np.asarray(states[-1], dtype=float)
    steps = max(1, int(np.ceil(endpoint[3] / (-params.min_accel * params.dt))) + 1)
    controls = np.tile([params.min_accel, 0.0], (steps, 1))
    continuation = rollout(endpoint, controls, params)
    return check_road_bounds(continuation) and check_obstacles(continuation, obstacles, min_clearance)


def check_dynamic_target(states: np.ndarray, target_xy: np.ndarray, min_clearance: float = 2.0,
                         time_aligned: bool = False) -> bool:
    """Check time-aligned clearance to a predicted moving target."""
    states = np.asarray(states, dtype=float)
    target_xy = np.asarray(target_xy, dtype=float)
    if target_xy.size == 0:
        return True
    if target_xy.ndim != 2 or target_xy.shape[1] < 2:
        raise ValueError("target_xy must have shape (H, >=2)")
    # A rollout includes the current ego state at index zero, whereas the
    # forecast begins at the *next* simulation step. Historical protocols
    # retain their old indexing unless the V5 correction is enabled.
    if time_aligned:
        states = states[1:]
    n = min(len(states), len(target_xy))
    if n == 0:
        return True
    distance = np.linalg.norm(states[:n, :2] - target_xy[:n, :2], axis=1)
    return bool(np.all(distance >= min_clearance))


def _extend_target_cv(target_xy: np.ndarray, steps: int) -> np.ndarray:
    """Extend the common mean forecast using its last observed displacement."""
    target = np.asarray(target_xy, dtype=float)[:, :2]
    if len(target) >= steps:
        return target[:steps]
    if len(target) == 0:
        raise ValueError("a target forecast is required")
    delta = target[-1] - target[-2] if len(target) > 1 else np.zeros(2)
    extra = target[-1] + np.arange(1, steps - len(target) + 1)[:, None] * delta
    return np.vstack([target, extra])


def check_dynamic_stop_viability(states: np.ndarray, target_xy: np.ndarray,
                                 params: VehicleParams, min_clearance: float = 2.0) -> bool:
    """Check a predicted target while braking straight after the candidate ends.

    This is a necessary continuation witness in the shared mean prediction,
    not a guarantee against unmodeled target maneuvers or observation noise.
    """
    endpoint = np.asarray(states[-1], dtype=float)
    steps = max(1, int(np.ceil(endpoint[3] / (-params.min_accel * params.dt))) + 1)
    continuation = rollout(endpoint, np.tile([params.min_accel, 0.0], (steps, 1)), params)
    target = _extend_target_cv(target_xy, len(states) - 1 + steps)
    return check_dynamic_target(continuation[1:], target[len(states)-1:], min_clearance)


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


def filter_dynamic_target(candidates, target_xy, min_clearance=2.0):
    """Hard-filter candidates against a time-aligned moving target trajectory."""
    if target_xy is None:
        return list(candidates)
    feasible = []
    for candidate in candidates:
        ok = check_dynamic_target(candidate.states, target_xy, min_clearance)
        candidate.feasible = bool(candidate.feasible and ok)
        if candidate.feasible:
            feasible.append(candidate)
    return feasible


def filter_with_diagnostics(candidates, target_xy=None, obstacles=None,
                            lane_half_width=1.75, static_clearance=1.5,
                            target_clearance=2.0, require_static_stop_viability=False,
                            vehicle_params=None, time_aligned_dynamic=False,
                            require_dynamic_stop_viability=False):
    """Apply all hard filters once and return mutually exclusive rejection counts."""
    obstacles = np.empty((0, 3)) if obstacles is None else np.asarray(obstacles, dtype=float)
    counts = {"generated": len(candidates), "road": 0, "speed": 0,
              "static": 0, "dynamic": 0, "feasible": 0}
    feasible = []
    for candidate in candidates:
        if not check_road_bounds(candidate.states, lane_half_width):
            counts["road"] += 1
        elif not check_speed(candidate.states):
            counts["speed"] += 1
        elif not check_obstacles(candidate.states, obstacles, static_clearance) or (
            require_static_stop_viability and not check_static_stop_viability(
                candidate.states, obstacles, vehicle_params or VehicleParams(), static_clearance
            )
        ):
            counts["static"] += 1
        elif target_xy is not None and (
            not check_dynamic_target(
                candidate.states,
                _extend_target_cv(target_xy, len(candidate.states)-1) if time_aligned_dynamic else target_xy,
                target_clearance, time_aligned_dynamic
            ) or (require_dynamic_stop_viability and not check_dynamic_stop_viability(
                candidate.states, target_xy, vehicle_params or VehicleParams(), target_clearance
            ))
        ):
            counts["dynamic"] += 1
        else:
            counts["feasible"] += 1
            feasible.append(candidate)
            continue
        candidate.feasible = False
    return feasible, counts
