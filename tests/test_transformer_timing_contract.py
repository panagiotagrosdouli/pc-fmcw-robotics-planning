import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('closed_loop',Path(__file__).parents[1]/'scripts'/'run_cmht_closed_loop.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def test_frame_step_transformer_rejected_with_measured_timestamps():
    timing={'mode':'contiguous_frame_steps','uses_physical_timestamps':False}
    with pytest.raises(ValueError,match='frame-step based'):
        mod.validate_transformer_timing(timing,True)


def test_frame_step_transformer_allowed_in_fixed_step_replay():
    timing={'mode':'contiguous_frame_steps','uses_physical_timestamps':False}
    mod.validate_transformer_timing(timing,False)


def test_timestamp_aware_contract_allowed_with_measured_timestamps():
    timing={'mode':'timestamp_resampled','uses_physical_timestamps':True}
    mod.validate_transformer_timing(timing,True)
