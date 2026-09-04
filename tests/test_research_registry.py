from pc_fmcw_robustness.registry import RESEARCH_PLANNERS, planner_names


def test_research_planner_registry_contains_new_methods():
    names = planner_names()
    assert "predictive_cvar" in names
    assert "predictive_chance" in names
    assert "predictive_adaptive" in names
    assert next(p for p in RESEARCH_PLANNERS if p.name == "oracle").deployable is False
