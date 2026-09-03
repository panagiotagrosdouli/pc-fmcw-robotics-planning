"""Mobility and connectivity costs."""

import numpy as np


def mobility_cost(candidate, reference_speed=None):
    states = candidate.states
    controls = candidate.controls
    speed_error = 0.0 if reference_speed is None else np.mean((states[:, 3] - reference_speed) ** 2)
    acceleration = np.mean(controls[:, 0] ** 2) if len(controls) else 0.0
    steering = np.mean(controls[:, 1] ** 2) if len(controls) else 0.0
    lateral = np.mean(states[:, 1] ** 2)
    return float(lateral + speed_error + 0.1 * acceleration + 0.1 * steering)


def connectivity_cost(forecast):
    outage = float(np.mean(forecast.outage_probability))
    survival = float(forecast.survival_probability)
    return 0.7 * outage + 0.3 * (1.0 - survival)
