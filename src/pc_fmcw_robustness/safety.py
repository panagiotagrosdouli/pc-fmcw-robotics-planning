"""Safety/connectivity decoupling helpers."""

from __future__ import annotations


def safety_feasible(collision_probability: float, delta: float) -> bool:
    """Return whether a trajectory satisfies an explicit collision-risk bound."""
    p = float(collision_probability)
    d = float(delta)
    if not 0.0 <= p <= 1.0:
        raise ValueError("collision_probability must be in [0, 1]")
    if not 0.0 <= d <= 1.0:
        raise ValueError("delta must be in [0, 1]")
    return p <= d
