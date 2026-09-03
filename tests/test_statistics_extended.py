import numpy as np

from iscai.evaluation.statistics import holm_adjust, pareto_mask


def test_holm_adjust_monotone_and_bounded():
    p = np.array([0.01, 0.04, 0.03])
    q = holm_adjust(p)
    assert q.shape == p.shape
    assert np.all((q >= 0) & (q <= 1))
    assert q[0] <= q[1]


def test_pareto_mask_minimize_two_objectives():
    x = np.array([[1.0, 3.0], [2.0, 2.0], [3.0, 1.0], [3.0, 3.0]])
    mask = pareto_mask(x, minimize=[True, True])
    assert mask.tolist() == [True, True, True, False]


def test_pareto_mask_mixed_directions():
    x = np.array([[0.1, 10.0], [0.2, 12.0], [0.3, 8.0]])
    mask = pareto_mask(x, minimize=[True, False])
    assert mask.tolist() == [True, True, False]
