import importlib.util
from pathlib import Path
import numpy as np
import pytest
torch=pytest.importorskip('torch')
from iscai.prediction.transformer import TrajectoryTransformer
spec=importlib.util.spec_from_file_location('closed_loop',Path(__file__).parents[1]/'scripts'/'run_cmht_closed_loop.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def test_transformer_forecast_returns_absolute_mean_and_positive_sigma():
 torch.manual_seed(1);m=TrajectoryTransformer(d_model=16,nhead=4,layers=1,horizon=4).eval();h=np.array([[0.,0.],[1.,0.],[2.,0.],[3.,0.]],float);mean,sigma=mod.transformer_forecast(m,h,3);assert mean.shape==(3,2);assert sigma.shape==(3,2);assert np.all(sigma>0);# model means are displacements anchored at last observation
 with torch.no_grad():raw,_=m(torch.tensor(h[None],dtype=torch.float32))
 assert np.allclose(mean,h[-1]+raw[0,:3].numpy())
