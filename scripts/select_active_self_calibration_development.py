#!/usr/bin/env python3
"""Aggregate development shards and select one frozen active-calibration setting.

Selection is intentionally deterministic and lexicographic:
1. require zero collision episodes, zero episodes with static-clearance violations,
   and zero episodes with any no-candidate step across all C0--C4 development runs;
2. minimize C3 mean cumulative decision regret;
3. tie-break by C3 mean cumulative probe cost;
4. then C3 mean probe fraction;
5. then setting_id.

Mechanism diagnostics for scenarios E/F are reported but are not used for selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _discover(root: Path):
    shards=[]
    for episodes_path in sorted(root.rglob("episodes.csv")):
        parent=episodes_path.parent
        manifest_path=parent/"manifest.json"
        if not manifest_path.exists():
            continue
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        setting_id=parent.name
        if setting_id.startswith("asc-dev-"):
            setting_id=setting_id[len("asc-dev-"):]
        if not setting_id.startswith("dev_"):
            # actions/download-artifact often creates asc-dev-dev_000/episodes.csv
            anc=next((p.name for p in episodes_path.parents if p.name.startswith("asc-dev-dev_")),None)
            if anc: setting_id=anc[len("asc-dev-"):]
        shards.append((setting_id,episodes_path,manifest_path,manifest))
    return shards


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,required=True)
    ap.add_argument("--config",type=Path,default=Path("configs/experiments/active_self_calibration.yaml"))
    ap.add_argument("--output-dir",type=Path,default=Path("artifacts/active_self_calibration/development"))
    args=ap.parse_args()

    config_path=args.config
    config=yaml.safe_load(config_path.read_text(encoding="utf-8"))
    expected_seeds=list(range(int(config["development"]["seed_range"][0]),int(config["development"]["seed_range"][1])+1))
    expected_hash=sha256(config_path)
    shards=_discover(args.root)
    if not shards:
        raise SystemExit(f"no development shards found under {args.root}")

    episodes_all=[];settings=[];manifest_hashes={};shard_dirs={}
    for setting_id,episodes_path,manifest_path,manifest in shards:
        if manifest.get("phase")!="development":
            raise SystemExit(f"{setting_id}: not a development manifest")
        if manifest.get("config_sha256")!=expected_hash:
            raise SystemExit(f"{setting_id}: config digest mismatch")
        if list(manifest.get("seed_values",[]))!=expected_seeds:
            raise SystemExit(f"{setting_id}: development seed set is incomplete or reordered")
        d=pd.read_csv(episodes_path);shard_dirs[setting_id]=episodes_path.parent
        if d.duplicated(["planner","scenario","seed"]).any():
            raise SystemExit(f"{setting_id}: duplicate planner/scenario/seed rows")
        expected_rows=len(expected_seeds)*len(config["scenarios"])*len(config["planners"])
        if len(d)!=expected_rows:
            raise SystemExit(f"{setting_id}: expected {expected_rows} episode rows, got {len(d)}")
        d.insert(0,"setting_id",setting_id);episodes_all.append(d)
        hyper=manifest.get("selected_hyperparameters") or {}
        settings.append({"setting_id":setting_id,**{k:float(hyper[k]) for k in (
            "decision_threshold","information_weight","probe_weight","min_expected_regret"
        )}})
        manifest_hashes[setting_id]=sha256(manifest_path)

    episodes=pd.concat(episodes_all,ignore_index=True)
    setting_table=pd.DataFrame(settings).drop_duplicates("setting_id").sort_values("setting_id")
    if len(setting_table)!=27:
        raise SystemExit(f"expected 27 declared development settings, found {len(setting_table)}")

    rows=[]
    for setting_id,g in episodes.groupby("setting_id",sort=True):
        c3=g[g.planner=="C3"]
        if c3.empty: raise SystemExit(f"{setting_id}: missing C3")
        e=c3[c3.scenario=="E_decision_irrelevant_uncertainty"]
        f=c3[c3.scenario=="F_decision_critical_uncertainty"]
        row={
            "setting_id":setting_id,
            "collision_episodes":int((g.collision_indicator.astype(int)>0).sum()),
            "no_candidate_episodes":int((g.no_candidate_steps.astype(int)>0).sum()),
            "static_violation_episodes":int((g.static_clearance_violation_steps.astype(int)>0).sum()),
            "c3_mean_regret":float(c3.cumulative_decision_regret.mean()),
            "c3_median_regret":float(c3.cumulative_decision_regret.median()),
            "c3_mean_probe_cost":float(c3.cumulative_probe_cost.mean()),
            "c3_mean_probe_fraction":float(c3.probe_fraction.mean()),
            "c3_mean_parameter_error":float(c3.final_parameter_error_normalized.mean()),
            "c3_E_probe_fraction":float(e.probe_fraction.mean()) if len(e) else float("nan"),
            "c3_E_regret":float(e.cumulative_decision_regret.mean()) if len(e) else float("nan"),
            "c3_F_probe_fraction":float(f.probe_fraction.mean()) if len(f) else float("nan"),
            "c3_F_regret":float(f.cumulative_decision_regret.mean()) if len(f) else float("nan"),
        }
        row["safety_eligible"]=(
            row["collision_episodes"]==0
            and row["no_candidate_episodes"]==0
            and row["static_violation_episodes"]==0
        )
        rows.append(row)

    diagnostics=pd.DataFrame(rows).merge(setting_table,on="setting_id",how="left",validate="one_to_one")
    eligible=diagnostics[diagnostics.safety_eligible].copy()
    if eligible.empty:
        raise SystemExit("NO DEVELOPMENT SETTING PASSED THE PREDECLARED SAFETY GATE; CONFIRMATORY SEEDS MUST REMAIN UNOPENED")
    selected=eligible.sort_values(
        ["c3_mean_regret","c3_mean_probe_cost","c3_mean_probe_fraction","setting_id"],
        kind="stable",
    ).iloc[0]
    setting_id=str(selected.setting_id)

    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    episodes.to_csv(out/"episodes.csv",index=False)
    episodes[episodes.setting_id==setting_id].to_csv(out/"selected_episodes.csv",index=False)
    selected_steps_path=shard_dirs[setting_id]/"steps.csv"
    if not selected_steps_path.exists(): raise SystemExit(f"{setting_id}: missing steps.csv")
    selected_steps=pd.read_csv(selected_steps_path);selected_steps.insert(0,"setting_id",setting_id)
    selected_steps.to_csv(out/"selected_steps.csv",index=False)
    setting_table.to_csv(out/"development_settings.csv",index=False)
    diagnostics.to_csv(out/"selection_diagnostics.csv",index=False)
    selection={
        "protocol_version":config["protocol_version"],
        "selection_rule":"safety gate, then lexicographic C3 mean regret, probe cost, probe fraction, setting_id",
        "selected_setting_id":setting_id,
        "selected_hyperparameters":{
            "decision_threshold":float(selected.decision_threshold),
            "information_weight":float(selected.information_weight),
            "probe_weight":float(selected.probe_weight),
            "min_expected_regret":float(selected.min_expected_regret),
        },
        "selected_diagnostics":{
            k:(bool(selected[k]) if k=="safety_eligible" else float(selected[k]))
            for k in (
                "safety_eligible","c3_mean_regret","c3_mean_probe_cost","c3_mean_probe_fraction",
                "c3_mean_parameter_error","c3_E_probe_fraction","c3_E_regret",
                "c3_F_probe_fraction","c3_F_regret",
            )
        },
        "development_seed_values":expected_seeds,
        "config_sha256":expected_hash,
        "shard_manifest_sha256":manifest_hashes,
    }
    (out/"selection.json").write_text(json.dumps(selection,indent=2),encoding="utf-8")
    aggregate_manifest={
        "schema_version":1,"protocol_version":config["protocol_version"],"phase":"development",
        "evidence_role":"development_only_not_confirmatory_evidence",
        "config_path":str(args.config),"config_sha256":expected_hash,
        "seed_values":expected_seeds,"seed_count":len(expected_seeds),
        "n_settings":len(setting_table),"selected_setting_id":setting_id,
        "selection_rule":selection["selection_rule"],"shard_manifest_sha256":manifest_hashes,
    }
    (out/"manifest.json").write_text(json.dumps(aggregate_manifest,indent=2),encoding="utf-8")
    print(json.dumps(selection,indent=2))


if __name__=="__main__":
    main()
