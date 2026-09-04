import numpy as np
import pytest

from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor
from iscai.connectivity.stress import (
    LinkStressProfile,
    ReactiveTimeIndexedStressedLinkPredictor,
    TimeIndexedStressedLinkPredictor,
    make_mismatched_pc_fmcw_predictor,
)


def test_sudden_blockage_is_time_indexed():
    profile = LinkStressProfile(kind="sudden_blockage", attenuation_db=10.0, start_fraction=0.5)
    attenuation = profile.attenuation(np.arange(6), episode_steps=6)
    assert attenuation[:2].tolist() == [0.0, 0.0]
    assert attenuation[-3:].tolist() == [10.0, 10.0, 10.0]


def test_stressed_predictor_reduces_future_snr():
    base = PCFMCWPlanningLinkPredictor()
    stress = TimeIndexedStressedLinkPredictor(
        base,
        LinkStressProfile(kind="persistent_nlos", attenuation_db=5.0),
        episode_steps=10,
    )
    ego = np.tile(np.array([0.0, 0.0, 0.0, 10.0]), (3, 1))
    target = np.tile(np.array([10.0, 0.0, 0.0, 6.0]), (3, 1))
    nominal = base.predict(ego, target)
    degraded = stress.predict(ego, target)
    assert np.allclose(degraded.snr_db, nominal.snr_db - 5.0)
    assert np.all(degraded.outage_probability >= nominal.outage_probability)


def test_reactive_stress_does_not_leak_future_blackout_schedule():
    base = PCFMCWPlanningLinkPredictor()
    profile = LinkStressProfile(kind="sudden_blockage", attenuation_db=12.0, start_fraction=0.5)
    predictive = TimeIndexedStressedLinkPredictor(base, profile, episode_steps=10)
    reactive = ReactiveTimeIndexedStressedLinkPredictor(base, profile, episode_steps=10)
    predictive.set_step(2)
    reactive.set_step(2)
    ego = np.tile(np.array([0.0, 0.0, 0.0, 10.0]), (6, 1))
    target = np.tile(np.array([10.0, 0.0, 0.0, 6.0]), (6, 1))
    nominal = base.predict(ego, target)
    predictive_forecast = predictive.predict(ego, target)
    reactive_forecast = reactive.predict(ego, target)
    assert np.allclose(reactive_forecast.snr_db, nominal.snr_db)
    assert np.any(predictive_forecast.snr_db < nominal.snr_db)


def test_mismatched_predictor_changes_only_planning_model():
    base = PCFMCWPlanningLinkPredictor()
    mismatched = make_mismatched_pc_fmcw_predictor(base, pathloss_scale=1.5)
    assert mismatched.geometry.pathloss_exponent == pytest.approx(base.geometry.pathloss_exponent * 1.5)
    assert base.geometry.pathloss_exponent == pytest.approx(2.0)
