"""Run the reproducible dataset-free PC-FMCW robotics paper benchmark."""
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(cmd,log_path):
 log_path.parent.mkdir(parents=True,exist_ok=True)
 with log_path.open('w',encoding='utf-8') as f:proc=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,text=True)
 return proc.returncode
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,default=Path('configs/experiments/paper.yaml'));ap.add_argument('--dry-run',action='store_true');args=ap.parse_args();cfg=yaml.safe_load((ROOT/args.config).read_text());out=ROOT/cfg['outputs']['root'];out.mkdir(parents=True,exist_ok=True);s=cfg['simulation']
 cmd=[sys.executable,'scripts/run_pc_fmcw_robotics_benchmark.py','--seed-start',str(cfg['seed_start']),'--seeds',str(cfg['seeds']),'--output-dir',cfg['outputs']['root'],'--dt',str(s['dt_s']),'--history',str(s['history_steps']),'--horizon',str(s['horizon_steps']),'--observation-sigma-m',str(s['observation_sigma_m']),'--prediction-sigma-m',str(s['prediction_sigma_m']),'--connectivity-weight',str(s['connectivity_weight']),'--mc-samples',str(s['p3_mc_samples']),'--collision-distance-m',str(s['collision_distance_m'])]
 manifest={'experiment':cfg['name'],'started_utc':datetime.now(timezone.utc).isoformat(),'config':cfg,'scientific_status':{'external_dataset_required':False,'target_motion':'parameterized simulation','ego_motion':'receding-horizon simulation','connectivity':'PC-FMCW-informed simulation model; not measured optical link','real_world_validation':False},'runs':[]};item={'name':'pc_fmcw_robotics_benchmark','command':cmd}
 if args.dry_run:item['status']='dry_run'
 else:
  rc=run(cmd,out/'logs'/'benchmark.log');item.update(returncode=rc,status='ok' if rc==0 else 'failed')
 manifest['runs'].append(item);manifest['finished_utc']=datetime.now(timezone.utc).isoformat();(out/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest,indent=2))
 if item['status']=='failed':raise SystemExit('Dataset-free benchmark failed; inspect the recorded log.')
if __name__=='__main__':main()
