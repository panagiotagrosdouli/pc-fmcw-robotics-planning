from pc_fmcw_robustness.counterfactual import matched_counterfactual_key


def test_counterfactual_key_is_stable():
    key = matched_counterfactual_key("lane_choice", 3)
    assert key.scenario == "lane_choice"
    assert key.seed == 3
