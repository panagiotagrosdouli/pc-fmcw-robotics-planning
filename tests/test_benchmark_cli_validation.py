from argparse import Namespace

import pytest

from scripts.run_pc_fmcw_robotics_benchmark import _validate_args


def _args(**overrides):
    values = dict(
        seeds=2,
        dt=0.1,
        history=8,
        horizon=20,
        observation_sigma_m=0.2,
        prediction_sigma_m=0.75,
        connectivity_weight=1.0,
        mc_samples=32,
        collision_distance_m=2.0,
    )
    values.update(overrides)
    return Namespace(**values)


def test_valid_benchmark_configuration_is_accepted():
    _validate_args(_args())


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("seeds", 0, "--seeds must be >= 1"),
        ("dt", 0.0, "--dt must be > 0"),
        ("history", 1, "--history must be >= 2"),
        ("horizon", 0, "--horizon must be >= 1"),
        ("observation_sigma_m", -0.1, "--observation-sigma-m must be >= 0"),
        ("prediction_sigma_m", -0.1, "--prediction-sigma-m must be >= 0"),
        ("connectivity_weight", -0.1, "--connectivity-weight must be >= 0"),
        ("mc_samples", 0, "--mc-samples must be >= 1"),
        ("collision_distance_m", -0.1, "--collision-distance-m must be >= 0"),
    ],
)
def test_invalid_benchmark_configuration_is_rejected(field, value, message):
    with pytest.raises(SystemExit, match=message):
        _validate_args(_args(**{field: value}))
