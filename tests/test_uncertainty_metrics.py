import numpy as np

from iscai.prediction.uncertainty_metrics import gaussian_coverage, gaussian_nll_numpy, sharpness


def test_gaussian_coverage_exact_cases():
    mean = np.zeros((2, 2))
    sigma = np.ones((2, 2))
    truth = np.array([[0.5, -0.5], [1.5, -1.5]])
    assert gaussian_coverage(mean, sigma, truth, 1.0) == 0.5
    assert gaussian_coverage(mean, sigma, truth, 2.0) == 1.0


def test_nll_prefers_accurate_mean():
    truth = np.zeros((4, 2))
    sigma = np.ones((4, 2))
    good = gaussian_nll_numpy(np.zeros((4, 2)), sigma, truth)
    bad = gaussian_nll_numpy(np.ones((4, 2)) * 3.0, sigma, truth)
    assert good < bad


def test_sharpness_is_mean_sigma():
    sigma = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert sharpness(sigma) == 2.5
