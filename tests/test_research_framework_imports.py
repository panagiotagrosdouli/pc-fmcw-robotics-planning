def test_research_extension_package_imports():
    import pc_fmcw_robustness

    assert callable(pc_fmcw_robustness.cvar)
    assert callable(pc_fmcw_robustness.chance_violation_probability)
    assert callable(pc_fmcw_robustness.adaptive_connectivity_weight)
