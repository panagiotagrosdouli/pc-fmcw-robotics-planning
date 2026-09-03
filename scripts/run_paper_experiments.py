"""Run the reproducible dataset-free PC-FMCW robotics paper benchmark.

No external dataset is required. The manifest records the claim boundary:
waveform parameters are traced to the upstream PC-FMCW notebook, while target
motion, ego motion and geometry-conditioned link behavior are simulated.
"""
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]

def run(cmd,log_path):
    log_path.parent.mkdir(parents=True,exist_ok=True)
    with log_path.open('w',encoding='utf-8') as f:
        proc=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,text=True)
    return proc.returncode

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,default=Path('configs/experiments/paper.yaml'));ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    cfg=yaml.safe_load((ROOT/args.config).read_text());out=ROOT/cfg['outputs']['root'];out.mkdir(parents=True,exist_ok=True);sim=cfg['simulation']
    cmd=[sys.executable,'scripts/run_pc_fmcw_robotics_benchmark.py','--seeds',str(cfg['seeds']),'--mc-samples',str(sim['p3_mc_samples']),'--output-dir',str(Path(cfg['outputs']['root']))]
    manifest={'experiment':cfg['name'],'started_utc':datetime.now(timezone.utc).isoformat(),'config':cfg,'scientific_status':{'external_dataset_required':False,'target_motion':'parameterized simulation','ego_motion':'receding-horizon simulation','connectivity':'PC-FMCW-informed simulation model; not measured optical link','real_world_validation':False},'runs':[]}
    item={'name':'pc_fmcw_robotics_benchmark','command':cmd}
    if args.dry_run:item['status']='dry_run'
    else:
        rc=run(cmd,out/'logs'/'benchmark.log');item.update(returncode=rc,status='ok' if rc==0 else 'failed')
    manifest['runs'].append(item);manifest['finished_utc']=datetime.now(timezone.utc).isoformat();(out/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest,indent=2))
    if item['status']=='failed':raise SystemExit('Dataset-free benchmark failed; inspect the recorded log.')
if __name__=='__main__':main()
