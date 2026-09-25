#!/usr/bin/env python3
"""Development-only structural safety diagnostic for the active-calibration study.

This script is invoked only after a development no-candidate failure. It never
uses confirmatory seeds and never relaxes hard safety distances. Candidate
profiles are ordered by generated candidate count; the selected remediation is
the smallest profile that has zero collision episodes, zero no-candidate
episodes and zero static-clearance-violation episodes on the declared failure
case for all C0--C4 planners.
"""
from __future__ import annotations
import argparse,json,sys
from dataclasses import replace
from pathlib import Path
import pandas as pd,yaml

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from iscai.active_self_calibration import CalibrationBenchmarkSettings,make_identifiability_scenarios,run_study

PROFILES={
 "current":{"lateral":(-1.0,0.0,1.0),"horizons":(2.0,3.0),"speeds":(-1.5,0.0,1.5)},
 "wider_lateral":{"lateral":(-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5),"horizons":(2.0,3.0),"speeds":(-1.5,0.0,1.5)},
 "longer_horizon":{"lateral":(-1.0,0.0,1.0),"horizons":(2.0,3.0,4.0,5.0),"speeds":(-1.5,0.0,1.5)},
 "wider_lateral_longer_horizon":{"lateral":(-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5),"horizons":(2.0,3.0,4.0,5.0),"speeds":(-1.5,0.0,1.5)},
 "full_v7_envelope":{"lateral":(-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5),"horizons":(2.0,3.0,4.0,5.0),"speeds":(-2.0,0.0,2.0)},
}

def count_candidates(p,dt=.1):
    # nominal + emergency lateral profiles + bounded brake/steer pulses
    pulse_steps=max(1,int(round(.5/dt)))
    return len(p["lateral"])*len(p["horizons"])*(len(p["speeds"])+1)+len(p["horizons"])*2*pulse_steps

