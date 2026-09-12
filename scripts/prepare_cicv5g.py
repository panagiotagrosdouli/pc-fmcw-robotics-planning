#!/usr/bin/env python3
"""Download the public CICV5G W2S measurement subset with provenance.

The downloader discovers the current upstream W2S text files from the GitHub tree,
then downloads the raw files and records SHA256 hashes. Raw measurements are not
committed to this repository.
"""
from __future__ import annotations
import argparse, hashlib, json, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "zxr805/CICV5G"
TREE_API = f"https://api.github.com/repos/{REPO}/git/trees/main?recursive=1"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/"

def discover_upstream() -> list[str]:
    req = urllib.request.Request(TREE_API, headers={"User-Agent": "pc-fmcw-real-v2x-research"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    paths = [x["path"] for x in payload.get("tree", []) if x.get("type") == "blob" and x["path"].startswith("data/W2S/") and x["path"].endswith(".txt")]
    if not paths: raise RuntimeError("No CICV5G W2S text files discovered upstream")
    return sorted(paths)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="data/raw/cicv5g"); ap.add_argument("--limit",type=int,default=0,help="0 downloads all W2S text runs")
    args=ap.parse_args(); root=Path(args.output); root.mkdir(parents=True,exist_ok=True)
    paths=discover_upstream()
    if args.limit>0: paths=paths[:args.limit]
    records=[]
    for i,rel in enumerate(paths,1):
        dest=root/rel.replace("data/W2S/",""); dest.parent.mkdir(parents=True,exist_ok=True)
        url=RAW_BASE+urllib.parse.quote(rel,safe="/")
        if not dest.exists() or dest.stat().st_size==0: urllib.request.urlretrieve(url,dest)
        rec={"upstream_path":rel,"source_url":url,"local_file":str(dest),"bytes":dest.stat().st_size,"sha256":sha256(dest)}
        records.append(rec); print(f"[{i}/{len(paths)}] {dest} ({rec['bytes']} bytes)")
    manifest={"dataset":"CICV5G","upstream_repository":f"https://github.com/{REPO}","subset":"W2S","downloaded_at_utc":datetime.now(timezone.utc).isoformat(),"n_files":len(records),"files":records}
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps({"n_files":len(records),"manifest":str(root/'manifest.json')},indent=2))

if __name__=="__main__": main()
