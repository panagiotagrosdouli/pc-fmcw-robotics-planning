from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import prepare_cicv5g


def test_discovery_returns_pinnable_tree_sha(monkeypatch):
    payload = {
        "sha": "a" * 40,
        "tree": [
            {"type": "blob", "path": "data/W2S/run_b.txt"},
            {"type": "blob", "path": "data/W2S/run_a.txt"},
            {"type": "blob", "path": "data/other.txt"},
        ],
    }

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(prepare_cicv5g.urllib.request, "urlopen", lambda *a, **k: Response())
    monkeypatch.setattr(prepare_cicv5g.json, "load", lambda response: payload)

    sha, paths = prepare_cicv5g.discover_upstream()
    assert sha == "a" * 40
    assert paths == ["data/W2S/run_a.txt", "data/W2S/run_b.txt"]


def test_atomic_download_retries_without_accepting_partial_file(tmp_path, monkeypatch):
    attempts = {"count": 0}

    class Response:
        def __init__(self, fail):
            self.fail = fail
            self.reads = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size):
            self.reads += 1
            if self.fail and self.reads == 2:
                raise ConnectionResetError("transient")
            return b"partial" if self.reads == 1 else b""

    def open_response(*args, **kwargs):
        attempts["count"] += 1
        return Response(fail=attempts["count"] == 1)

    monkeypatch.setattr(prepare_cicv5g.urllib.request, "urlopen", open_response)
    monkeypatch.setattr(prepare_cicv5g.time, "sleep", lambda seconds: None)
    dest = tmp_path / "measurement.txt"
    prepare_cicv5g.download_atomic("https://example.invalid/measurement", dest)

    assert attempts["count"] == 2
    assert dest.read_bytes() == b"partial"
    assert not (tmp_path / "measurement.txt.part").exists()
