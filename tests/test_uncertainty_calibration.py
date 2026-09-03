import numpy as np
import pytest
from iscai.prediction.uncertainty_metrics import optimal_sigma_scale,apply_sigma_scale,gaussian_nll_numpy

def test_optimal_scale_recovers_known_miscalibration():
 mean=np.zeros((4,2));sigma=np.ones((4,2));truth=np.full((4,2),2.0);c=optimal_sigma_scale(mean,sigma,truth);assert c==pytest.approx(2.0)

def test_optimal_scale_does_not_increase_nll():
 mean=np.zeros((5,2));sigma=np.ones((5,2));truth=np.array([[3.,-2.],[1.,2.],[-2.,3.],[2.,-1.],[-3.,1.]])
 c=optimal_sigma_scale(mean,sigma,truth);assert gaussian_nll_numpy(mean,apply_sigma_scale(sigma,c),truth)<=gaussian_nll_numpy(mean,sigma,truth)+1e-12

def test_invalid_scale_rejected():
 with pytest.raises(ValueError):apply_sigma_scale(np.ones((2,2)),0.)
