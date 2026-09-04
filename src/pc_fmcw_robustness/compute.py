"""Compute-budget declarations for matched planner evaluation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComputeBudget:
    horizon_steps: int
    mc_samples: int
    candidate_budget: int | None = None

    def __post_init__(self):
        if self.horizon_steps < 0:
            raise ValueError("horizon_steps must be non-negative")
        if self.mc_samples < 1:
            raise ValueError("mc_samples must be positive")
        if self.candidate_budget is not None and self.candidate_budget < 1:
            raise ValueError("candidate_budget must be positive when provided")
