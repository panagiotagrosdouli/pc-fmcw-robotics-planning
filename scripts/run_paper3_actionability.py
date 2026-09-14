#!/usr/bin/env python3
"""Paper 3 route-constrained communication-forecast actionability replay.

The runner preserves measured-support counterfactual validity: candidates are
future states actually traversed on the held-out route. Realized future delay is
outcome-only and is never passed to the decision selector.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from iscai.connectivity.real_v2x.datasets import add_run_metadata, blocked_run_split, discover_cicv5g_files, load_cicv5g_file
from iscai.connectivity.real_v2x.predictors import ConditionedSpatialKNNPredictor
from iscai.connectivity.real_v2x.support import SpatialSupportModel
from iscai.connectivity.real_v2x.uncertainty import ResidualConformalCalibrator
from iscai.evaluation.actionability import select_actionable_candidate, decision_regret, changed_action_outcome

CONTEXT=("network","direction","nominal_speed_kmh")

def pairs(df,h):
    rows=[]
    for _,g in df.groupby("run_id",sort=False):
        g=g.sort_values("pub_time_ms").reset_index(drop=True)
        if len(g)<=h: continue
        fut=g.iloc[h:].copy().reset_index(drop=True); cur=g.iloc[:-h].reset_index(drop=True)
        fut["current_delay_ms"]=cur.delay_ms.to_numpy(float); rows.append(fut)
    return pd.concat(rows,ignore_index=True) if rows else pd.DataFrame()

def key_tuple(key):
    if not isinstance(key,tuple): key=(key,)
    return tuple(None if pd.isna(v) else v for v in key)

def fit_horizon(cal,model,h,alpha):
    ca=pairs(cal,h); spatial=model.predict(ca); work=ca[list(CONTEXT)].copy()
    work["y"]=ca.delay_ms.to_numpy(float); work["p"]=ca.current_delay_ms.to_numpy(float); work["m"]=spatial
    weights={}
    grid=np.linspace(0,1,41)
    for key,g in work.groupby(list(CONTEXT),dropna=False):
        if len(g)<100: weights[key_tuple(key)]=1.0; continue
        losses=[np.mean(np.abs(g.y-(w*g.p+(1-w)*g.m))) for w in grid]
        weights[key_tuple(key)]=float(grid[int(np.argmin(losses))])
    pred=np.empty(len(ca),float)
    for i,row in ca.iterrows():
        w=weights.get(tuple(row[c] for c in CONTEXT),1.0); pred[i]=w*row.current_delay_ms+(1-w)*spatial[i]
    conf=ResidualConformalCalibrator(alpha).fit(ca.delay_ms.to_numpy(float),pred)
    return weights,conf

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",default="data/raw/cicv5g"); ap.add_argument("--output",default="results/paper3_actionability")
    ap.add_argument("--seed",type=int,default=0); ap.add_argument("--nominal-horizon",type=int,default=20); ap.add_argument("--offset-factors",default="0.5,1.0,1.5")
    ap.add_argument("--alpha",type=float,default=.1); ap.add_argument("--support-radius-m",type=float,default=1.0); ap.add_argument("--support-min-neighbors",type=int,default=5)
    ap.add_argument("--mobility-scale-ms",type=float,default=1.0); ap.add_argument("--min-net-gain-ms",type=float,default=0.0); ap.add_argument("--delay-threshold-ms",type=float,default=50.0)
    args=ap.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    files=discover_cicv5g_files(args.data); df=pd.concat([add_run_metadata(load_cicv5g_file(p),p) for p in files],ignore_index=True)
    train,cal,test,split=blocked_run_split(df,seed=args.seed)
    spatial=ConditionedSpatialKNNPredictor("delay_ms",20,min_group_samples=100).fit(train)
    support=SpatialSupportModel(radius_m=args.support_radius_m,min_neighbors=args.support_min_neighbors).fit(train)
    nominal=args.nominal_horizon; offsets=sorted(set(max(1,int(round(nominal*float(f)))) for f in args.offset_factors.split(",")))
    fitted={h:fit_horizon(cal,spatial,h,args.alpha) for h in offsets}; rows=[]
    for run_id,g0 in test.groupby("run_id",sort=False):
        g=g0.sort_values("pub_time_ms").reset_index(drop=True)
        for t in range(len(g)-max(offsets)):
            current=g.iloc[t]; lows=[]; highs=[]; means=[]; supported=[]; mobility=[]; truth=[]
            for h in offsets:
                future=g.iloc[t+h:t+h+1].copy(); mp=float(spatial.predict(future)[0]); weights,conf=fitted[h]
                w=float(weights.get(tuple(future.iloc[0][c] for c in CONTEXT),1.0)); pred=w*float(current.delay_ms)+(1-w)*mp
                lo,hi=conf.interval(np.asarray([pred])); sup=support.evaluate(future)
                lows.append(float(lo[0])); highs.append(float(hi[0])); means.append(pred); supported.append(bool(sup["supported"][0])); mobility.append(abs(h-nominal)/max(nominal,1)); truth.append(float(future.delay_ms.iloc[0]))
            ref=offsets.index(nominal); a0=ref; a1=int(np.argmin(np.asarray(means)+args.mobility_scale_ms*np.asarray(mobility)))
            choice=select_actionable_candidate(lows,highs,supported,args.mobility_scale_ms*np.asarray(mobility),reference_index=ref,min_net_gain=args.min_net_gain_ms); a2=choice.index
            for mode,idx in (("A0",a0),("A1",a1),("A2",a2)):
                changed=idx!=ref; outcome=changed_action_outcome(truth[ref],truth[idx]) if changed else "reference"
                rows.append({"run_id":run_id,"t_index":t,"mode":mode,"chosen_horizon_steps":offsets[idx],"changed":changed,"measured_delay_ms":truth[idx],"reference_delay_ms":truth[ref],"delay_violation":truth[idx]>args.delay_threshold_ms,"supported":supported[idx],"mobility_deviation":mobility[idx],"decision_regret_ms":decision_regret(truth[idx],truth),"changed_outcome":outcome})
    d=pd.DataFrame(rows); d.to_csv(out/"decisions.csv",index=False)
    r=d.groupby(["run_id","mode"]).agg(mean_delay_ms=("measured_delay_ms","mean"),violation_fraction=("delay_violation","mean"),changed_fraction=("changed","mean"),unsupported_fraction=("supported",lambda x:float(np.mean(~x.astype(bool)))),mean_regret_ms=("decision_regret_ms","mean"),mobility_deviation=("mobility_deviation","mean")).reset_index(); r.to_csv(out/"run_metrics.csv",index=False)
    r.groupby("mode").mean(numeric_only=True).reset_index().to_csv(out/"summary.csv",index=False)
    meta={"seed":args.seed,"offsets":offsets,"nominal_horizon":nominal,"alpha":args.alpha,"support_radius_m":args.support_radius_m,"support_min_neighbors":args.support_min_neighbors,"mobility_scale_ms":args.mobility_scale_ms,"min_net_gain_ms":args.min_net_gain_ms,"split":split,"claim_boundary":"offline route-constrained measured-support replay; realized future QoS is outcome-only"}; (out/"metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    print(r.groupby("mode").mean(numeric_only=True).to_string())
if __name__=="__main__": main()
