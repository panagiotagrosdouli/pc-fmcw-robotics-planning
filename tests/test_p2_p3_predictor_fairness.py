import importlib.util
from pathlib import Path
import numpy as np

P=Path(__file__).resolve().parents[1]/'scripts'/'run_cmht_closed_loop.py';spec=importlib.util.spec_from_file_location('cl',P);cl=importlib.util.module_from_spec(spec);spec.loader.exec_module(cl)

def test_p2_p3_share_transformer_mean():
 cv=np.array([[1.,0.],[2.,0.]])
 truth=np.array([[1.,1.],[2.,1.]])
 mean=np.array([[1.2,.3],[2.4,.5]])
 sigma=np.array([[.4,.5],[.6,.7]])
 p2,pr2,u2=cl.planner_targets('P2',cv,truth,mean,sigma,.1,.75)
 p3,pr3,u3=cl.planner_targets('P3',cv,truth,mean,sigma,.1,.75)
 assert pr2==pr3=='transformer'
 assert np.allclose(p2[:,:2],p3['mean_xy'])
 assert np.allclose(p3['sigma_xy'],sigma)

def test_p2_p3_share_cv_mean_without_transformer():
 cv=np.array([[1.,0.],[2.,0.]])
 truth=np.array([[1.,1.],[2.,1.]])
 p2,_,_=cl.planner_targets('P2',cv,truth,None,None,.1,.75)
 p3,_,u3=cl.planner_targets('P3',cv,truth,None,None,.1,.75)
 assert np.allclose(p2[:,:2],p3['mean_xy'])
 assert np.allclose(p3['sigma_xy'],.75)
 assert u3=='fixed_sigma'
