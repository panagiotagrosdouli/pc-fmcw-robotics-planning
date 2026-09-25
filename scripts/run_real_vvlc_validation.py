#!/usr/bin/env python3
"""Real vehicular optical path-loss validation for the active-calibration geometry model.

Data source:
  Bugra Turan / Sinem Coleri ML_VVLC public measurement repository.
  IEEE TVT 2021, DOI 10.1109/TVT.2021.3107835.

This script validates whether a directional geometry term adds held-out predictive
value on measured vehicular VLC path loss. It does NOT claim direct calibration of
the repository's PC-FMCW optical waveform or closed-loop vehicle validation.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import urllib.request

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from sklearn.model_selection import GroupShuffleSplit

UPSTREAM_REPO="bugratu/ML_VVLC"
UPSTREAM_COMMIT="bdf38f402d67f9f1c48daea074730136cb6bef7e"
RAW_REL="datasets/rawPLdataset.csv"
VAL_REL="datasets/valPLdata.csv"
PAPER_DOI="10.1109/TVT.2021.3107835"


def _download(rel: str,dest: Path):
    dest.parent.mkdir(parents=True,exist_ok=True)
    url=f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{UPSTREAM_COMMIT}/{rel}"
    req=urllib.request.Request(url,headers={"User-Agent":"pc-fmcw-active-self-calibration"})
    with urllib.request.urlopen(req,timeout=60) as response,dest.open("wb") as out:
        for block in iter(lambda:response.read(1024*1024),b""): out.write(block)
    if not dest.exists() or dest.stat().st_size==0: raise RuntimeError(f"empty download: {url}")
    return url


def _sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()


def _norm(name):
    return " ".join(str(name).strip().lower().replace("_"," ").split())


def load_raw(path: Path):
    df=pd.read_csv(path,sep=";")
    columns={_norm(c):c for c in df.columns}
    required={
        "east","north","sunload","lane","receiver angle","distance",
        "turbulence","path loss",
    }
    missing=required-set(columns)
    if missing: raise ValueError(f"raw V-VLC data missing columns: {sorted(missing)}")
    out=pd.DataFrame({
        "east":pd.to_numeric(df[columns["east"]],errors="coerce"),
        "north":pd.to_numeric(df[columns["north"]],errors="coerce"),
        "sunload":pd.to_numeric(df[columns["sunload"]],errors="coerce"),
        "lane":pd.to_numeric(df[columns["lane"]],errors="coerce"),
        "angle_deg":pd.to_numeric(df[columns["receiver angle"]],errors="coerce"),
        "distance_m":pd.to_numeric(df[columns["distance"]],errors="coerce"),
        "turbulence":pd.to_numeric(df[columns["turbulence"]],errors="coerce"),
        "path_loss_db":pd.to_numeric(df[columns["path loss"]],errors="coerce"),
    }).dropna()
    out=out[(out.distance_m>0)&np.isfinite(out.path_loss_db)].reset_index(drop=True)
    out["spatial_group"]=(
        out.east.round(3).astype(str)+"_"+out.north.round(3).astype(str)
    )
    return out


def load_repository_validation(path: Path):
    """Parse repository-provided validation table (variables as rows, samples as columns)."""
    a=pd.read_csv(path,sep=",",header=None)
    if a.shape[0]<6: raise ValueError("validation table must contain at least six rows")
    a=a.iloc[:6].T
    a.columns=["sunload","lane","angle_deg","distance_m","turbulence","path_loss_db"]
    for c in a.columns:a[c]=pd.to_numeric(a[c],errors="coerce")
    return a.dropna().query("distance_m > 0").reset_index(drop=True)


def split_groups(df,seed):
    groups=df.spatial_group.to_numpy()
    unique=np.unique(groups)
    if len(unique)<5: raise ValueError("need at least five spatial groups")
    splitter=GroupShuffleSplit(n_splits=1,test_size=.40,random_state=seed)
    train_idx,temp_idx=next(splitter.split(df,groups=groups))
    temp=df.iloc[temp_idx].reset_index(drop=True)
    temp_groups=temp.spatial_group.to_numpy()
    splitter2=GroupShuffleSplit(n_splits=1,test_size=.50,random_state=seed+1)
    cal_rel,test_rel=next(splitter2.split(temp,groups=temp_groups))
    return df.iloc[train_idx].copy(),temp.iloc[cal_rel].copy(),temp.iloc[test_rel].copy()


def _features(df):
    logd=np.log10(np.maximum(df.distance_m.to_numpy(float),.1)/10.0)
    angle=np.deg2rad(df.angle_deg.to_numpy(float))
    return logd,angle


def fit_distance(train):
    logd,_=_features(train);y=train.path_loss_db.to_numpy(float)
    x=np.column_stack([np.ones(len(train)),logd])
    beta=np.linalg.lstsq(x,y,rcond=None)[0]
    return {"intercept_db":float(beta[0]),"distance_coefficient_db_per_decade":float(beta[1])}


def predict_distance(df,p):
    logd,_=_features(df)
    return p["intercept_db"]+p["distance_coefficient_db_per_decade"]*logd


def fit_directional(train):
    logd,angle=_features(train);y=train.path_loss_db.to_numpy(float)
    d0=fit_distance(train)
    x0=np.array([d0["intercept_db"],max(0.0,d0["distance_coefficient_db_per_decade"]),10.0,0.0])
    lo=np.array([-200.0,0.0,0.0,-np.deg2rad(45.0)])
    hi=np.array([200.0,120.0,800.0,np.deg2rad(45.0)])
    def residual(x):
        b0,bd,ba,delta=x
        return b0+bd*logd+ba*(angle-delta)**2-y
    res=least_squares(residual,x0,bounds=(lo,hi),loss="linear",max_nfev=10000)
    if not res.success: raise RuntimeError(f"directional fit failed: {res.message}")
    b0,bd,ba,delta=res.x
    beam_sigma=.12
    alpha_loss=bd/(10.0*2.0)
    k_angular=ba*(beam_sigma**2)*np.log(10.0)/5.0
    return {
        "intercept_db":float(b0),
        "distance_coefficient_db_per_decade":float(bd),
        "angle_quadratic_db_per_rad2":float(ba),
        "delta_beam_rad":float(delta),
        "mapped_alpha_loss":float(alpha_loss),
        "mapped_k_angular":float(k_angular),
        "mapping_status":"transfer-form mapping into modeled PC-FMCW geometry variables; not direct PC-FMCW calibration",
    }


def predict_directional(df,p):
    logd,angle=_features(df)
    return (
        p["intercept_db"]
        +p["distance_coefficient_db_per_decade"]*logd
        +p["angle_quadratic_db_per_rad2"]*(angle-p["delta_beam_rad"])**2
    )


def metrics(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);e=p-y
    return {
        "n":int(len(y)),"mae_db":float(np.mean(np.abs(e))),
        "rmse_db":float(np.sqrt(np.mean(e**2))),"bias_db":float(np.mean(e)),
    }


def conformal_radius(y,p,alpha=.1):
    r=np.abs(np.asarray(y,float)-np.asarray(p,float))
    if len(r)==0:return float("nan")
    q=min(1.0,np.ceil((len(r)+1)*(1-alpha))/len(r))
    return float(np.quantile(r,q,method="higher"))


def paired_group_effects(test,p0,p1,bootstrap=10000,seed=2026):
    work=test[["spatial_group","path_loss_db"]].copy()
    work["e0"]=np.abs(p0-work.path_loss_db.to_numpy(float))
    work["e1"]=np.abs(p1-work.path_loss_db.to_numpy(float))
    g=work.groupby("spatial_group",as_index=False).agg(distance_abs_error=("e0","mean"),directional_abs_error=("e1","mean"))
    delta=(g.directional_abs_error-g.distance_abs_error).to_numpy(float)
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(delta),size=(bootstrap,len(delta)))
    boot=delta[idx].mean(axis=1)
    try:
        from scipy.stats import wilcoxon
        pv=float(wilcoxon(delta,zero_method="wilcox").pvalue) if np.any(~np.isclose(delta,0.0)) else 1.0
    except ValueError: pv=1.0
    sd=float(np.std(delta,ddof=1)) if len(delta)>1 else 0.0
    dz=0.0 if sd==0.0 else float(np.mean(delta)/sd)
    return g,{
        "comparison":"directional_minus_distance_only_absolute_error",
        "inference_unit":"held-out spatial group",
        "n_groups":int(len(delta)),
        "mean_delta_mae_db":float(np.mean(delta)),
        "ci95_low_db":float(np.quantile(boot,.025)),
        "ci95_high_db":float(np.quantile(boot,.975)),
        "wilcoxon_p":pv,
        "cohens_dz":dz,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,default=Path("artifacts/active_self_calibration/real_vvlc"))
    ap.add_argument("--seed",type=int,default=2026)
    ap.add_argument("--bootstrap",type=int,default=10000)
    args=ap.parse_args()
    out=args.output;raw_dir=out/"_raw";raw=raw_dir/"rawPLdataset.csv";val=raw_dir/"valPLdata.csv"
    raw_url=_download(RAW_REL,raw);val_url=_download(VAL_REL,val)
    df=load_raw(raw);train,cal,test=split_groups(df,args.seed)
    repo_val=load_repository_validation(val)
    dfit=fit_distance(train);qfit=fit_directional(train)

    records=[]
    predictions={}
    for split_name,frame in (("train",train),("calibration",cal),("spatial_test",test),("repository_validation",repo_val)):
        y=frame.path_loss_db.to_numpy(float)
        for name,fit,predfn in (
            ("distance_only",dfit,predict_distance),("directional",qfit,predict_directional)
        ):
            pred=predfn(frame,fit);predictions[(split_name,name)]=pred
            records.append({"split":split_name,"model":name,**metrics(y,pred)})

    radii={
        "distance_only":conformal_radius(cal.path_loss_db,predictions[("calibration","distance_only")]),
        "directional":conformal_radius(cal.path_loss_db,predictions[("calibration","directional")]),
    }
    test_coverage=[]
    for name in ("distance_only","directional"):
        pred=predictions[("spatial_test",name)];y=test.path_loss_db.to_numpy(float);r=radii[name]
        test_coverage.append({
            "model":name,"calibration_radius_90_db":r,
            "spatial_test_coverage":float(np.mean(np.abs(y-pred)<=r)),
            "spatial_test_mean_interval_width_db":float(2*r),
        })

    group_metrics,effect=paired_group_effects(
        test,predictions[("spatial_test","distance_only")],
        predictions[("spatial_test","directional")],args.bootstrap,args.seed,
    )
    strata=test[["lane","angle_deg","turbulence","path_loss_db"]].copy()
    strata["distance_abs_error"]=np.abs(predictions[("spatial_test","distance_only")]-strata.path_loss_db)
    strata["directional_abs_error"]=np.abs(predictions[("spatial_test","directional")]-strata.path_loss_db)
    strata_summary=strata.groupby(["lane","angle_deg","turbulence"],dropna=False,as_index=False).agg(
        n=("path_loss_db","size"),measured_path_loss_mean_db=("path_loss_db","mean"),
        distance_mae_db=("distance_abs_error","mean"),directional_mae_db=("directional_abs_error","mean"),
    )

    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(records).to_csv(out/"model_metrics.csv",index=False)
    pd.DataFrame(test_coverage).to_csv(out/"interval_metrics.csv",index=False)
    group_metrics.to_csv(out/"spatial_group_metrics.csv",index=False)
    pd.DataFrame([effect]).to_csv(out/"paired_effect.csv",index=False)
    strata_summary.to_csv(out/"residual_strata.csv",index=False)
    split_summary=pd.DataFrame([
        {"split":"train","rows":len(train),"spatial_groups":train.spatial_group.nunique()},
        {"split":"calibration","rows":len(cal),"spatial_groups":cal.spatial_group.nunique()},
        {"split":"spatial_test","rows":len(test),"spatial_groups":test.spatial_group.nunique()},
        {"split":"repository_validation","rows":len(repo_val),"spatial_groups":np.nan},
    ])
    split_summary.to_csv(out/"split_summary.csv",index=False)
    fit_payload={"distance_only":dfit,"directional":qfit}
    (out/"fit_parameters.json").write_text(json.dumps(fit_payload,indent=2),encoding="utf-8")
    manifest={
        "schema_version":1,"study":"real vehicular VLC geometry validation",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "dataset_repository":UPSTREAM_REPO,"upstream_commit":UPSTREAM_COMMIT,
        "paper_doi":PAPER_DOI,
        "files":{
            RAW_REL:{"url":raw_url,"sha256":_sha256(raw),"bytes":raw.stat().st_size},
            VAL_REL:{"url":val_url,"sha256":_sha256(val),"bytes":val.stat().st_size},
        },
        "raw_rows":int(len(df)),"repository_validation_rows":int(len(repo_val)),
        "split_policy":"grouped by rounded measured East/North location; 60/20/20 train/calibration/spatial-test",
        "primary_real_data_comparison":"directional vs distance-only absolute path-loss error on held-out spatial groups",
        "repository_validation_status":"secondary descriptive validation; independence from raw training table is stated upstream as validation but not independently verified here",
        "measured_quantity":"vehicular VLC path loss",
        "claim_boundary":"REAL measured vehicular VLC path loss. This validates directional optical-geometry relevance and transfer-form parameter estimation; it is not direct PC-FMCW waveform calibration, not a measured PC-FMCW link, and not closed-loop planning validation.",
    }
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    # Raw external measurements are transient and deliberately not retained as an artifact.
    raw.unlink(missing_ok=True);val.unlink(missing_ok=True)
    try: raw_dir.rmdir()
    except OSError: pass
    print(pd.DataFrame(records).to_string(index=False))
    print(json.dumps(effect,indent=2))
    print(json.dumps(fit_payload,indent=2))


if __name__=="__main__":
    main()
