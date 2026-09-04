"""Matched-run identifiers for counterfactual trajectory exports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class CounterfactualKey:
    scenario: str
    seed: int


def matched_counterfactual_key(scenario: str, seed: int) -> CounterfactualKey:
    return CounterfactualKey(str(scenario), int(seed))
