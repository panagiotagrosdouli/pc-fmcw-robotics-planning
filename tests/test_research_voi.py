from pc_fmcw_robustness.voi import INFORMATION_LEVELS, planner_information_order


def test_information_ladder_is_canonical():
    assert planner_information_order() == ("P1", "P2", "P3", "P4")
    assert INFORMATION_LEVELS[-1].deployable is False
