import numpy as np
from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings,_prediction,run_simulated_episode
from iscai.simulation.scenario import following_lateral_offset

def test_cv_prediction_is_finite_and_has_requested_horizon():
 h=np.array([[0.,0.],[1.,0.],[2.,0.]])
 p=_prediction(h,5,1.0);assert p.shape==(5,4);assert np.all(np.isfinite(p));assert np.allclose(p[:,0],[3,4,5,6,7])

def test_dataset_free_episode_is_reproducible_and_claim_safe():
 s=following_lateral_offset(steps=8,dt=.1);cfg=BenchmarkSettings(horizon_steps=5,p3_mc_samples=2)
 a=run_simulated_episode('P2',s,seed=7,settings=cfg);b=run_simulated_episode('P2',s,seed=7,settings=cfg)
 assert a==b;assert a['measured_optical_link'] is False;assert np.isfinite(a['mean_snr_db'])

def test_p3_runs_with_same_mean_prediction_interface():
 s=following_lateral_offset(steps=6,dt=.1);cfg=BenchmarkSettings(horizon_steps=4,p3_mc_samples=2)
 r=run_simulated_episode('P3',s,seed=3,settings=cfg);assert r['planner']=='P3';assert r['no_candidate_steps']>=0
