"""Value-of-information utilities for matched planner comparisons."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InformationLevel:
    name: str
    deployable: bool
    description: str


INFORMATION_LEVELS = (
    InformationLevel("P1", True, "reactive/current connectivity only"),
    InformationLevel("P2", True, "causal future connectivity prediction"),
    InformationLevel("P3", True, "causal prediction with predictive uncertainty"),
    InformationLevel("P4", False, "oracle future connectivity upper bound"),
)


def planner_information_order():
    """Return the canonical information ladder used by value-of-information experiments."""
    return tuple(level.name for level in INFORMATION_LEVELS)
