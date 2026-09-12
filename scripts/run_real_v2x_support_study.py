#!/usr/bin/env python3
"""Leakage-safe real-CICV5G QoS prediction, uncertainty and support study."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from iscai.connectivity.real_v2x.datasets import load_cicv5g_file, add_run_metadata, discover_cicv5g_files, blocked_run_split
from iscai.connectivity.real_v2x.predictors import PersistencePredictor, SpatialKNNPredictor, TreeQoSPredictor
from iscai.connectivity.real_v2x.uncertainty import ResidualConformalCalibrator
from iscai.connectivity.real_v2x.support import SpatialSupportModel

def metrics(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float)
    return {"mae":float(mean_absolute_error(y,p)),"rmse":float(mean_squared_error(y,p)**.5)}

def fit_models(target):
    return {"persistence":PersistencePredictor(target),"spatial_knn":SpatialKNNPredictor(target,20),"extra_trees":TreeQoSPredictor(target,"extra_trees",300,0),"random_forest":TreeQoSPredictor(target,"random_forest",300,0)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",default="data/raw/cicv5g"); ap.add_argument("--output",default="results/real_v2x_support"); ap.add_argument("--alpha",type=float,default=.1); ap.add_argument("--support-radius-m",type=float,default=15.0); ap.add_argument("--support-min-neighbors",type=int,default=5); ap.add_argument("--delay-threshold-ms",type=float,default=50.0); ap.add_argument("--seed",type=int,default=0)
    args=ap.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    files=discover_cicv5g_files(args.data)
    if len(files)<6: raise SystemExit("Need >=6 CICV5G run files; run scripts/prepare_cicv5g.py first")
    df=pd.concat([add_run_metadata(load_cicv5g_file(p),p) for p in files],ignore_index=True)
    train,cal,test,split=blocked_run_split(df,seed=args.seed); (out/"split.json").write_text(json.dumps(split,indent=2),encoding="utf-8")
    ds=(df.groupby(["network","nominal_speed_kmh","direction"],dropna=False).agg(samples=("delay_ms","size"),runs=("run_id","nunique"),delay_mean_ms=("delay_ms","mean"),delay_p95_ms=("delay_ms",lambda x:float(np.quantile(x,.95))),sinr_mean_db=("sinr_db","mean")).reset_index())
    ds.to_csv(out/"dataset_summary.csv",index=False)
    predictor_rows=[]; per_run_rows=[]; fitted_delay={}
    for target,unit in [("delay_ms","ms"),("sinr_db","dB")]:
        for name,model in fit_models(target).items():
            t0=time.perf_counter(); model.fit(train); fit_s=time.perf_counter()-t0
            t1=time.perf_counter(); pred=model.predict(test); pred_s=time.perf_counter()-t1
            mm=metrics(test[target],pred); predictor_rows.append({"target":target,"unit":unit,"model":name,"mae":mm["mae"],"rmse":mm["rmse"],"fit_s":fit_s,"predict_us_per_sample":pred_s/max(len(test),1)*1e6})
            if target=="delay_ms": fitted_delay[name]=model
            tmp=test[["run_id",target]].copy(); tmp["pred"]=pred
            for run,g in tmp.groupby("run_id"):
                rm=metrics(g[target],g.pred); per_run_rows.append({"target":target,"model":name,"run_id":run,"n":len(g),"mae":rm["mae"],"rmse":rm["rmse"]})
    predictor_df=pd.DataFrame(predictor_rows); predictor_df.to_csv(out/"predictor_metrics.csv",index=False); pd.DataFrame(per_run_rows).to_csv(out/"predictor_run_metrics.csv",index=False)
    best=str(predictor_df[predictor_df.target=="delay_ms"].sort_values("mae").iloc[0].model); model=fitted_delay[best]
    cal_pred=model.predict(cal); conformal=ResidualConformalCalibrator(args.alpha).fit(cal.delay_ms.to_numpy(),cal_pred)
    test_pred=model.predict(test); lo,hi=conformal.interval(test_pred); coverage=float(np.mean((test.delay_ms.to_numpy()>=lo)&(test.delay_ms.to_numpy()<=hi)))
    support=SpatialSupportModel(args.support_radius_m,args.support_min_neighbors).fit(train); ss=support.evaluate(test)
    cols=["run_id","network","nominal_speed_kmh","direction","pub_time_ms","utm_x_m","utm_y_m","delay_ms","sinr_db"]
    pt=test[cols].copy(); pt["pred_delay_ms"]=test_pred; pt["interval_lo_ms"]=lo; pt["interval_hi_ms"]=hi; pt["covered"]=(pt.delay_ms>=lo)&(pt.delay_ms<=hi); pt["nearest_train_m"]=ss["nearest_distance_m"]; pt["local_train_count"]=ss["local_count"]; pt["supported"]=ss["supported"]; pt["delay_violation"]=pt.delay_ms>args.delay_threshold_ms; pt["pred_delay_violation"]=pt.pred_delay_ms>args.delay_threshold_ms; pt.to_csv(out/"test_predictions.csv",index=False)
    run_rows=[]
    for run,g in pt.groupby("run_id"):
        run_rows.append({"run_id":run,"n":len(g),"network":g.network.iloc[0],"direction":g.direction.iloc[0],"nominal_speed_kmh":g.nominal_speed_kmh.iloc[0],"mae_ms":float(np.mean(np.abs(g.delay_ms-g.pred_delay_ms))),"violation_rate":float(g.delay_violation.mean()),"pred_violation_rate":float(g.pred_delay_violation.mean()),"interval_coverage":float(g.covered.mean()),"unsupported_fraction":float((~g.supported).mean()),"mean_nearest_m":float(g.nearest_train_m.mean())})
    pd.DataFrame(run_rows).to_csv(out/"run_metrics.csv",index=False)
    bins=[-np.inf,1,5,15,30,60,np.inf]; labels=["<=1m","1-5m","5-15m","15-30m","30-60m",">60m"]; pt["support_bin"]=pd.cut(pt.nearest_train_m,bins=bins,labels=labels)
    sr=[]
    for b,g in pt.groupby("support_bin",observed=True): sr.append({"support_bin":str(b),"n":len(g),"mae_ms":float(np.mean(np.abs(g.delay_ms-g.pred_delay_ms))),"coverage":float(g.covered.mean()),"violation_rate":float(g.delay_violation.mean())})
    pd.DataFrame(sr).to_csv(out/"support_stratified_metrics.csv",index=False)
    summary={"n_files":len(files),"n_runs":int(df.run_id.nunique()),"n_total":len(df),"n_train":len(train),"n_cal":len(cal),"n_test":len(test),"split":split,"best_delay_model":best,"conformal_alpha":args.alpha,"conformal_radius_ms":conformal.radius_,"test_interval_coverage":coverage,"support_radius_m":args.support_radius_m,"support_min_neighbors":args.support_min_neighbors,"test_unsupported_fraction":float(np.mean(~ss["supported"])),"delay_threshold_ms":args.delay_threshold_ms,"threshold_status":"experimental operating point; not claimed as a universal standard","claim_boundary":"QoS samples are measured; QoS forecasts are learned; counterfactual motion remains offline/model-based."}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8"); print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
