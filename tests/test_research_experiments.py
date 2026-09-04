from iscai.simulation.research_benchmark import ResearchBenchmarkSettings
from iscai.simulation.research_experiments import build_experiment_specs, load_research_config


def test_all_experiment_families_have_unique_settings():
    config = load_research_config()
    base = ResearchBenchmarkSettings(mc_samples=2)
    for family in ("core", "horizon", "weight", "risk", "shift", "blackout", "compute"):
        specs = build_experiment_specs(family, config=config, base=base)
        assert specs
        keys = [(s.experiment, s.setting_id) for s in specs]
        assert len(keys) == len(set(keys))


def test_horizon_zero_is_represented_by_reactive_baseline_not_zero_step_horizon():
    specs = build_experiment_specs("horizon", base=ResearchBenchmarkSettings(mc_samples=2))
    assert all(spec.settings.horizon_steps >= 1 for spec in specs)
    assert all("P1" in spec.planners for spec in specs)


def test_blackout_matrix_contains_hidden_and_visible_conditions():
    specs = build_experiment_specs("blackout", base=ResearchBenchmarkSettings(mc_samples=2))
    visible = {spec.settings.blackout_visible_to_planner for spec in specs}
    assert visible == {False, True}
