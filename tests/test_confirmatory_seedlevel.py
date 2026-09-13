from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location(
    "confirmatory_seedlevel", ROOT / "scripts" / "analyze_pc_fmcw_confirmatory_seedlevel.py"
)
MOD = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_seed_effects_aggregate_scenarios_before_inference():
    rows = []
    # Seed 1 has scenario deltas +1 and +3 -> seed effect +2.
    # Seed 2 has scenario deltas -2 and +2 -> seed effect 0.
    for seed, deltas in [(1, (1.0, 3.0)), (2, (-2.0, 2.0))]:
        for scenario, delta in zip(("a", "b"), deltas):
            rows.append({"planner": "P1", "scenario": scenario, "seed": seed, "metric": 10.0})
            rows.append({"planner": "P2", "scenario": scenario, "seed": seed, "metric": 10.0 + delta})
    df = pd.DataFrame(rows)
    effects = MOD.seed_effects(df, "P1", "P2", "metric")
    assert effects.index.tolist() == [1, 2]
    assert np.allclose(effects.seed_delta.to_numpy(float), [2.0, 0.0])
    assert effects.n_scenarios.tolist() == [2, 2]


def test_seed_effects_reject_unequal_scenario_coverage():
    df = pd.DataFrame([
        {"planner": "P1", "scenario": "a", "seed": 1, "metric": 1.0},
        {"planner": "P2", "scenario": "a", "seed": 1, "metric": 2.0},
        {"planner": "P1", "scenario": "a", "seed": 2, "metric": 1.0},
        {"planner": "P2", "scenario": "a", "seed": 2, "metric": 2.0},
        {"planner": "P1", "scenario": "b", "seed": 2, "metric": 1.0},
        {"planner": "P2", "scenario": "b", "seed": 2, "metric": 2.0},
    ])
    try:
        MOD.seed_effects(df, "P1", "P2", "metric")
    except ValueError as exc:
        assert "unequal scenario coverage" in str(exc)
    else:
        raise AssertionError("unequal within-seed scenario coverage must be rejected")


def test_holm_adjust_is_monotone_and_not_smaller_than_raw_p():
    # Imported by the confirmatory analyzer and used separately within each
    # five-endpoint planner-comparison family.
    raw = np.asarray([0.001, 0.01, 0.03, 0.2, 0.8])
    adjusted = MOD.holm_adjust(raw)
    assert adjusted.shape == raw.shape
    assert np.all(adjusted >= raw - 1e-15)
    order = np.argsort(raw)
    assert np.all(np.diff(adjusted[order]) >= -1e-15)
    assert np.all((0.0 <= adjusted) & (adjusted <= 1.0))


def test_all_zero_wilcoxon_is_well_defined():
    assert MOD.signed_wilcoxon(np.zeros(10)) == 1.0
