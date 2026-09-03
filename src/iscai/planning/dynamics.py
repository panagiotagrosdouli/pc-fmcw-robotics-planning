"""Vehicle dynamics for the Stage 9 robotics planner."""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class VehicleParams:
    wheelbase: float = 2.7
    dt: float = 0.1
    max_accel: float = 2.5
    min_accel: float = -4.0
    max_steering: float = 0.5
    max_lateral_accel: float = 3.0


def step(state: np.ndarray, control: np.ndarray, params: VehicleParams) -> np.ndarray:
    """Advance [x, y, yaw, v] with control [acceleration, steering]."""
    x, y, yaw, velocity = np.asarray(state, dtype=float)
    acceleration, steering = np.asarray(control, dtype=float)
    acceleration = np.clip(acceleration, params.min_accel, params.max_accel)
    steering = np.clip(steering, -params.max_steering, params.max_steering)
    velocity_next = max(0.0, velocity + acceleration * params.dt)
    x_next = x + velocity * np.cos(yaw) * params.dt
    y_next = y + velocity * np.sin(yaw) * params.dt
    yaw_next = yaw + velocity / params.wheelbase * np.tan(steering) * params.dt
    return np.array([x_next, y_next, yaw_next, velocity_next])


def rollout(state: np.ndarray, controls: np.ndarray, params: VehicleParams) -> np.ndarray:
    """Roll out a control sequence and return states including the initial state."""
    states = [np.asarray(state, dtype=float)]
    current = states[0]
    for control in controls:
        current = step(current, control, params)
        states.append(current)
    return np.asarray(states)
