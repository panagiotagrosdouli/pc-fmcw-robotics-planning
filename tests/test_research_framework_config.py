from pathlib import Path

import yaml


def test_research_framework_config_has_declared_method_families():
    config = yaml.safe_load(Path("configs/research_framework.yaml").read_text())

    assert config["protocol_version"] == "research-framework-v1"
    assert config["risk_aware"]["enabled"] is True
    assert config["chance_constraints"]["enabled"] is True
    assert config["adaptive_weight"]["enabled"] is True
    assert 0.0 in config["prediction_horizon_s"]
    assert 5.0 in config["prediction_horizon_s"]
    assert "sudden_blockage" in config["blackout_scenarios"]
    assert "rapid_degradation" in config["blackout_scenarios"]


def test_research_framework_config_keeps_safety_separate():
    config = yaml.safe_load(Path("configs/research_framework.yaml").read_text())
    assert config["reporting"]["separate_safety_claims"] is True
    assert config["reporting"]["retain_negative_results"] is True
