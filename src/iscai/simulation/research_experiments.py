"""Protocol-driven experiment matrix for the communication-uncertainty study."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable

import yaml

from .research_benchmark import RESEARCH_PLANNERS, ResearchBenchmarkSettings, run_research_benchmark


@dataclass(frozen=True)
class ExperimentSpec:
    experiment: str
    setting_id: str
    settings: ResearchBenchmarkSettings
    planners: tuple[str, ...]

    def manifest(self) -> dict:
        return {
            "experiment": self.experiment,
            "setting_id": self.setting_id,
            "planners": list(self.planners),
            "settings": asdict(self.settings),
        }


def load_research_config(path="configs/research_framework.yaml") -> dict:
    config = yaml.safe_load(Path(path).read_text())
    if config.get("protocol_version") != "research-framework-v1":
        raise ValueError("research config must use protocol_version=research-framework-v1")
    return config


def _steps(seconds: float, dt: float) -> int:
    value = int(round(float(seconds) / float(dt)))
    if value < 1:
        raise ValueError("predictive horizons must contain at least one step")
    return value


def _validate_planners(planners: Iterable[str]) -> tuple[str, ...]:
    names = tuple(planners)
    unknown = set(names) - set(RESEARCH_PLANNERS)
    if unknown:
        raise ValueError(f"unknown research planners: {sorted(unknown)}")
    return names


def build_experiment_specs(mode: str, config: dict | None = None,
                           base: ResearchBenchmarkSettings | None = None) -> list[ExperimentSpec]:
    """Build a predeclared experiment family without inspecting outcomes."""
    cfg = load_research_config() if config is None else config
    base = base or ResearchBenchmarkSettings(mc_samples=int(cfg["benchmark"]["mc_samples"]))
    all_planners = _validate_planners(cfg["benchmark"]["planners"])
    mode = str(mode).lower()
    specs: list[ExperimentSpec] = []

    if mode == "core":
        specs.append(ExperimentSpec("core", "nominal", base, all_planners))

    elif mode == "horizon":
        planners = ("P1", "P2", "P3", "P4", "P2-CVaR", "P2-Chance", "P2-Adaptive")
        for horizon_s in cfg["prediction_horizon_s"]:
            settings = replace(base, horizon_steps=_steps(horizon_s, base.dt))
            specs.append(ExperimentSpec("horizon", f"H={float(horizon_s):g}s", settings, planners))

    elif mode == "weight":
        planners = ("P0", "P1", "P2", "P3", "P2-CVaR", "P2-Chance", "P2-Adaptive")
        for weight in cfg["connectivity_weights"]:
            max_adaptive = max(float(weight), float(base.adaptive_max_connectivity_weight))
            settings = replace(base, connectivity_weight=float(weight), adaptive_max_connectivity_weight=max_adaptive)
            specs.append(ExperimentSpec("weight", f"lambda={float(weight):g}", settings, planners))

    elif mode == "risk":
        for alpha in cfg["risk_aware"]["cvar_alpha_values"]:
            for risk_weight in cfg["risk_aware"]["cvar_weights"]:
                settings = replace(base, cvar_alpha=float(alpha), cvar_weight=float(risk_weight))
                specs.append(ExperimentSpec("risk", f"cvar_a={alpha}_w={risk_weight}", settings, ("P2", "P3", "P2-CVaR", "P2-Worst")))
        for epsilon in cfg["chance_constraints"]["max_violation_probabilities"]:
            settings = replace(
                base,
                chance_max_violation_probability=float(epsilon),
                chance_hard_constraint=bool(cfg["chance_constraints"]["hard_constraint"]),
                chance_violation_penalty=float(cfg["chance_constraints"]["soft_penalty"]),
            )
            specs.append(ExperimentSpec("risk", f"chance_eps={float(epsilon):g}", settings, ("P2", "P2-Chance")))
        for base_weight in cfg["adaptive_weight"]["base_weights"]:
            for max_weight in cfg["adaptive_weight"]["max_weights"]:
                if float(max_weight) < float(base_weight):
                    continue
                for threshold in cfg["adaptive_weight"]["activation_thresholds"]:
                    settings = replace(
                        base,
                        connectivity_weight=float(base_weight),
                        adaptive_max_connectivity_weight=float(max_weight),
                        adaptive_activation_threshold=float(threshold),
                    )
                    specs.append(ExperimentSpec(
                        "risk",
                        f"adaptive_b={base_weight}_m={max_weight}_t={threshold}",
                        settings,
                        ("P2", "P2-Adaptive"),
                    ))

    elif mode == "shift":
        planners = ("P1", "P2", "P3", "P2-CVaR", "P2-Chance", "P2-Adaptive", "P2-Worst")
        shift = cfg["distribution_shift"]
        for bias in shift["prediction_bias_x_m"]:
            specs.append(ExperimentSpec("shift", f"pred_bias_x={float(bias):g}m", replace(base, prediction_bias_x_m=float(bias)), planners))
        for bias in shift["prediction_bias_y_m"]:
            specs.append(ExperimentSpec("shift", f"pred_bias_y={float(bias):g}m", replace(base, prediction_bias_y_m=float(bias)), planners))
        for scale in shift["prediction_noise_scale"]:
            specs.append(ExperimentSpec("shift", f"pred_noise={float(scale):g}", replace(base, prediction_noise_scale=float(scale)), planners))
        for scale in shift["reported_uncertainty_scale"]:
            specs.append(ExperimentSpec("shift", f"uncertainty_x={float(scale):g}", replace(base, reported_uncertainty_scale=float(scale)), planners))
        for delay_s in shift["observation_delay_s"]:
            delay_steps = int(round(float(delay_s) / base.dt))
            specs.append(ExperimentSpec("shift", f"delay={float(delay_s):g}s", replace(base, observation_delay_steps=delay_steps), planners))
        for bias in shift["reference_snr_bias_db"]:
            specs.append(ExperimentSpec("shift", f"snr_bias={float(bias):g}dB", replace(base, reference_snr_bias_db=float(bias)), planners))
        for scale in shift["pathloss_scale"]:
            specs.append(ExperimentSpec("shift", f"pathloss_x={float(scale):g}", replace(base, pathloss_scale=float(scale)), planners))
        for scale in shift["beam_sigma_scale"]:
            specs.append(ExperimentSpec("shift", f"beam_x={float(scale):g}", replace(base, beam_sigma_scale=float(scale)), planners))

    elif mode == "blackout":
        planners = ("P1", "P2", "P3", "P4", "P2-CVaR", "P2-Chance", "P2-Adaptive", "P2-Worst")
        blackout = cfg["blackout"]
        attenuation = float(blackout["attenuation_db"])
        for kind in blackout["kinds"]:
            for visibility in blackout["visibility"]:
                visible = str(visibility).lower() == "visible"
                settings = replace(
                    base,
                    blackout_kind=str(kind),
                    blackout_attenuation_db=attenuation,
                    blackout_visible_to_planner=visible,
                )
                specs.append(ExperimentSpec("blackout", f"{kind}_{visibility}", settings, planners))

    elif mode == "compute":
        planners = ("P2", "P3", "P2-CVaR", "P2-Chance", "P2-Worst")
        horizons = cfg["prediction_horizon_s"]
        mc_budgets = cfg["mc_sample_budgets"]
        for horizon_s in horizons:
            for mc_samples in mc_budgets:
                settings = replace(base, horizon_steps=_steps(horizon_s, base.dt), mc_samples=int(mc_samples))
                specs.append(ExperimentSpec("compute", f"H={float(horizon_s):g}s_mc={int(mc_samples)}", settings, planners))

    elif mode == "all":
        for family in ("core", "horizon", "weight", "risk", "shift", "blackout", "compute"):
            specs.extend(build_experiment_specs(family, cfg, base))
    else:
        raise ValueError("mode must be one of core,horizon,weight,risk,shift,blackout,compute,all")

    ids = [(s.experiment, s.setting_id) for s in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("experiment matrix contains duplicate setting IDs")
    return specs


def run_experiment_specs(specs: Iterable[ExperimentSpec], seeds, scenarios=None):
    """Execute specs and annotate every output with its experimental condition."""
    episode_rows = []
    trace_rows = []
    manifests = []
    for spec in specs:
        episodes, traces = run_research_benchmark(
            seeds=seeds,
            settings=spec.settings,
            scenarios=scenarios,
            planners=spec.planners,
        )
        for row in episodes:
            episode_rows.append({"experiment": spec.experiment, "setting_id": spec.setting_id, **row})
        for row in traces:
            trace_rows.append({"experiment": spec.experiment, "setting_id": spec.setting_id, **row})
        manifests.append(spec.manifest())
    return episode_rows, trace_rows, manifests
