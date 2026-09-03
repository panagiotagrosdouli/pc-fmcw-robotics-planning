import numpy as np
import pytest
from iscai.prediction.trajectory_predictor import constant_velocity


def test_constant_velocity_uses_irregular_measured_times():
    history_t=np.array([10.0,10.07,10.19,10.31])
    velocity=np.array([3.0,-1.5])
    origin=np.array([4.0,2.0])
    history=origin+(history_t-history_t[0])[:,None]*velocity
    future_t=np.array([10.40,10.55,10.73])
    pred=constant_velocity(history,3,history_times=history_t,future_times=future_t)
    expected=origin+(future_t-history_t[0])[:,None]*velocity
    assert np.allclose(pred,expected,atol=1e-10)


def test_measured_times_must_follow_history():
    history=np.array([[0.,0.],[1.,0.]])
    with pytest.raises(ValueError,match='after the final history'):
        constant_velocity(history,1,history_times=[1.,2.],future_times=[1.5])


def test_uniform_dt_api_remains_backward_compatible():
    history=np.array([[0.,0.],[1.,2.],[2.,4.]])
    pred=constant_velocity(history,2,0.5)
    assert np.allclose(pred,[[3.,6.],[4.,8.]])
