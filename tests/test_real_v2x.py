from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np, pandas as pd
from iscai.connectivity.real_v2x.datasets import load_cicv5g_file, blocked_run_split
from iscai.connectivity.real_v2x.predictors import TreeQoSPredictor
from iscai.connectivity.real_v2x.uncertainty import ResidualConformalCalibrator
from iscai.connectivity.real_v2x.support import SpatialSupportModel


def _df(run):
    n=20; x=np.arange(n,dtype=float)
    return pd.DataFrame({"pub_time_ms":x,"sub_time_ms":x+10,"delay_ms":10+x%4,"utm_x_m":x,"utm_y_m":np.zeros(n),"heading_rad":np.zeros(n),"velocity_mps":np.ones(n)*5,"cell_id":"A","sinr_db":20-x*.1,"rsrp_db":-80-x*.1,"run_id":run})

def test_group_split_no_run_leakage():
    d=pd.concat([_df(f"r{i}") for i in range(5)],ignore_index=True); tr,ca,te,_=blocked_run_split(d)
    assert set(tr.run_id).isdisjoint(ca.run_id) and set(tr.run_id).isdisjoint(te.run_id) and set(ca.run_id).isdisjoint(te.run_id)

def test_support_flags_far_points():
    m=SpatialSupportModel(radius_m=2,min_neighbors=2).fit(_df("r")); q=_df("q").iloc[:2].copy(); q["utm_x_m"]=[5,100]; s=m.evaluate(q)
    assert bool(s["supported"][0]) and not bool(s["supported"][1])

def test_conformal_has_expected_shape():
    c=ResidualConformalCalibrator(.1).fit([1,2,3,4],[1,2,2,5]); lo,hi=c.interval([10,20]); assert lo.shape==(2,) and np.all(hi>=lo)

def test_tree_predictor_runs():
    d=pd.concat([_df("a"),_df("b")],ignore_index=True); m=TreeQoSPredictor(n_estimators=10).fit(d); assert m.predict(d.iloc[:3]).shape==(3,)

def test_loader_handles_extra_position_columns(tmp_path):
    p=tmp_path/"x.txt"; p.write_text("pub_time(ms) sub_time(ms) delay(ms) utmX(m) utmY(m) heading(rad) velocity(m/s) cellid(db) sinr(db) rsrp(db)\n1 2 1 3 4 0 5 A 10 -80 3.1 4.1\n")
    d=load_cicv5g_file(p); assert "current_x_m" in d and "current_y_m" in d and len(d)==1

def test_metadata_detects_s2w_direction(tmp_path):
    from iscai.connectivity.real_v2x.datasets import add_run_metadata
    p=tmp_path/"n8"/"V30"/"s2w_n8_v30_run01.txt"; out=add_run_metadata(pd.DataFrame({"delay_ms":[1]}),p)
    assert out.loc[0,"scenario"]=="W2S" and out.loc[0,"direction"]=="s2w" and out.loc[0,"network"]=="n8" and out.loc[0,"nominal_speed_kmh"]==30.0

def test_candidate_scorer_penalizes_unsupported():
    from iscai.connectivity.real_v2x.planner import score_candidates, PlannerMode
    class Predictor:
        def predict(self,df): return np.asarray(df["mock_pred"],float)
    class Support:
        def evaluate(self,df):
            flag=np.asarray(df["supported"],bool); return {"supported":flag,"nearest_distance_m":np.zeros(len(df)),"local_count":np.ones(len(df),int)}
    a=pd.DataFrame({"mock_pred":[10,10],"supported":[True,True]}); b=pd.DataFrame({"mock_pred":[10,10],"supported":[False,False]})
    ranked=score_candidates([{"name":"a","df":a,"mobility_cost":0.0},{"name":"b","df":b,"mobility_cost":0.0}],Predictor(),Support(),mode=PlannerMode.P2,unsupported_penalty=2.0)
    assert ranked[0]["name"]=="a" and ranked[1]["score"]>ranked[0]["score"]

def test_explicit_candidate_lag_context_is_not_overwritten():
    from iscai.connectivity.real_v2x.predictors import make_features
    d=_df("candidate").iloc[:3].copy(); d["delay_lag1"]=77.0; d["sinr_lag1"]=-3.0
    f=make_features(d); assert np.all(f.delay_lag1==77.0) and np.all(f.sinr_lag1==-3.0)

def test_support_conditional_conformal_uses_distance_bins():
    from iscai.connectivity.real_v2x.uncertainty import SupportConditionalConformalCalibrator
    y=np.r_[np.zeros(120),np.ones(120)*10]; p=np.zeros(240); d=np.r_[np.zeros(120)+.5,np.zeros(120)+8]
    c=SupportConditionalConformalCalibrator(alpha=.1,min_bin_samples=50).fit(y,p,d)
    r=c.radii([.5,8.0]); assert r[1] > r[0]

def test_conditioned_spatial_map_separates_known_network_contexts():
    from iscai.connectivity.real_v2x.predictors import ConditionedSpatialKNNPredictor
    a=_df("a"); b=_df("b");
    for d,net,delay in [(a,"n8",10.0),(b,"n78",40.0)]:
        d["network"]=net; d["direction"]="w2s"; d["nominal_speed_kmh"]=30.0; d["delay_ms"]=delay
    train=pd.concat([a,b],ignore_index=True); m=ConditionedSpatialKNNPredictor("delay_ms",n_neighbors=3,min_group_samples=5).fit(train)
    q=train.iloc[[0,20]].copy(); pred=m.predict(q)
    assert pred[0] < 15 and pred[1] > 35
