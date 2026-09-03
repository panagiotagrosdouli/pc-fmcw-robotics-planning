import math
import pytest

from iscai.simulation.pc_fmcw_benchmark import BenchmarkSettings


def test_default_benchmark_settings_are_valid():
    settings = BenchmarkSettings()
    assert settings.dt > 0.0
    assert settings.history_steps >= 2
    assert settings.horizon_steps >= 1
    assert settings.p3_mc_samples >= 1
    assert settings.collision_distance_m >= 0.0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("dt", 0.0, "dt must be positive and finite"),
        ("dt", math.inf, "dt must be positive and finite"),
        ("history_steps", 1, "history_steps must be >= 2"),
        ("horizon_steps", 0, "horizon_steps must be >= 1"),
        ("observation_sigma_m", -0.1, "observation_sigma_m must be non-negative and finite"),
        ("observation_sigma_m", math.nan, "observation_sigma_m must be non-negative and finite"),
        ("prediction_sigma_m", -0.1, "prediction_sigma_m must be non-negative and finite"),
        ("prediction_sigma_m", math.inf, "prediction_sigma_m must be non-negative and finite"),
        ("connectivity_weight", -0.1, "connectivity_weight must be non-negative and finite"),
        ("connectivity_weight", math.nan, "connectivity_weight must be non-negative and finite"),
        ("p3_mc_samples", 0, "p3_mc_samples must be >= 1"),
        ("collision_distance_m", -0.1, "collision_distance_m must be non-negative and finite"),
        ("collision_distance_m", math.inf, "collision_distance_m must be non-negative and finite"),
    ],
)
def test_invalid_benchmark_settings_are_rejected(field, value, message):
    with pytest.raises(ValueError, match=message):
        BenchmarkSettings(**{field: value})


def test_zero_uncertainty_weight_and_clearance_are_allowed():
    settings = BenchmarkSettings(
        observation_sigma_m=0.0,
        prediction_sigma_m=0.0,
        connectivity_weight=0.0,
        collision_distance_m=0.0,
    )
    assert settings.observation_sigma_m == 0.0
    assert settings.prediction_sigma_m == 0.0
    assert settings.connectivity_weight == 0.0
    assert settings.collision_distance_m == 0.0
