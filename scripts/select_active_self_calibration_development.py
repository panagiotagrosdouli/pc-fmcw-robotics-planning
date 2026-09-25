#!/usr/bin/env python3
"""Aggregate development shards and select one frozen active-calibration setting.

The workflow may compute C0/C1/C4 once as a common deterministic baseline and
C2/C3 separately for each of the 27 declared hyperparameter settings. This
script reconstructs the exact 5-planner paired table for every setting before
selection. It also accepts the earlier monolithic 5-planner shard layout.

Selection is deterministic and predeclared:
1. zero collision episodes, zero static-clearance-violation episodes and zero
   episodes with any no-candidate step across all C0--C4 development runs;
2. minimize C3 mean cumulative decision regret;
3. tie-break by C3 mean cumulative probe cost;
4. then C3 mean probe fraction;
5. then setting_id.

Scenario E/F diagnostics are reported but never used for tuning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

HYPER_KEYS=("decision_threshold","information_weight","probe_weight","min_expected_regret")
BASELINE_PLANNERS={"C0","C1","C4"}
ADAPTIVE_PLANNERS={"C2","C3"}
FULL_PLANNERS={"C0","C1","C2","C3","C4"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_label(path: Path) -> str:
    for parent in path.parents:
        if parent.name.startswith("asc-dev-"):
            return parent.name[len("asc-dev-"):]
    return path.parent.name


def _discover(root: Path):
    shards=[]
    for episodes_path in sorted(root.rglob("episodes.csv")):
        manifest_path=episodes_path.parent/"manifest.json"
        if not manifest_path.exists():
            continue
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        shards.append({
            "label":_artifact_label(episodes_path),
            "episodes_path":episodes_path,
            "steps_path":episodes_path.parent/"steps.csv",
            "manifest_path":manifest_path,
            "manifest":manifest,
        })
    return shards


def _hyper(manifest):
    h=manifest.get("selected_hyperparameters") or {}
    missing=[k for k in HYPER_KEYS if k not in h]
    if missing:
        raise SystemExit(f"development manifest missing hyperparameters: {missing}")
    return {k:float(h[k]) for k in HYPER_KEYS}


def _setting_id(h):
    return (
        f"dev_t{round(100*h['decision_threshold']):03d}"
        f"_i{round(100*h['information_weight']):03d}"
        f"_p{round(100*h['probe_weight']):03d}"
    )


def _stamp(df,setting_id,h):
    out=df.copy()
    if "setting_id" in out.columns:
        out=out.drop(columns=["setting_id"])
    out.insert(0,"setting_id",setting_id)
    for k,v in h.items():
        out[k]=float(v)
    return out


def _validate_common(shard,expected_hash,expected_seeds):
    m=shard["manifest"]
    label=shard["label"]
    if m.get("phase")!="development":
        raise SystemExit(f"{label}: not a development manifest")
    if m.get("config_sha256")!=expected_hash:
        raise SystemExit(f"{label}: config digest mismatch")
    if list(m.get("seed_values",[]))!=expected_seeds:
        raise SystemExit(f"{label}: development seed set is incomplete or reordered")
    if not shard["steps_path"].exists():
        raise SystemExit(f"{label}: missing steps.csv")
    d=pd.read_csv(shard["episodes_path"])
    if d.duplicated(["planner","scenario","seed"]).any():
        raise SystemExit(f"{label}: duplicate planner/scenario/seed rows")
    return d


def _reconstruct(config,shards,expected_hash,expected_seeds):
    n_unit=len(expected_seeds)*len(config["scenarios"])
    manifest_hashes={}
    full=[]
    baseline=[]
    adaptive=[]

    for shard in shards:
        d=_validate_common(shard,expected_hash,expected_seeds)
        planners=set(d.planner.astype(str).unique())
        shard["episodes"]=d
        shard["planners"]=planners
        shard["hyper"]=_hyper(shard["manifest"])
        manifest_hashes[shard["label"]]=sha256(shard["manifest_path"])
        if planners==FULL_PLANNERS:
            if len(d)!=n_unit*5:
                raise SystemExit(f"{shard['label']}: full shard has {len(d)} rows, expected {n_unit*5}")
            full.append(shard)
        elif planners==BASELINE_PLANNERS:
            if len(d)!=n_unit*3:
                raise SystemExit(f"{shard['label']}: baseline shard has {len(d)} rows, expected {n_unit*3}")
            baseline.append(shard)
        elif planners==ADAPTIVE_PLANNERS:
            if len(d)!=n_unit*2:
                raise SystemExit(f"{shard['label']}: C2/C3 shard has {len(d)} rows, expected {n_unit*2}")
            adaptive.append(shard)
        else:
            raise SystemExit(f"{shard['label']}: unsupported planner subset {sorted(planners)}")

    # Backward-compatible monolithic layout.
    if full:
        if baseline or adaptive:
            raise SystemExit("mixed monolithic and planner-subset development layouts are not allowed")
        episode_sets=[];settings=[];step_sources={}
        for shard in full:
            h=shard["hyper"];sid=shard["label"]
            if not sid.startswith("dev_"):
                sid=_setting_id(h)
            episode_sets.append(_stamp(shard["episodes"],sid,h))
            settings.append({"setting_id":sid,**h})
            step_sources[sid]=[shard]
        table=pd.DataFrame(settings).drop_duplicates("setting_id")
        if len(table)!=27:
            raise SystemExit(f"expected 27 monolithic settings, found {len(table)}")
        return pd.concat(episode_sets,ignore_index=True),table,step_sources,manifest_hashes,"monolithic"

    # Optimized exact reconstruction: one common C0/C1/C4 baseline + 27 C2/C3 settings.
    if len(baseline)!=1:
        raise SystemExit(f"expected exactly one C0/C1/C4 baseline shard, found {len(baseline)}")
    if len(adaptive)!=27:
        raise SystemExit(f"expected exactly 27 C2/C3 setting shards, found {len(adaptive)}")

    b=baseline[0]
    episode_sets=[];settings=[];step_sources={}
    seen=set()
    for shard in adaptive:
        h=shard["hyper"];sid=_setting_id(h)
        if sid in seen:
            raise SystemExit(f"duplicate adaptive setting {sid}")
        seen.add(sid)
        combined=pd.concat([
            _stamp(b["episodes"],sid,h),
            _stamp(shard["episodes"],sid,h),
        ],ignore_index=True)
        if len(combined)!=n_unit*5 or set(combined.planner)!=FULL_PLANNERS:
            raise SystemExit(f"{sid}: reconstructed table is not a complete C0-C4 paired setting")
        if combined.duplicated(["planner","scenario","seed"]).any():
            raise SystemExit(f"{sid}: duplicate planner/scenario/seed after reconstruction")
        episode_sets.append(combined)
        settings.append({"setting_id":sid,**h})
        step_sources[sid]=[b,shard]

    table=pd.DataFrame(settings).sort_values("setting_id",kind="stable").reset_index(drop=True)
    return pd.concat(episode_sets,ignore_index=True),table,step_sources,manifest_hashes,"planner_subset_reconstructed"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,required=True)
    ap.add_argument("--config",type=Path,default=Path("configs/experiments/active_self_calibration.yaml"))
    ap.add_argument("--output-dir",type=Path,default=Path("artifacts/active_self_calibration/development"))
    args=ap.parse_args()

    config_path=args.config
    config=yaml.safe_load(config_path.read_text(encoding="utf-8"))
    lo,hi=map(int,config["development"]["seed_range"])
    expected_seeds=list(range(lo,hi+1))
    expected_hash=sha256(config_path)
    shards=_discover(args.root)
    if not shards:
        raise SystemExit(f"no development shards found under {args.root}")

    episodes,setting_table,step_sources,manifest_hashes,layout=_reconstruct(
        config,shards,expected_hash,expected_seeds
    )
    if len(setting_table)!=27:
        raise SystemExit(f"expected 27 declared development settings, found {len(setting_table)}")

    expected_per_setting=len(expected_seeds)*len(config["scenarios"])*len(config["planners"])
    counts=episodes.groupby("setting_id").size()
    if not (counts==expected_per_setting).all():
        raise SystemExit(f"reconstructed setting row counts are invalid: {counts.to_dict()}")

    rows=[]
    for setting_id,g in episodes.groupby("setting_id",sort=True):
        c3=g[g.planner=="C3"]
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
        raise SystemExit(
            "NO DEVELOPMENT SETTING PASSED THE PREDECLARED SAFETY GATE; "
            "CONFIRMATORY SEEDS MUST REMAIN UNOPENED"
        )
    selected=eligible.sort_values(
        ["c3_mean_regret","c3_mean_probe_cost","c3_mean_probe_fraction","setting_id"],
        kind="stable",
    ).iloc[0]
    setting_id=str(selected.setting_id)
    selected_h={k:float(selected[k]) for k in HYPER_KEYS}

    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    episodes.to_csv(out/"episodes.csv",index=False)
    episodes[episodes.setting_id==setting_id].to_csv(out/"selected_episodes.csv",index=False)

    selected_step_parts=[]
    for shard in step_sources[setting_id]:
        s=pd.read_csv(shard["steps_path"])
        selected_step_parts.append(_stamp(s,setting_id,selected_h))
    selected_steps=pd.concat(selected_step_parts,ignore_index=True)
    if set(selected_steps.planner)!=FULL_PLANNERS:
        raise SystemExit(f"{setting_id}: selected steps do not contain complete C0-C4 family")
    selected_steps.to_csv(out/"selected_steps.csv",index=False)

    setting_table.to_csv(out/"development_settings.csv",index=False)
    diagnostics.to_csv(out/"selection_diagnostics.csv",index=False)
    selection={
        "protocol_version":config["protocol_version"],
        "development_layout":layout,
        "selection_rule":"safety gate, then lexicographic C3 mean regret, probe cost, probe fraction, setting_id",
        "selected_setting_id":setting_id,
        "selected_hyperparameters":selected_h,
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
        "development_layout":layout,
        "config_path":str(args.config),"config_sha256":expected_hash,
        "seed_values":expected_seeds,"seed_count":len(expected_seeds),
        "n_settings":len(setting_table),"selected_setting_id":setting_id,
        "selection_rule":selection["selection_rule"],"shard_manifest_sha256":manifest_hashes,
        "paired_reconstruction":"C0/C1/C4 baseline rows are deterministic common controls and are copied into each hyperparameter setting before safety gating and selection",
    }
    (out/"manifest.json").write_text(json.dumps(aggregate_manifest,indent=2),encoding="utf-8")
    print(json.dumps(selection,indent=2))


if __name__=="__main__":
    main()
