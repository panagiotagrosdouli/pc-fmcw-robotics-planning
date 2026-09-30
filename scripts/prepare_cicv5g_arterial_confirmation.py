#!/usr/bin/env python3
"""Download the frozen CICV5G arterial n8 50/80-km/h confirmation subset.

Only per-run raw files are downloaded. Aggregate all.txt files are excluded to avoid
duplicating measurements. Discovery is pinned to the exact upstream tree SHA returned
at runtime and a provenance manifest records every file hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "zxr805/CICV5G"
TREE_API = f"https://api.github.com/repos/{REPO}/git/trees/main?recursive=1"
PREFIXES = (
    "data/Arterial road/n8/v50/",
    "data/Arterial road/n8/50/",
    "data/Arterial road/n8/v80/",
    "data/Arterial road/n8/80/",
)


def github_headers() -> dict[str, str]:
    headers = {
        "User-Agent": "pc-fmcw-paper2-arterial-confirmation",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    return headers


def discover_upstream() -> tuple[str, list[str]]:
    req = urllib.request.Request(TREE_API, headers=github_headers())
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    tree_sha = str(payload.get("sha", ""))
    if not tree_sha:
        raise RuntimeError("CICV5G tree response did not include a tree SHA")
    paths = []
    for item in payload.get("tree", []):
        path = str(item.get("path", ""))
        if item.get("type") != "blob" or not path.endswith(".txt"):
            continue
        if path.endswith("/all.txt"):
            continue
        if any(path.startswith(prefix) for prefix in PREFIXES):
            paths.append(path)
    paths = sorted(paths)
    if not paths:
        raise RuntimeError("No arterial n8 50/80-km/h per-run files discovered")
    return tree_sha, paths


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download_atomic(url: str, dest: Path, attempts: int = 5) -> None:
    part = dest.with_suffix(dest.suffix + ".part")
    last_error = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers=github_headers())
            with urllib.request.urlopen(req, timeout=60) as response, part.open("wb") as out:
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    out.write(block)
            if part.stat().st_size == 0:
                raise RuntimeError(f"empty download: {url}")
            part.replace(dest)
            return
        except Exception as exc:
            last_error = exc
            part.unlink(missing_ok=True)
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to download {url}") from last_error


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/raw/cicv5g_arterial_confirmation")
    args = ap.parse_args()

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    tree_sha, paths = discover_upstream()

    records = []
    raw_base = f"https://raw.githubusercontent.com/{REPO}/{tree_sha}/"
    for i, rel in enumerate(paths, 1):
        local_name = rel.split("/")[-1]
        dest = root / local_name
        url = raw_base + urllib.parse.quote(rel, safe="/")
        if not dest.exists() or dest.stat().st_size == 0:
            download_atomic(url, dest)
        record = {
            "upstream_path": rel,
            "source_url": url,
            "local_file": str(dest),
            "bytes": dest.stat().st_size,
            "sha256": sha256(dest),
        }
        records.append(record)
        print(f"[{i}/{len(paths)}] {dest.name} ({record['bytes']} bytes)")

    speeds = {"50": 0, "80": 0}
    for rel in paths:
        if "_v50_" in rel:
            speeds["50"] += 1
        elif "_v80_" in rel:
            speeds["80"] += 1

    manifest = {
        "dataset": "CICV5G",
        "scenario": "arterial",
        "network": "n8",
        "speed_actions_kmh": [50, 80],
        "upstream_repository": f"https://github.com/{REPO}",
        "upstream_tree_sha": tree_sha,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "n_files": len(records),
        "run_counts_by_speed": speeds,
        "aggregate_files_excluded": True,
        "files": records,
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "n_files": len(records),
        "run_counts_by_speed": speeds,
        "manifest": str(root / "manifest.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
