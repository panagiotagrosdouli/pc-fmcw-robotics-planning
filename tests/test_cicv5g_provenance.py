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
