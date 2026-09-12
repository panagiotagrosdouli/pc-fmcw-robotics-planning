#!/usr/bin/env python3
"""Planning-horizon study: temporal persistence vs spatial map vs causal fusion.

The future candidate position is assumed known from the motion planner; future QoS is
never used as an input. Fusion weights are selected only on the run-disjoint calibration
partition. Test QoS is used only for evaluation.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np, pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from iscai.connectivity.real_v2x.datasets import load_cicv5g_file, add_run_metadata, discover_cicv5g_files, blocked_run_split
from iscai.connectivity.real_v2x.predictors import SpatialKNNPredictor
from iscai.connectivity.real_v2x.support import SpatialSupportModel
from iscai.connectivity.real_v2x.uncertainty import ResidualConformalCalibrator, SupportConditionalConformalCalibrator

def pairs(df,h):
    rows=[]
    for run,g in df.groupby("run_id",sort=False):
        g=g.sort_values("pub_time_ms").reset_index(drop=True)
        if len(g)<=h: continue
        fut=g.iloc[h:].copy().reset_index(drop=True); cur=g.iloc[:-h].reset_index(drop=True)
        fut["current_delay_ms"]=cur.delay_ms.to_numpy(float); fut["current_sinr_db"]=cur.sinr_db.to_numpy(float)
        fut["horizon_ms"]=fut.pub_time_ms.to_numpy(float)-cur.pub_time_ms.to_numpy(float)
        rows.append(fut)
    return pd.concat(rows,ignore_index=True) if rows else pd.DataFrame()

def err(y,p): return float(mean_absolute_error(y,p)),float(mean_squared_error(y,p)**.5)

def choose_weight(y,persist,map_pred):
    grid=np.linspace(0,1,41); vals=[np.mean(np.abs(y-(w*persist+(1-w)*map_pred))) for w in grid]; i=int(np.argmin(vals)); return float(grid[i]),float(vals[i])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",default="data/raw/cicv5g"); ap.add_argument("--output",default="results/real_v2x_horizon"); ap.add_argument("--horizons",default="1,5,10,20,50,100"); ap.add_argument("--seed",type=int,default=0); ap.add_argument("--alpha",type=float,default=.1)
    a=ap.parse_args(); out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    files=discover_cicv5g_files(a.data); df=pd.concat([add_run_metadata(load_cicv5g_file(p),p) for p in files],ignore_index=True)
    train,cal,test,split=blocked_run_split(df,seed=a.seed); support=SpatialSupportModel(radius_m=15,min_neighbors=5).fit(train)
    map_delay=SpatialKNNPredictor("delay_ms",20).fit(train); map_sinr=SpatialKNNPredictor("sinr_db",20).fit(train)
    summary=[]; runrows=[]
    for h in [int(x) for x in a.horizons.split(",") if x.strip()]:
        ca=pairs(cal,h); te=pairs(test,h)
        if len(ca)<200 or len(te)<200: continue
        for target,current_col,map_model in [("delay_ms","current_delay_ms",map_delay),("sinr_db","current_sinr_db",map_sinr)]:
            cy=ca[target].to_numpy(float); cp=ca[current_col].to_numpy(float); cm=map_model.predict(ca); w,_=choose_weight(cy,cp,cm)
            ty=te[target].to_numpy(float); tp=te[current_col].to_numpy(float); tm=map_model.predict(te); tf=w*tp+(1-w)*tm
            pmae,prmse=err(ty,tp); mmae,mrmse=err(ty,tm); fmae,frmse=err(ty,tf)
            rec={"target":target,"horizon_steps":h,"median_horizon_ms":float(np.median(te.horizon_ms)),"fusion_persistence_weight":w,"persistence_mae":pmae,"spatial_mae":mmae,"fusion_mae":fmae,"persistence_rmse":prmse,"spatial_rmse":mrmse,"fusion_rmse":frmse}
            if target=="delay_ms":
                cd=support.evaluate(ca)["nearest_distance_m"]; td=support.evaluate(te)["nearest_distance_m"]; cf=w*cp+(1-w)*cm
                glob=ResidualConformalCalibrator(a.alpha).fit(cy,cf); glo,ghi=glob.interval(tf)
                cond=SupportConditionalConformalCalibrator(a.alpha).fit(cy,cf,cd); alo,ahi=cond.interval(tf,td)
                rec.update({"global_coverage":float(np.mean((ty>=glo)&(ty<=ghi))),"adaptive_coverage":float(np.mean((ty>=alo)&(ty<=ahi))),"global_width_ms":float(np.mean(ghi-glo)),"adaptive_width_ms":float(np.mean(ahi-alo)),"adaptive_bin_counts":json.dumps(cond.counts_),"adaptive_bin_radii_ms":json.dumps(cond.radii_.tolist())})
            summary.append(rec)
            temp=te[["run_id"]].copy(); temp["y"]=ty; temp["persist"]=tp; temp["map_pred"]=tm; temp["fusion"]=tf
            for run,g in temp.groupby("run_id"):
                runrows.append({"target":target,"horizon_steps":h,"run_id":run,"n":len(g),"persistence_mae":float(np.mean(np.abs(g["y"]-g["persist"]))),"spatial_mae":float(np.mean(np.abs(g["y"]-g["map_pred"]))),"fusion_mae":float(np.mean(np.abs(g["y"]-g["fusion"]))),"fusion_persistence_weight":w})
    pd.DataFrame(summary).to_csv(out/"horizon_summary.csv",index=False); pd.DataFrame(runrows).to_csv(out/"horizon_run_metrics.csv",index=False); (out/"split.json").write_text(json.dumps(split,indent=2),encoding="utf-8"); print(pd.DataFrame(summary).to_string(index=False))

if __name__=="__main__": main()
