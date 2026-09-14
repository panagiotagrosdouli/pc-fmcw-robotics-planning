"""Decision-level metrics for communication-forecast actionability.

This module is intentionally outcome-agnostic at selection time. Candidate
selection consumes only forecast intervals, empirical support flags, and
mobility penalties. Realized outcomes are accepted only by post-selection
assessment helpers such as :func:`decision_regret`.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ActionabilityChoice:
    index: int
    changed: bool
    net_conservative_gain: float


def conservative_gain_lower_is_better(reference_lower: float, candidate_upper: float) -> float:
    """Worst-case forecast gain when a smaller QoS quantity is preferable."""
    return float(reference_lower - candidate_upper)


def select_actionable_candidate(
    lower_bounds,
    upper_bounds,
    supported,
    mobility_penalties,
    *,
    reference_index: int = 0,
    min_net_gain: float = 0.0,
) -> ActionabilityChoice:
    """Select a candidate using decision-time information only.

    The first/reference action is returned unless a supported alternative has
    strictly positive conservative gain after the mobility penalty and the
    frozen minimum net-gain threshold. No realized/future QoS argument exists
    by design, preventing outcome leakage through this API.
    """
    lower = np.asarray(lower_bounds, dtype=float)
    upper = np.asarray(upper_bounds, dtype=float)
    support = np.asarray(supported, dtype=bool)
    mobility = np.asarray(mobility_penalties, dtype=float)

    n = len(lower)
    if not (len(upper) == len(support) == len(mobility) == n):
        raise ValueError("all candidate arrays must have the same length")
    if n == 0:
        raise ValueError("at least one candidate is required")
    if not 0 <= reference_index < n:
        raise IndexError("reference_index out of range")
    if not np.all(np.isfinite(lower)) or not np.all(np.isfinite(upper)):
        raise ValueError("forecast bounds must be finite")
    if not np.all(np.isfinite(mobility)) or np.any(mobility < 0.0):
        raise ValueError("mobility penalties must be finite and non-negative")
    if not np.isfinite(min_net_gain) or min_net_gain < 0.0:
        raise ValueError("min_net_gain must be finite and non-negative")

    ref_lower = lower[reference_index]
    best_index = reference_index
    best_net = 0.0

    for idx in range(n):
        if idx == reference_index or not support[idx]:
            continue
        gain = conservative_gain_lower_is_better(ref_lower, upper[idx])
        net = gain - mobility[idx]
        if net > min_net_gain and net > best_net:
            best_index = idx
            best_net = float(net)

    return ActionabilityChoice(
        index=best_index,
        changed=best_index != reference_index,
        net_conservative_gain=best_net,
    )


def realized_change_lower_is_better(reference_loss: float, chosen_loss: float) -> float:
    """Positive values mean the selected action improved realized QoS."""
    return float(reference_loss - chosen_loss)


def decision_regret(chosen_loss: float, candidate_realized_losses) -> float:
    """Post-selection regret over a legitimately observed candidate set."""
    losses = np.asarray(candidate_realized_losses, dtype=float)
    if losses.size == 0 or not np.all(np.isfinite(losses)):
        raise ValueError("candidate realized losses must be non-empty and finite")
    if not np.isfinite(chosen_loss):
        raise ValueError("chosen_loss must be finite")
    return float(chosen_loss - np.min(losses))


def changed_action_outcome(reference_loss: float, chosen_loss: float, *, atol: float = 0.0) -> str:
    """Classify a changed action as beneficial, harmful, or neutral."""
    delta = realized_change_lower_is_better(reference_loss, chosen_loss)
    if delta > atol:
        return "beneficial"
    if delta < -atol:
        return "harmful"
    return "neutral"
