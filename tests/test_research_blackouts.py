import numpy as np

from pc_fmcw_robustness.blackouts import apply_snr_blackout, blackout_mask


def test_sudden_blockage_activates_second_half():
    mask = blackout_mask("sudden_blockage", 6)
    assert mask.tolist() == [False, False, False, True, True, True]


def test_persistent_nlos_degrades_all_samples():
    snr = np.array([20.0, 15.0, 10.0])
    degraded = apply_snr_blackout(snr, "persistent_nlos", attenuation_db=5.0)
    assert np.allclose(degraded, [15.0, 10.0, 5.0])
