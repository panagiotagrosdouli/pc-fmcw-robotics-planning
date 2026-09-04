"""Manifest helpers for research-framework experiment provenance."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ResearchMethodManifest:
    protocol_version: str
    planner: str
    information_level: str
    risk_mode: str
    horizon_s: float
    mc_samples: int
    connectivity_weight: float

    def to_dict(self):
        return asdict(self)
