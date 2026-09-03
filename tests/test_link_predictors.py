import json
from pathlib import Path

import numpy as np

from iscai.connectivity.calibrated_predictor import CalibratedGeometryLinkPredictor
from iscai.prediction.link_predictor import LinkPredictor
from iscai.planning.trajectory import CandidateTrajectory


def _candidate():
    states = np.array([
        [0.0, 0.0, 0.0, 5.0],
        [1.0, 0.0, 0.0, 5.0],
        [2.0, 0.0, 0.0, 5.0],
    ])
    controls = np.zeros((2, 2))
    return CandidateTrajectory(states, controls, 0.2, 0.0, 5.0)


def _target():
    out = np.zeros((3, 4))
    out[:, 0] = [10.0, 11.0, 12.0]
    return out


def _assert_forecast_contract(f):
    assert f.snr_db.shape == (3,)
    assert f.ber.shape == (3,)
    assert f.outage_probability.shape == (3,)
    assert f.goodput.shape == (3,)
    assert np.isfinite(f.snr_db).all()
    assert 0.0 <= float(f.survival_probability) <= 1.0


def test_default_and_calibrated_predictors_share_contract(tmp_path: Path):
    default = LinkPredictor(reference_snr_db=20.0, reference_distance=10.0, min_snr_db=8.0)
    _assert_forecast_contract(default.predict(_candidate(), _target()))

    cfg = {
        "metadata": {
            "source": "unit-test synthetic calibration",
            "measurement_type": "synthetic-test-only",
            "calibration_date": "2026-09-03",
        },
        "parameters": {
            "reference_snr_db": 30.0,
            "pathloss_exponent": 2.0,
            "beam_sigma_rad": 0.2,
            "outage_threshold_db": 8.0,
            "ber_slope": 1.0,
        },
    }
    p = tmp_path / "calibration.json"
    p.write_text(json.dumps(cfg))
    calibrated = CalibratedGeometryLinkPredictor.from_json(p)
    _assert_forecast_contract(calibrated.predict(_candidate(), _target()))


def test_calibrated_predictor_requires_provenance():
    try:
        CalibratedGeometryLinkPredictor(
            {}, reference_snr_db=30.0, pathloss_exponent=2.0, beam_sigma_rad=0.2
        )
    except ValueError as exc:
        assert "provenance" in str(exc).lower()
    else:
        raise AssertionError("missing provenance must be rejected")
