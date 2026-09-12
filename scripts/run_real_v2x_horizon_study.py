#!/usr/bin/env python3
"""Causal planning-horizon study using measured CICV5G QoS.

Future candidate positions are assumed known from the motion planner. Future measured
QoS is never used as an input. Fusion weights are selected only on run-disjoint
calibration data and separately for network/direction/speed contexts. Unseen calibration
contexts fall back to persistence rather than trusting an unsupported spatial map.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np, pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from iscai.connectivity.real_v2x.datasets import load_cicv5g_file, add_run_metadata, discover_cicv5g_files, blocked_run_split
from iscai.connectivity.real_v2x.predictors import SpatialKNNPredictor, ConditionedSpatialKNNPredictor
from iscai.connectivity.real_v2x.support import SpatialSupportModel
from iscai.connectivity.real_v2x.uncertainty import ResidualConformalCalibrator, SupportConditionalConformalCalibrator

CONTEXT=("network","direction","nominal_speed_kmh")

def pairs(df,h):
    rows=[]
    for run,g in df.groupby("run_id",sort=False):
        g=g.sort_values("pub_time_ms").reset_index(drop=True)
        if len(g)<=h: continue
        fut=g.iloc[h:].copy().reset_index(drop=True); cur=g.iloc[:-h].reset_index(drop=True)
        fut["current_delay_ms"]=cur.delay_ms.to_numpy(float); fut["current_sinr_db"]=cur.sinr_db.to_numpy(float)
        fut["horizon_ms"]=fut.pub_time_ms.to_numpy(float)-cur.pub_time_ms.to_numpy(float); rows.append(fut)
    return pd.concat(rows,ignore_index=True) if rows else pd.DataFrame()

def err(y,p): return float(mean_absolute_error(y,p)),float(mean_squared_error(y,p)**.5)
def choose_weight(y,persist,map_pred):
    grid=np.linspace(0,1,41); vals=[np.mean(np.abs(y-(w*persist+(1-w)*map_pred))) for w in grid]; return float(grid[int(np.argmin(vals))])
def key_tuple(key):
    if not isinstance(key,tuple): key=(key,)
    return tuple(None if pd.isna(v) else v for v in key)
def calibrate_context_weights(df,target,current_col,map_pred,min_samples=100):
    work=df[list(CONTEXT)].copy(); work["y"]=df[target].to_numpy(float); work["p"]=df[current_col].to_numpy(float); work["m"]=np.asarray(map_pred,float)
    weights={}
    for key,g in work.groupby(list(CONTEXT),dropna=False):
        k=key_tuple(key)
        weights[k]=choose_weight(g.y.to_numpy(),g.p.to_numpy(),g.m.to_numpy()) if len(g)>=min_samples else 1.0
    return weights
def gated_fusion(df,persist,map_pred,weights):
    out=np.asarray(persist,float).copy(); used=np.ones(len(df),float)
    for key,idxs in df.groupby(list(CONTEXT),dropna=False,sort=False).groups.items():
        k=key_tuple(key); w=float(weights.get(k,1.0)); pos=np.asarray([df.index.get_loc(i) for i in idxs],int)
        out[pos]=w*np.asarray(persist)[pos]+(1-w)*np.asarray(map_pred)[pos]; used[pos]=w
    return out,used

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",default="data/raw/cicv5g"); ap.add_argument("--output",default="results/real_v2x_horizon"); ap.add_argument("--horizons",default="1,5,10,20,50,100"); ap.add_argument("--seed",type=int,default=0); ap.add_argument("--alpha",type=float,default=.1)
    a=ap.parse_args(); out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    files=discover_cicv5g_files(a.data); df=pd.concat([add_run_metadata(load_cicv5g_file(p),p) for p in files],ignore_index=True)
    train,cal,test,split=blocked_run_split(df,seed=a.seed); support=SpatialSupportModel(radius_m=15,min_neighbors=5).fit(train)
    global_maps={t:SpatialKNNPredictor(t,20).fit(train) for t in ("delay_ms","sinr_db")}
    cond_maps={t:ConditionedSpatialKNNPredictor(t,20,min_group_samples=100).fit(train) for t in ("delay_ms","sinr_db")}
    summary=[]; runrows=[]
    for h in [int(x) for x in a.horizons.split(",") if x.strip()]:
        ca=pairs(cal,h); te=pairs(test,h)
        if len(ca)<200 or len(te)<200: continue
        for target,current_col in [("delay_ms","current_delay_ms"),("sinr_db","current_sinr_db")]:
            cy=ca[target].to_numpy(float); cp=ca[current_col].to_numpy(float); cglobal=global_maps[target].predict(ca); ccond=cond_maps[target].predict(ca)
            weights=calibrate_context_weights(ca,target,current_col,ccond); cf,cweights=gated_fusion(ca,cp,ccond,weights)
            ty=te[target].to_numpy(float); tp=te[current_col].to_numpy(float); tglobal=global_maps[target].predict(te); tcond=cond_maps[target].predict(te); tf,tweights=gated_fusion(te,tp,tcond,weights)
            pmae,prmse=err(ty,tp); gmae,grmse=err(ty,tglobal); cmae,crmse=err(ty,tcond); fmae,frmse=err(ty,tf)
            rec={"target":target,"horizon_steps":h,"median_horizon_ms":float(np.median(te.horizon_ms)),"mean_fusion_persistence_weight":float(np.mean(tweights)),"fallback_to_persistence_fraction":float(np.mean(tweights==1.0)),"n_calibrated_contexts":len(weights),"persistence_mae":pmae,"global_spatial_mae":gmae,"conditioned_spatial_mae":cmae,"fusion_mae":fmae,"persistence_rmse":prmse,"global_spatial_rmse":grmse,"conditioned_spatial_rmse":crmse,"fusion_rmse":frmse}
            if target=="delay_ms":
                cd=support.evaluate(ca)["nearest_distance_m"]; td=support.evaluate(te)["nearest_distance_m"]
                glob=ResidualConformalCalibrator(a.alpha).fit(cy,cf); glo,ghi=glob.interval(tf)
                adaptive=SupportConditionalConformalCalibrator(a.alpha).fit(cy,cf,cd); alo,ahi=adaptive.interval(tf,td)
                rec.update({"global_coverage":float(np.mean((ty>=glo)&(ty<=ghi))),"adaptive_coverage":float(np.mean((ty>=alo)&(ty<=ahi))),"global_width_ms":float(np.mean(ghi-glo)),"adaptive_width_ms":float(np.mean(ahi-alo)),"adaptive_bin_counts":json.dumps(adaptive.counts_),"adaptive_bin_radii_ms":json.dumps(adaptive.radii_.tolist()),"context_weights":json.dumps({str(k):v for k,v in weights.items()})})
            summary.append(rec)
            temp=te[["run_id"]].copy(); temp["y"]=ty; temp["persist"]=tp; temp["global_map"]=tglobal; temp["cond_map"]=tcond; temp["fusion"]=tf; temp["w"]=tweights
            for run,g in temp.groupby("run_id"):
                runrows.append({"target":target,"horizon_steps":h,"run_id":run,"n":len(g),"persistence_mae":float(np.mean(np.abs(g["y"]-g["persist"]))),"global_spatial_mae":float(np.mean(np.abs(g["y"]-g["global_map"]))),"conditioned_spatial_mae":float(np.mean(np.abs(g["y"]-g["cond_map"]))),"fusion_mae":float(np.mean(np.abs(g["y"]-g["fusion"]))),"mean_fusion_persistence_weight":float(g.w.mean())})
    pd.DataFrame(summary).to_csv(out/"horizon_summary.csv",index=False); pd.DataFrame(runrows).to_csv(out/"horizon_run_metrics.csv",index=False); (out/"split.json").write_text(json.dumps(split,indent=2),encoding="utf-8"); print(pd.DataFrame(summary).to_string(index=False))
if __name__=="__main__": main()
