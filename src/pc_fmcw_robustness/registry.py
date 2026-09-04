"""Registry of research planner variants and their information/risk semantics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannerVariant:
    name: str
    information: str
    risk_mode: str
    deployable: bool = True


RESEARCH_PLANNERS = (
    PlannerVariant("reactive", "current", "expected"),
    PlannerVariant("predictive", "causal_prediction", "expected"),
    PlannerVariant("predictive_cvar", "causal_prediction", "cvar"),
    PlannerVariant("predictive_chance", "causal_prediction", "chance_constraint"),
    PlannerVariant("predictive_adaptive", "causal_prediction", "adaptive_weight"),
    PlannerVariant("uncertainty_aware", "predictive_distribution", "expected"),
    PlannerVariant("oracle", "future_realized", "expected", deployable=False),
)


def planner_names():
    return tuple(p.name for p in RESEARCH_PLANNERS)
