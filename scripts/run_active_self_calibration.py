#!/usr/bin/env python3
"""Run smoke, development, or frozen confirmatory active-calibration experiments."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from iscai.active_self_calibration import (
    CalibrationBenchmarkSettings,ParameterizedPCFMCWLinkModel,
    make_identifiability_scenarios,run_study,
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_sha():
    try:
        return subprocess.check_output(
            ["git","rev-parse","HEAD"],cwd=ROOT,text=True,stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unavailable"


def _seed_values(config,phase,seed_start=None,seeds=None):
    if phase=="smoke":
        start=0 if seed_start is None else int(seed_start)
        count=1 if seeds is None else int(seeds)
        if count<1: raise SystemExit("--seeds must be >= 1")
        return list(range(start,start+count))
    lo,hi=config[phase]["seed_range"];declared=list(range(int(lo),int(hi)+1))
    if seed_start is not None or seeds is not None:
        start=int(lo if seed_start is None else seed_start)
        count=int(len(declared) if seeds is None else seeds)
        if count<1: raise SystemExit("--seeds must be >= 1")
        return list(range(start,start+count))
    return declared


def _hyperparameters(config,phase,args):
    defaults=dict(config["development"]["default_hyperparameters"])
    if phase=="confirmatory":
        if args.frozen_protocol is None:
            raise SystemExit("confirmatory execution requires --frozen-protocol")
        frozen=json.loads((ROOT/args.frozen_protocol).read_text(encoding="utf-8"))
        if frozen.get("protocol_version")!=config["protocol_version"]:
            raise SystemExit("frozen protocol version does not match config")
        if frozen.get("config_sha256")!=_sha256(ROOT/args.config):
            raise SystemExit("frozen protocol config digest does not match current config")
        return dict(frozen["selected_hyperparameters"]),frozen
    for cli_name,key in (
        ("decision_threshold","decision_threshold"),("information_weight","information_weight"),
        ("probe_weight","probe_weight"),("min_expected_regret","min_expected_regret"),
    ):
        value=getattr(args,cli_name)
        if value is not None: defaults[key]=float(value)
    return defaults,None


def _settings(config,hyper):
    s=config["simulation"]
    return CalibrationBenchmarkSettings(
        dt=float(s["dt"]),history_steps=int(s["history_steps"]),
        horizon_steps=int(s["horizon_steps"]),
        target_observation_sigma_m=float(s["target_observation_sigma_m"]),
        communication_observation_sigma_db=float(config["latent_model"]["observation_sigma_db"]),
        connectivity_weight=float(s["connectivity_weight"]),
        information_weight=float(hyper["information_weight"]),
        probe_weight=float(hyper["probe_weight"]),
        decision_threshold=float(hyper["decision_threshold"]),
        min_expected_regret=float(hyper.get("min_expected_regret",0.0)),
        information_horizon_steps=int(s["information_horizon_steps"]),
        collision_distance_m=float(s["collision_distance_m"]),
        planning_safety_margin_m=float(s["planning_safety_margin_m"]),
        candidate_lateral_offsets=tuple(s["candidate_lateral_offsets"]),
        candidate_horizons=tuple(s["candidate_horizons"]),
        candidate_speed_offsets=tuple(s["candidate_speed_offsets"]),
        require_static_stop_viability=bool(s["require_static_stop_viability"]),
        bounded_brake_steer=bool(s["bounded_brake_steer"]),
        time_aligned_dynamic=bool(s["time_aligned_dynamic"]),
        require_dynamic_stop_viability=bool(s["require_dynamic_stop_viability"]),
        hierarchical_clearance=bool(s["hierarchical_clearance"]),
        damped_lateral_prediction=bool(s["damped_lateral_prediction"]),
        endpoint_anchored_lateral=bool(s["endpoint_anchored_lateral"]),
    )


def _one_run(config,args,phase,hyper,seed_values,setting_id=None):
    settings=_settings(config,hyper)
    scenario_steps=int(args.scenario_steps or config["simulation"]["scenario_steps"])
    scenarios=make_identifiability_scenarios(steps=scenario_steps,dt=settings.dt)
    result=run_study(seeds=seed_values,settings=settings,scenarios=scenarios)
    episodes=pd.DataFrame(result["episodes"]);steps=pd.DataFrame(result["steps"])
    if setting_id is not None:
        episodes.insert(0,"setting_id",setting_id);steps.insert(0,"setting_id",setting_id)
    for key,value in hyper.items():
        episodes[key]=value;steps[key]=value
    return settings,episodes,steps


def _write_outputs(out,episodes,steps,manifest):
    out.mkdir(parents=True,exist_ok=True)
    episodes.to_csv(out/"episodes.csv",index=False);steps.to_csv(out/"steps.csv",index=False)
    summary=episodes.groupby("planner",as_index=False).agg(
        episodes=("seed","size"),collision_rate=("collision_indicator","mean"),
        mean_regret=("cumulative_decision_regret","mean"),
        mean_probe_fraction=("probe_fraction","mean"),
        mean_parameter_error=("final_parameter_error_normalized","mean"),
        mean_progress_m=("progress_m","mean"),mean_outage=("mean_outage_probability","mean"),
    )
    summary.to_csv(out/"summary.csv",index=False)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(summary.to_string(index=False))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,default=Path("configs/experiments/active_self_calibration.yaml"))
    p.add_argument("--phase",choices=("smoke","development","confirmatory"),default="smoke")
    p.add_argument("--output-dir",type=Path,default=None)
    p.add_argument("--seed-start",type=int,default=None);p.add_argument("--seeds",type=int,default=None)
    p.add_argument("--scenario-steps",type=int,default=None)
    p.add_argument("--decision-threshold",type=float,default=None)
    p.add_argument("--information-weight",type=float,default=None)
    p.add_argument("--probe-weight",type=float,default=None)
    p.add_argument("--min-expected-regret",type=float,default=None)
    p.add_argument("--frozen-protocol",type=Path,default=None)
    p.add_argument("--sweep-development-grid",action="store_true")
    args=p.parse_args()

    config_path=ROOT/args.config
    config=yaml.safe_load(config_path.read_text(encoding="utf-8"));phase=args.phase
    if phase=="confirmatory" and any(
        x is not None for x in (
            args.decision_threshold,args.information_weight,args.probe_weight,args.min_expected_regret
        )
    ):
        raise SystemExit("confirmatory hyperparameters must come only from --frozen-protocol")
    if args.sweep_development_grid and phase!="development":
        raise SystemExit("--sweep-development-grid is valid only for development")

    seed_values=_seed_values(config,phase,args.seed_start,args.seeds)
    out=ROOT/(args.output_dir or Path(config["artifact_root"])/phase)
    frozen=None
    if args.sweep_development_grid:
        grid=config["development"]["hyperparameter_grid"];episodes_all=[];steps_all=[]
        setting_records=[];settings=None
        for idx,values in enumerate(itertools.product(
            grid["decision_threshold"],grid["information_weight"],grid["probe_weight"]
        )):
            hyper={
                "decision_threshold":float(values[0]),"information_weight":float(values[1]),
                "probe_weight":float(values[2]),
                "min_expected_regret":float(config["development"]["default_hyperparameters"].get("min_expected_regret",0.0)),
            }
            setting_id=f"dev_{idx:03d}"
            settings,episodes,step_rows=_one_run(config,args,phase,hyper,seed_values,setting_id)
            episodes_all.append(episodes);steps_all.append(step_rows)
            setting_records.append({"setting_id":setting_id,**hyper})
        episodes=pd.concat(episodes_all,ignore_index=True);steps=pd.concat(steps_all,ignore_index=True)
        out.mkdir(parents=True,exist_ok=True)
        pd.DataFrame(setting_records).to_csv(out/"development_settings.csv",index=False)
        selected_hyper=None
    else:
        hyper,frozen=_hyperparameters(config,phase,args)
        settings,episodes,steps=_one_run(config,args,phase,hyper,seed_values)
        selected_hyper=hyper

    evidence_role={
        "smoke":"engineering_smoke_not_scientific_evidence",
        "development":"development_only_not_confirmatory_evidence",
        "confirmatory":"frozen_confirmatory_candidate_evidence",
    }[phase]
    if phase!="smoke" and (args.seed_start is not None or args.seeds is not None):
        evidence_role="subset_or_exploratory_run_not_full_declared_evidence"

    manifest={
        "schema_version":1,"protocol_version":config["protocol_version"],"phase":phase,
        "evidence_role":evidence_role,"created_utc":datetime.now(timezone.utc).isoformat(),
        "git_commit_sha":_git_sha(),"config_path":str(args.config),
        "config_sha256":_sha256(config_path),"seed_values":seed_values,
        "seed_count":len(seed_values),
        "scenario_steps":int(args.scenario_steps or config["simulation"]["scenario_steps"]),
        "settings":asdict(settings),"selected_hyperparameters":selected_hyper,
        "development_grid_sweep":bool(args.sweep_development_grid),"frozen_protocol":frozen,
        "latent_parameter_generation_policy":"declared modeled truth per A-F scenario; never exposed to C0-C3",
        "planner_oracle_boundary":"C4 receives latent link parameters only; all planners use the same causal target prediction and hard safety filters",
        "link_provenance":ParameterizedPCFMCWLinkModel().provenance(),
        "software":{"python":platform.python_version(),"platform":platform.platform(),
                    "numpy":np.__version__,"pandas":pd.__version__},
        "claim_boundary":config["claim_boundary"],
    }
    _write_outputs(out,episodes,steps,manifest)


if __name__=="__main__":
    main()
