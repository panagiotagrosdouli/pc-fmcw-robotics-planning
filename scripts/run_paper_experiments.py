"""Run the reproducible Stage-9 paper experiment suite from one manifest.

The orchestrator never fabricates missing data or calibration artifacts. It
records commands, status and scientific provenance. Closed-loop CMHT replay is
hybrid data-driven simulation: measured target motion, simulated ego motion and
modeled connectivity; it is not a real vehicle trial.
"""
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
def optional_path(value):return None if not value else ROOT/value
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,default=Path('configs/experiments/paper.yaml'));ap.add_argument('--dry-run',action='store_true');args=ap.parse_args();cfg=yaml.safe_load((ROOT/args.config).read_text());out=ROOT/cfg['outputs']['root'];out.mkdir(parents=True,exist_ok=True);cmht=cfg['cmht'];labels=ROOT/cmht['labels'];timestamps=optional_path(cmht.get('timestamps'));commands=[]
 horizons=[str(x) for x in cmht['horizons_s']];commands.append(('real_horizon_sweep',[sys.executable,'scripts/run_real_horizon_sweep.py','--labels',str(labels),'--history-s',str(cmht['history']*cmht['dt']),'--dt',str(cmht['dt']),'--horizons',*horizons,'--output-dir',str(out/'trajectory_horizon')]))
 pr=cfg['planner_replay'];pr_cal=optional_path(pr.get('link_calibration'));replay=[sys.executable,'scripts/run_cmht_planner_replay.py','--labels',str(labels),'--history',str(cmht['history']),'--horizon',str(pr['horizon_steps']),'--dt',str(cmht['dt']),'--sigma-m',str(pr['sigma_m']),'--max-windows',str(cmht['max_windows']),'--output',str(out/'planner_replay.csv')]
 if pr_cal:replay += ['--link-calibration',str(pr_cal)]
 commands.append(('planner_replay',replay));cl=cfg.get('closed_loop',{});cl_cal=optional_path(cl.get('link_calibration'));tf=optional_path(cl.get('transformer_checkpoint'))
 if cl.get('enabled',False):
  cmd=[sys.executable,'scripts/run_cmht_closed_loop.py','--labels',str(labels),'--history',str(cmht['history']),'--horizon',str(cl['horizon_steps']),'--dt',str(cmht['dt']),'--sigma-m',str(cl['sigma_m']),'--max-tracks',str(cmht['max_tracks']),'--output',str(out/'closed_loop.csv')]
  if timestamps:cmd += ['--timestamps',str(timestamps),'--frame-start',str(cmht.get('frame_start',0))]
  if cl_cal:cmd += ['--link-calibration',str(cl_cal)]
  if tf:cmd += ['--transformer-checkpoint',str(tf)]
  commands.append(('closed_loop',cmd))
 required={'cmht_labels':labels,'cmht_timestamps':timestamps,'planner_link_calibration':pr_cal,'closed_loop_link_calibration':cl_cal,'transformer_checkpoint':tf};manifest={'experiment':cfg['name'],'started_utc':datetime.now(timezone.utc).isoformat(),'config':cfg,'scientific_status':{'cmht_target_motion':'measured annotations','ego_motion':'simulated','connectivity':'modeled unless frozen calibration provenance says otherwise','closed_loop':'hybrid data-driven simulation, not real vehicle trial'},'inputs':{k:None if v is None else {'path':str(v),'exists':v.exists()} for k,v in required.items()},'runs':[]}
 if not args.dry_run:
  missing=[f'{k}: {v}' for k,v in required.items() if v is not None and not v.exists()]
  if missing:raise SystemExit('Required experiment inputs missing; no results generated:\n'+'\n'.join(missing))
 for name,cmd in commands:
  item={'name':name,'command':cmd}
  if args.dry_run:item['status']='dry_run'
  else:
   rc=run(cmd,out/'logs'/f'{name}.log');item['returncode']=rc;item['status']='ok' if rc==0 else 'failed'
  manifest['runs'].append(item)
  if item['status']=='failed':break
 manifest['finished_utc']=datetime.now(timezone.utc).isoformat();(out/'run_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
