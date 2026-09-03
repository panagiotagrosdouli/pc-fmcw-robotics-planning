import numpy as np
import pytest
from iscai.data.cmht_loader import timestamp_map


def test_timestamp_map_with_explicit_frames(tmp_path):
    p=tmp_path/'timestamps.txt';p.write_text('10.0\n10.05\n10.11\n')
    out=timestamp_map(p,frames=[100,101,102])
    assert out=={100:10.0,101:10.05,102:10.11}


def test_timestamp_map_rejects_nonmonotonic_time(tmp_path):
    p=tmp_path/'timestamps.txt';p.write_text('1.0\n0.9\n')
    with pytest.raises(ValueError,match='strictly increasing'):
        timestamp_map(p)


def test_timestamp_map_rejects_alignment_length_mismatch(tmp_path):
    p=tmp_path/'timestamps.txt';p.write_text('1.0\n1.1\n')
    with pytest.raises(ValueError,match='identical length'):
        timestamp_map(p,frames=[5])
