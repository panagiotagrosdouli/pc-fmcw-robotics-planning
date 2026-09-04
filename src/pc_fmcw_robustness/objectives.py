"""Composable connectivity objectives for planner integration."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .risk import adaptive_connectivity_weight, chance_violation_probability, cvar


@dataclass(frozen=True)
class RiskObjectiveConfig:
    expected_weight: float = 1.0
    risk_weight: float = 0.0
    cvar_alpha: float = 0.9


@dataclass(frozen=True)
class ChanceConstraintConfig:
    snr_threshold_db: float
    max_violation_probability: float
    penalty: float = 1e6


@dataclass(frozen=True)
class AdaptiveWeightConfig:
    base_weight: float
    max_weight: float
    activation_threshold: float


def risk_aware_connectivity_cost(cost_samples, config: RiskObjectiveConfig) -> float:
    values = np.asarray(cost_samples, dtype=float)
    if values.size == 0:
        raise ValueError("cost_samples must be non-empty")
    mean_cost = float(np.mean(values))
    tail_cost = cvar(values, config.cvar_alpha)
    return float(config.expected_weight * mean_cost + config.risk_weight * tail_cost)


def chance_constrained_cost(base_cost: float, snr_samples_db, config: ChanceConstraintConfig) -> tuple[float, float, bool]:
    probability = chance_violation_probability(snr_samples_db, config.snr_threshold_db)
    feasible = probability <= config.max_violation_probability
    cost = float(base_cost) if feasible else float(base_cost) + float(config.penalty)
    return cost, probability, feasible


def adaptive_weighted_cost(base_connectivity_cost: float, outage_probability: float, config: AdaptiveWeightConfig) -> tuple[float, float]:
    weight = adaptive_connectivity_weight(
        outage_probability,
        config.base_weight,
        config.max_weight,
        config.activation_threshold,
    )
    return float(weight * float(base_connectivity_cost)), weight
