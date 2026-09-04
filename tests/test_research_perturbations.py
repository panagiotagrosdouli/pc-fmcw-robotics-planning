import numpy as np
import pytest

from pc_fmcw_robustness.perturbations import delayed_history, perturb_prediction


def test_prediction_bias_is_applied_without_extra_noise():
    values = np.array([1.0, 2.0, 3.0])
    shifted = perturb_prediction(values, bias=2.0, noise_scale=1.0)
    assert np.allclose(shifted, values + 2.0)


def test_delayed_history_removes_unavailable_future_samples():
    values = np.arange(5)
    delayed = delayed_history(values, 2)
    assert delayed.tolist() == [0, 1, 2]


def test_negative_delay_rejected():
    with pytest.raises(ValueError):
        delayed_history(np.arange(3), -1)
