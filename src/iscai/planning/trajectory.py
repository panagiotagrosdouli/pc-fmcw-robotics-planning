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


def _quintic_second_derivative(coeff, t):
    """Evaluate the analytic second derivative of a quintic polynomial."""
    t = np.asarray(t, dtype=float)
    return 2.0 * coeff[2] + 6.0 * coeff[3] * t + 12.0 * coeff[4] * t**2 + 20.0 * coeff[5] * t**3


def _controls_for_lateral_profile(state, lateral_offset, horizon, acceleration, params):
    """Build bounded steering controls for a lateral quintic and fixed acceleration."""
    steps = max(2, int(round(horizon / params.dt)))
    control_t = np.arange(steps, dtype=float) * params.dt
    coeff = quintic_coefficients(0.0, lateral_offset, horizon)
    lateral_acc = _quintic_second_derivative(coeff, control_t)
    controls = np.zeros((steps, 2), dtype=float)
    controls[:, 0] = float(np.clip(acceleration, params.min_accel, params.max_accel))
    speed_profile = np.maximum(0.1, state[3] + controls[0, 0] * control_t)
    controls[:, 1] = np.arctan2(lateral_acc * params.wheelbase, speed_profile**2)
    controls[:, 1] = np.clip(controls[:, 1], -params.max_steering, params.max_steering)
    return controls


def generate_candidates(
    state: np.ndarray,
    lateral_offsets=(-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5),
    horizons=(2.0, 3.0, 4.0, 5.0),
    speed_offsets=(-2.0, 0.0, 2.0),
    params: VehicleParams | None = None,
) -> list[CandidateTrajectory]:
    """Generate nominal and shared emergency-envelope trajectory candidates.

    The nominal lattice combines lateral quintics with speed targets. The
    emergency family combines maximum physically permitted braking with the
    same lateral offsets at every horizon. This permits braking-plus-evasion
    instead of assuming that a straight stop is always geometrically feasible.
    The emergency family is identical for P0--P4 and contains no communication
    information. Road, speed, static-obstacle, and dynamic-target filters still
    decide feasibility.
    """
    params = params or VehicleParams()
    state = np.asarray(state, dtype=float)
    candidates = []
    for lateral_offset in lateral_offsets:
        for horizon in horizons:
            for speed_offset in speed_offsets:
                target_speed = max(0.0, state[3] + speed_offset)
                requested_accel = (target_speed - state[3]) / horizon
                acceleration = float(np.clip(requested_accel, params.min_accel, params.max_accel))
                controls = _controls_for_lateral_profile(state, lateral_offset, horizon, acceleration, params)
                states = rollout(state, controls, params)
                candidates.append(CandidateTrajectory(states, controls, horizon, lateral_offset, target_speed))

    # Shared emergency envelope: maximum braking plus each available lateral
    # profile. This is a structural safety fix motivated by development-only
    # failure analysis, not a communication-specific optimization.
    for lateral_offset in lateral_offsets:
        for horizon in horizons:
            controls = _controls_for_lateral_profile(
                state, lateral_offset, horizon, params.min_accel, params
            )
            states = rollout(state, controls, params)
            candidates.append(CandidateTrajectory(states, controls, horizon, lateral_offset, 0.0))
    return candidates