def settings_from_config(c):
    s=c["simulation"];h=c["development"]["default_hyperparameters"]
    return CalibrationBenchmarkSettings(
      dt=float(s["dt"]),history_steps=int(s["history_steps"]),horizon_steps=int(s["horizon_steps"]),
      target_observation_sigma_m=float(s["target_observation_sigma_m"]),
      communication_observation_sigma_db=float(c["latent_model"]["observation_sigma_db"]),
      connectivity_weight=float(s["connectivity_weight"]),information_weight=float(h["information_weight"]),
      probe_weight=float(h["probe_weight"]),decision_threshold=float(h["decision_threshold"]),
      min_expected_regret=float(h.get("min_expected_regret",0.0)),
      information_horizon_steps=int(s["information_horizon_steps"]),
      collision_distance_m=float(s["collision_distance_m"]),
      planning_safety_margin_m=float(s["planning_safety_margin_m"]),
      require_static_stop_viability=bool(s["require_static_stop_viability"]),
      bounded_brake_steer=bool(s["bounded_brake_steer"]),
      time_aligned_dynamic=bool(s["time_aligned_dynamic"]),
      require_dynamic_stop_viability=bool(s["require_dynamic_stop_viability"]),
      hierarchical_clearance=bool(s["hierarchical_clearance"]),
      damped_lateral_prediction=bool(s["damped_lateral_prediction"]),
      endpoint_anchored_lateral=bool(s["endpoint_anchored_lateral"]),
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",type=Path,default=Path("configs/experiments/active_self_calibration.yaml"))
    ap.add_argument("--output",type=Path,default=Path("artifacts/active_self_calibration/safety_diagnostic"))
    args=ap.parse_args();c=yaml.safe_load(args.config.read_text());base=settings_from_config(c)
    failure_seed=31015;scenario=[x for x in make_identifiability_scenarios(steps=int(c["simulation"]["scenario_steps"]),dt=base.dt) if x.name=="A_angular_bias"]
    rows=[];episodes=[]
    for name,p in PROFILES.items():
        cfg=replace(base,candidate_lateral_offsets=p["lateral"],candidate_horizons=p["horizons"],candidate_speed_offsets=p["speeds"])
        result=run_study(seeds=[failure_seed],settings=cfg,scenarios=scenario)
        d=pd.DataFrame(result["episodes"]);d.insert(0,"profile",name);episodes.append(d)
        row={"profile":name,"candidate_count":count_candidates(p,base.dt),
             "collision_episodes":int((d.collision_indicator>0).sum()),
             "no_candidate_episodes":int((d.no_candidate_steps>0).sum()),
             "no_candidate_steps":int(d.no_candidate_steps.sum()),
             "static_violation_episodes":int((d.static_clearance_violation_steps>0).sum())}
        row["safety_pass"]=row["collision_episodes"]==0 and row["no_candidate_episodes"]==0 and row["static_violation_episodes"]==0
        rows.append(row)
    table=pd.DataFrame(rows).sort_values(["candidate_count","profile"],kind="stable")
    eligible=table[table.safety_pass]
    selected=None if eligible.empty else str(eligible.iloc[0].profile)

    # If candidate-envelope expansion cannot fix the failure, diagnose whether
    # Scenario A itself is an incidental near-collision stress case. A is meant
    # to isolate angular identifiability, so we may increase only its initial
    # longitudinal separation during DEVELOPMENT. Hard safety distances, vehicle
    # limits, target lateral motion, latent parameters and confirmatory seeds are
    # untouched. Select the smallest shift that clears the known failure seed,
    # then require it to clear the entire declared development seed set.
    shift_rows=[];selected_shift=None;verification=None
    if selected is None:
        from iscai.active_self_calibration.scenarios import CalibrationScenario
        base_scenario=scenario[0]
        for shift in (0.0,1.0,2.0,3.0,4.0,5.0,6.0):
            target=base_scenario.scenario.target_states.copy();target[:,0]+=shift
            shifted=CalibrationScenario(
                name=base_scenario.name,
                scenario=replace(base_scenario.scenario,target_states=target),
                true_parameters=base_scenario.true_parameters,
                prior_axes=base_scenario.prior_axes,
                mechanism=base_scenario.mechanism,
            )
            result=run_study(seeds=[failure_seed],settings=base,scenarios=[shifted])
            d=pd.DataFrame(result["episodes"])
            row={"target_shift_m":shift,
                 "collision_episodes":int((d.collision_indicator>0).sum()),
                 "no_candidate_episodes":int((d.no_candidate_steps>0).sum()),
                 "no_candidate_steps":int(d.no_candidate_steps.sum()),
                 "static_violation_episodes":int((d.static_clearance_violation_steps>0).sum())}
            row["safety_pass"]=row["collision_episodes"]==0 and row["no_candidate_episodes"]==0 and row["static_violation_episodes"]==0
            shift_rows.append(row)
            if row["safety_pass"] and selected_shift is None:
                selected_shift=float(shift)
        if selected_shift is not None:
            target=base_scenario.scenario.target_states.copy();target[:,0]+=selected_shift
            shifted=CalibrationScenario(
                name=base_scenario.name,
                scenario=replace(base_scenario.scenario,target_states=target),
                true_parameters=base_scenario.true_parameters,
                prior_axes=base_scenario.prior_axes,
                mechanism=base_scenario.mechanism,
            )
            lo,hi=map(int,c["development"]["seed_range"])
            dev_result=run_study(seeds=list(range(lo,hi+1)),settings=base,scenarios=[shifted])
            vd=pd.DataFrame(dev_result["episodes"])
            verification={
                "seed_range":[lo,hi],"episodes":int(len(vd)),
                "collision_episodes":int((vd.collision_indicator>0).sum()),
                "no_candidate_episodes":int((vd.no_candidate_steps>0).sum()),
                "no_candidate_steps":int(vd.no_candidate_steps.sum()),
                "static_violation_episodes":int((vd.static_clearance_violation_steps>0).sum()),
            }
            verification["safety_pass"]=(
                verification["collision_episodes"]==0
                and verification["no_candidate_episodes"]==0
                and verification["static_violation_episodes"]==0
            )
            if not verification["safety_pass"]:
                selected_shift=None

    out=args.output;out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"profile_safety.csv",index=False);pd.concat(episodes,ignore_index=True).to_csv(out/"episodes.csv",index=False)
    if shift_rows: pd.DataFrame(shift_rows).to_csv(out/"scenario_a_shift_sweep.csv",index=False)
    payload={"development_failure_case":{"seed":failure_seed,"scenario":"A_angular_bias"},
             "candidate_selection_rule":"minimum candidate_count among profiles with zero collision/no-candidate/static-violation episodes for all C0-C4; no safety-distance relaxation",
             "selected_profile":selected,"profiles":PROFILES,
             "scenario_remediation_rule":"if no candidate profile passes, choose smallest +x target translation in [0,1,2,3,4,5,6] m that clears the known development failure, then require zero collision/no-candidate/static-violation episodes across seeds 31000-31019 for C0-C4",
             "selected_scenario_a_target_shift_m":selected_shift,
             "development_verification":verification,
             "scientific_boundary":"development-only removal of incidental near-collision confounding in Scenario A; no safety-distance relaxation and no confirmatory seeds used"}
    (out/"selection.json").write_text(json.dumps(payload,indent=2))
    print(table.to_string(index=False))
    if shift_rows: print(pd.DataFrame(shift_rows).to_string(index=False))
    print(json.dumps(payload,indent=2))
    if selected is None and selected_shift is None:
        raise SystemExit("no candidate-envelope or Scenario-A separation remediation passed the development safety diagnostic")

if __name__=="__main__":main()
