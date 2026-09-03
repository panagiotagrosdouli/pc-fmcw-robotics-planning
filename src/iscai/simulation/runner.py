"""Closed-loop experiment runner for Stage 9."""

from dataclasses import dataclass
import numpy as np

from ..planning.dynamics import VehicleParams, step


@dataclass
class EpisodeResult:
    planner: str
    scenario: str
    travel_time: float
    path_length: float
    outage_fraction: float
    link_lifetime: float
    min_obstacle_distance: float
    actions: np.ndarray


def _first_control(result):
    if result.candidate is None or len(result.candidate.controls) == 0:
        return np.zeros(2)
    return np.asarray(result.candidate.controls[0], dtype=float)


def run_episode(planner, scenario, planner_name="planner", params=None, dt=0.1):
    """Run a deterministic receding-horizon episode."""
    params = params or VehicleParams(dt=dt)
    ego = np.asarray(scenario.ego_state, dtype=float).copy()
    target = np.asarray(scenario.target_states, dtype=float)
    actions = []
    outage = []
    min_clearance = np.inf
    positions = [ego[:2].copy()]

    for k in range(len(target) - 1):
        result = planner.plan(
            ego_state=ego,
            target_prediction=target[k:],
            obstacles=scenario.obstacles,
            reference_speed=scenario.reference_speed,
        )
        u = _first_control(result)
        actions.append(u)
        outage.append(0.0 if result.forecast is None else float(np.mean(result.forecast.outage_probability)))
        ego = step(ego, u, params)
        positions.append(ego[:2].copy())

        for ox, oy, radius in scenario.obstacles:
            min_clearance = min(min_clearance, np.hypot(ego[0] - ox, ego[1] - oy) - radius)

    positions = np.asarray(positions)
    actions = np.asarray(actions)
    outage_fraction = float(np.mean(outage)) if outage else 0.0
    link_lifetime = float((1.0 - outage_fraction) * max(0, len(outage) - 1) * dt)
    path_length = float(np.sum(np.linalg.norm(np.diff(positions, axis=0), axis=1)))
    return EpisodeResult(
        planner=planner_name,
        scenario=scenario.name,
        travel_time=max(0, len(target) - 1) * dt,
        path_length=path_length,
        outage_fraction=outage_fraction,
        link_lifetime=link_lifetime,
        min_obstacle_distance=float(min_clearance),
        actions=actions,
    )
