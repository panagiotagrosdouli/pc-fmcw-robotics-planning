from pc_fmcw_robustness.pareto import pareto_efficient


def test_pareto_efficiency_for_minimization():
    points = [(1.0, 3.0), (2.0, 2.0), (3.0, 1.0), (3.0, 3.0)]
    assert pareto_efficient(points) == [True, True, True, False]
