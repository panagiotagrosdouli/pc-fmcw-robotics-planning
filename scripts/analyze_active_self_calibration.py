#!/usr/bin/env python3
"""Seed-level paired analysis for the active self-calibration study."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from iscai.evaluation.statistics import holm_adjust,paired_bootstrap_delta,paired_effect_sizes,paired_wilcoxon

METRICS=(
    "cumulative_decision_regret","oracle_parameter_agreement_fraction",
    "probe_fraction","cumulative_probe_cost","final_parameter_error_normalized",
    "progress_m","mean_outage_probability",
)

def _seed_pair(df,a,b,metric):
    left=df[df.planner==a].groupby("seed",sort=True)[metric].mean().rename("a")
    right=df[df.planner==b].groupby("seed",sort=True)[metric].mean().rename("b")
    pair=pd.concat([left,right],axis=1,join="inner").dropna()
    if pair.empty: raise ValueError(f"no finite seed pairs for {a} vs {b}: {metric}")
    return pair

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True)
    p.add_argument("--config",type=Path,default=Path("configs/experiments/active_self_calibration.yaml"))
    p.add_argument("--output-dir",type=Path,default=None);p.add_argument("--setting-id",default=None)
    p.add_argument("--bootstrap-samples",type=int,default=10000);p.add_argument("--bootstrap-seed",type=int,default=2026)
    args=p.parse_args()
    if args.bootstrap_samples<1: raise SystemExit("--bootstrap-samples must be >= 1")
    inp=ROOT/args.input;df=pd.read_csv(inp)
    if args.setting_id is not None:
        if "setting_id" not in df.columns: raise SystemExit("--setting-id requires setting_id")
        df=df[df.setting_id==args.setting_id].copy()
        if df.empty: raise SystemExit(f"no rows for setting_id={args.setting_id}")
    required={"planner","scenario","seed",*METRICS};missing=required-set(df.columns)
    if missing: raise SystemExit(f"input missing columns: {sorted(missing)}")
    if df.duplicated(["planner","scenario","seed"]).any():
        raise SystemExit("duplicate planner/scenario/seed rows; filter a development setting first")
    config=yaml.safe_load((ROOT/args.config).read_text(encoding="utf-8"))
    comparisons=[tuple(x) for x in config["confirmatory"]["primary_comparisons"]]
    rows=[];delta_rows=[]
    for ci,(a,b) in enumerate(comparisons):
        family=[]
        for mi,metric in enumerate(METRICS):
            pair=_seed_pair(df,a,b,metric);av=pair.a.to_numpy(float);bv=pair.b.to_numpy(float)
            boot=paired_bootstrap_delta(av,bv,samples=args.bootstrap_samples,rng=args.bootstrap_seed+100*ci+mi)
            wil=paired_wilcoxon(av,bv);effects=paired_effect_sizes(av,bv)
            row={"planner_a":a,"planner_b":b,"comparison":f"{b}-{a}","metric":metric,
                 "n_independent_seeds":int(len(pair)),"mean_seed_delta_b_minus_a":boot["mean_delta"],
                 "ci95_low":boot["ci_low"],"ci95_high":boot["ci_high"],
                 "wilcoxon_p":wil["pvalue"],**effects}
            family.append(row)
            for seed,v in pair.iterrows():
                delta_rows.append({"planner_a":a,"planner_b":b,"comparison":f"{b}-{a}",
                                   "metric":metric,"seed":int(seed),"a":float(v.a),"b":float(v.b),
                                   "delta_b_minus_a":float(v.b-v.a)})
        adjusted=holm_adjust(np.asarray([r["wilcoxon_p"] for r in family],float))
        for row,padj in zip(family,adjusted):
            row["holm_p_within_comparison_family"]=float(padj);rows.append(row)
    out=ROOT/(args.output_dir or inp.parent);out.mkdir(parents=True,exist_ok=True)
    effects=pd.DataFrame(rows);effects.to_csv(out/"paired_effects.csv",index=False)
    pd.DataFrame(delta_rows).to_csv(out/"seed_level_deltas.csv",index=False)
    summary=df.groupby(["scenario","planner"],as_index=False).agg(
        episodes=("seed","size"),regret=("cumulative_decision_regret","mean"),
        probe_fraction=("probe_fraction","mean"),parameter_error=("final_parameter_error_normalized","mean"),
        progress_m=("progress_m","mean"),outage=("mean_outage_probability","mean"),
        collision_rate=("collision_indicator","mean"),no_candidate_steps=("no_candidate_steps","mean"),
    )
    summary.to_csv(out/"scenario_summary.csv",index=False);print(effects.to_string(index=False))

if __name__=="__main__": main()
