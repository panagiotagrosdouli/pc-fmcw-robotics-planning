"""Interpretable candidate trajectory generation."""

from dataclasses import dataclass
import numpy as np

from .dynamics import VehicleParams, rollout


@dataclass
class CandidateTrajectory:
    states: np.ndarray
    controls: np.ndarray
    horizon: float
    lateral_offset: float
    target_speed: float
    feasible: bool = True


def quintic_coefficients(d0, d1, T):
    """Return quintic coefficients for zero initial/final derivatives."""
    A = np.array([[T**3, T**4, T**5], [3*T**2, 4*T**3, 5*T**4], [6*T, 12*T**2, 20*T**3]])
    b = np.array([d1 - d0, 0.0, 0.0])
    return np.array([d0, 0.0, 0.0, *np.linalg.solve(A, b)])


def generate_candidates(
    state: np.ndarray,
    lateral_offsets=(-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5),
    horizons=(2.0, 3.0, 4.0, 5.0),
    speed_offsets=(-2.0, 0.0, 2.0),
    params: VehicleParams | None = None,
) -> list[CandidateTrajectory]:
    """Generate dynamically consistent candidates in the ego-heading frame.

    A quintic lateral profile supplies the desired lateral acceleration. That
    acceleration is converted to steering and propagated once through the
    kinematic bicycle model. We deliberately do not add the quintic lateral
    displacement to the rolled-out positions afterwards: doing both would
    count the same lateral maneuver twice and make candidate geometry
    inconsistent with the controls that are actually executed.
    """
    params = params or VehicleParams()
    state = np.asarray(state, dtype=float)
    candidates = []
    for lateral_offset in lateral_offsets:
        for horizon in horizons:
            steps = max(2, int(round(horizon / params.dt)))
            t = np.linspace(0.0, horizon, steps + 1)
            coeff = quintic_coefficients(0.0, lateral_offset, horizon)
            lateral = sum(coeff[i] * t**i for i in range(6))
            lateral_rate = np.gradient(lateral, t)
            lateral_acc = np.gradient(lateral_rate, t)
            for speed_offset in speed_offsets:
                target_speed = max(0.0, state[3] + speed_offset)
                controls = np.zeros((steps, 2))
                controls[:, 0] = (target_speed - state[3]) / horizon
                speed_for_steering = max(float(state[3]), 0.1)
                controls[:, 1] = np.arctan2(
                    lateral_acc[:-1] * params.wheelbase,
                    speed_for_steering**2,
                )
                controls[:, 1] = np.clip(
                    controls[:, 1], -params.max_steering, params.max_steering
                )
                states = rollout(state, controls, params)
                candidates.append(
                    CandidateTrajectory(states, controls, horizon, lateral_offset, target_speed)
                )
    return candidates
