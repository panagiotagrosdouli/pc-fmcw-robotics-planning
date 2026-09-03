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
    """Run a short deterministic receding-horizon episode.

    The target trajectory is simulator ground truth; a predictive planner may use it
    as its forecast, while the reactive baseline intentionally collapses it to the
    current state inside its planner implementation.
    """
    params = params or VehicleParams(dt=dt)
    ego = np.asarray(scenario.ego_state, dtype=float).copy()
    target = np.asarray(scenario.target_states, dtype=float)
    actions = []
    outage = []
    min_clearance = np.inf

    for k in range(len(target) - 1):
        target_future = target[k:]
        result = planner.plan(
            ego_state=ego,
            target_prediction=target_future,
            obstacles=scenario.obstacles,
            reference_speed=scenario.reference_speed,
        )
        u = _first_control(result)
        actions.append(u)
        if result.forecast is None:
            outage.append(0.0)
        else:
            outage.append(float(np.mean(result.forecast.outage_probability)))
        ego = step(ego, u, params)

        for ox, oy, radius in scenario.obstacles:
            d = np.hypot(ego[0] - ox, ego[1] - oy) - radius
            min_clearance = min(min_clearance, d)

    actions = np.asarray(actions)
    outage_fraction = float(np.mean(outage)) if outage else 0.0
    link_lifetime = float((1.0 - outage_fraction) * max(0, len(outage) - 1) * dt)
    path_length = float(np.sum(np.linalg.norm(np.diff(np.vstack(([scenario.ego_state[:2]], ego[:2]))), axis=1)))
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
