import numpy as np

from iscai.connectivity.pc_fmcw_bridge import (
    PCFMCWPlanningLinkPredictor,
    PCFMCWReferenceParameters,
)


def _ego(x=0.0, y=0.0, yaw=0.0):
    return np.array([[x, y, yaw, 10.0]], dtype=float)


def test_reference_parameters_are_explicit_and_self_consistent():
    p = PCFMCWReferenceParameters()
    assert np.isclose(p.carrier_frequency_hz, 193.4e12)
    assert np.isclose(p.chirp_bandwidth_hz, 10e9)
    assert np.isclose(p.chirp_duration_s, 10e-6)
    assert np.isclose(p.data_rate_bps, 1e9)
    assert np.isclose(p.chirp_slope_hz_per_s, 1e15)
    assert np.isclose(p.symbol_duration_s, 1e-9)
    assert 1.5e-6 < p.wavelength_m < 1.6e-6


def test_range_and_pointing_geometry_change_forecast():
    predictor = PCFMCWPlanningLinkPredictor()
    near = predictor.predict(_ego(), np.array([[10.0, 0.0]]))
    far = predictor.predict(_ego(), np.array([[30.0, 0.0]]))
    off_axis = predictor.predict(_ego(), np.array([[10.0, 5.0]]))

    assert near.snr_db[0] > far.snr_db[0]
    assert near.snr_db[0] > off_axis.snr_db[0]
    assert near.outage_probability[0] < far.outage_probability[0]


def test_provenance_does_not_claim_unverified_traceability_or_measurements():
    provenance = PCFMCWPlanningLinkPredictor().provenance()
    assert provenance["reference_parameters_explicit"] is True
    assert provenance["upstream_parameter_provenance_verified"] is False
    assert provenance["optical_geometry_model"] == "simulation_assumption"
    assert provenance["measured_optical_link"] is False
    assert provenance["real_world_validation"] is False
