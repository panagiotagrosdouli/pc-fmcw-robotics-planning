import importlib.util
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location('closed_loop',Path(__file__).parents[1]/'scripts'/'run_cmht_closed_loop.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_initial_ego_is_behind_motion_direction():
    h=np.array([[0.,0.],[1.,0.],[2.,0.]])
    e=mod.initial_ego(h,.1,gap=5.)
    assert np.allclose(e[:2],[-3.,0.])
    assert e[3]>0

def test_states_from_xy_has_speed_and_heading():
    s=mod.states_from_xy(np.array([[0.,0.],[1.,0.],[2.,0.]]),.5)
    assert s.shape==(3,4)
    assert np.allclose(s[:,2],0.)
    assert np.allclose(s[:,3],2.)

def test_tracks_split_annotation_gaps():
    rows=[[0,0,0,0,'a','Car'],[1,1,0,0,'a','Car'],[2,2,0,0,'a','Car'],[7,7,0,0,'a','Car'],[8,8,0,0,'a','Car'],[9,9,0,0,'a','Car']]
    out=list(mod.tracks(rows))
    assert len(out)==2
    assert all(len(xy)==3 for _,_,xy in out)
