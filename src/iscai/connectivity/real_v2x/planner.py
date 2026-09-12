from __future__ import annotations
from enum import Enum
import numpy as np

class PlannerMode(str, Enum):
    P0="P0"; P1="P1"; P2="P2"; P3="P3"


def _norm(x, lo, hi):
    return np.clip((np.asarray(x,float)-lo)/max(hi-lo,1e-9),0,1)


def score_candidates(candidates, predictor, support_model=None, calibrator=None,
                     mode=PlannerMode.P2, comm_weight=1.0, risk_weight=1.0,
                     delay_threshold_ms=50.0, unsupported_penalty=1.0):
    """Score already-safe tabular candidate trajectories using measured-data QoS models.

    Each candidate is dict(df=<future states with causal QoS context>, mobility_cost=float).
    Safety remains external and common across planner variants. Counterfactual candidate
    tables must carry current/causal lag context explicitly; future measured QoS must not
    be inserted as a planner input.
    """
    out=[]
    for c in candidates:
        df=c["df"]; mobility=float(c.get("mobility_cost",0.0))
        if mode == PlannerMode.P0:
            out.append({**c,"score":mobility,"comm_cost":0.0,"risk_cost":0.0}); continue
        if mode == PlannerMode.P1:
            if "delay_lag1" not in df:
                raise ValueError("P1 requires causal current delay in delay_lag1; future measured delay must not be used")
            pred=np.repeat(float(df["delay_lag1"].iloc[0]),len(df))
        else:
            pred=np.asarray(predictor.predict(df),float)
        comm=float(np.mean(_norm(pred,0,delay_threshold_ms*2)))
        risk=0.0
        if mode == PlannerMode.P3 and calibrator is not None:
            _,hi=calibrator.interval(pred)
            risk=float(np.mean(hi>delay_threshold_ms))
        unsupported=0.0
        if support_model is not None:
            s=support_model.evaluate(df)
            unsupported=float(np.mean(~s["supported"]))
        score=mobility+comm_weight*comm+risk_weight*risk+unsupported_penalty*unsupported
        out.append({**c,"score":float(score),"comm_cost":comm,"risk_cost":risk,"unsupported_fraction":unsupported,"pred_delay_ms":pred})
    return sorted(out,key=lambda z:z["score"])
