#!/usr/bin/env python3
"""Run the publication experiment matrix with matched planner/scenario seeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from iscai.simulation.research_experiments import build_experiment_specs, load_research_config, run_experiment_specs


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',default='all',choices=['core','horizon','weight','risk','shift','blackout','compute','all'])
    p.add_argument('--seeds',type=int,default=None,help='number of matched integer seeds starting at zero')
    p.add_argument('--config',default='configs/research_framework.yaml')
    p.add_argument('--output-dir',default='results/publication_study')
    p.add_argument('--no-traces',action='store_true')
    return p.parse_args()


def main():
    args=parse_args(); cfg=load_research_config(args.config)
    n=int(cfg['benchmark']['seeds'] if args.seeds is None else args.seeds)
    if n<1: raise SystemExit('--seeds must be >= 1')
    specs=build_experiment_specs(args.mode,cfg)
    episodes,traces,manifests=run_experiment_specs(specs,range(n))
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(episodes).to_csv(out/'episodes.csv',index=False)
    if not args.no_traces: pd.DataFrame(traces).to_csv(out/'traces.csv',index=False)
    manifest={'protocol_version':cfg['protocol_version'],'mode':args.mode,'seeds':list(range(n)),'config':cfg,'experiments':manifests,'claim_boundary':'controlled PC-FMCW-informed simulation; not measured optical-link or real-road validation'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True))
    print(f'wrote {len(episodes)} matched episode rows to {out}')

if __name__=='__main__': main()
