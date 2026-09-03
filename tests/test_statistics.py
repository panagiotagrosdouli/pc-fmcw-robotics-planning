import numpy as np

from iscai.evaluation.statistics import paired_bootstrap_delta, paired_wilcoxon


def test_paired_bootstrap_detects_positive_delta():
    a = np.array([1.0, 1.2, 0.8, 1.1, 0.9])
    b = a + 0.5
    out = paired_bootstrap_delta(a, b, samples=2000, rng=3)
    assert np.isclose(out["mean_delta"], 0.5)
    assert out["ci_low"] > 0.0


def test_wilcoxon_all_zero_difference():
    a = np.array([1.0, 2.0, 3.0])
    out = paired_wilcoxon(a, a.copy())
    assert out["pvalue"] == 1.0
