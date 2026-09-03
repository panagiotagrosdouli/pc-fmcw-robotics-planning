"""Train, validation-calibrate, and test a probabilistic CMHT Transformer.

The current Transformer is frame-step based: training windows are contiguous
annotation frames and do not consume physical timestamps. The checkpoint stores
this timing contract so replay code can refuse scientifically ambiguous use.
"""
import argparse,sys,json,random
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader,TensorDataset
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_dataset import make_windows
from iscai.prediction.transformer import TrajectoryTransformer,gaussian_nll
from iscai.prediction.uncertainty_metrics import optimal_sigma_scale,gaussian_nll_numpy,gaussian_coverage,sharpness

def tensors(s):return torch.tensor(np.stack([x['history'] for x in s]),dtype=torch.float32),torch.tensor(np.stack([x['future'] for x in s]),dtype=torch.float32)
def predictions(model,samples,batch=256):
 X,Y=tensors(samples);means=[];sigmas=[];truth=[];model.eval()
 with torch.no_grad():
  for h,f in DataLoader(TensorDataset(X,Y),batch_size=batch):
   m,l=model(h);means.append(m.numpy());sigmas.append(torch.exp(l).numpy());truth.append((f-h[:,-1:,:]).numpy())
 return np.concatenate(means),np.concatenate(sigmas),np.concatenate(truth)
def metrics(model,samples,batch=256,sigma_scale=1.):
 m,s,y=predictions(model,samples,batch);s=s*sigma_scale;e=np.linalg.norm(m-y,axis=-1)
 return {'nll':gaussian_nll_numpy(m,s,y),'ade_m':float(e.mean()),'fde_m':float(e[:,-1].mean()),'coverage_1sigma':gaussian_coverage(m,s,y,1.),'coverage_2sigma':gaussian_coverage(m,s,y,2.),'sharpness_m':sharpness(s),'windows':len(samples)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--labels',type=Path,required=True);p.add_argument('--history',type=int,default=8);p.add_argument('--horizon',type=int,default=12);p.add_argument('--epochs',type=int,default=50);p.add_argument('--patience',type=int,default=7);p.add_argument('--batch-size',type=int,default=128);p.add_argument('--lr',type=float,default=2e-4);p.add_argument('--seed',type=int,default=7);p.add_argument('--output',type=Path,default=Path('artifacts/trajectory_transformer.pt'));a=p.parse_args();random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
 samples=make_windows(extract_object_positions(a.labels),a.history,a.horizon);ids=np.array(sorted(set(s['object_id'] for s in samples)),dtype=object)
 if len(ids)<3:raise RuntimeError('Need at least three object IDs for train/validation/test')
 rng=np.random.default_rng(a.seed);rng.shuffle(ids);n=len(ids);nt=max(1,int(.7*n));nv=max(1,int(.15*n));nt=min(nt,n-2);nv=min(nv,n-nt-1);ti=set(ids[:nt]);vi=set(ids[nt:nt+nv]);qi=set(ids[nt+nv:]);train=[s for s in samples if s['object_id'] in ti];val=[s for s in samples if s['object_id'] in vi];test=[s for s in samples if s['object_id'] in qi]
 if not train or not val or not test:raise RuntimeError('One object-disjoint split has no windows')
 X,Y=tensors(train);loader=DataLoader(TensorDataset(X,Y),batch_size=a.batch_size,shuffle=True);model=TrajectoryTransformer(horizon=a.horizon);opt=torch.optim.AdamW(model.parameters(),lr=a.lr,weight_decay=1e-4);best=float('inf');state=None;stale=0
 for ep in range(a.epochs):
  model.train();total=0.
  for h,f in loader:
   y=f-h[:,-1:,:];m,l=model(h);loss=gaussian_nll(m,y,l);opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();total+=float(loss)*len(h)
  vm=metrics(model,val,a.batch_size);print(f"epoch={ep+1:03d} train_nll={total/len(train):.6f} val_nll={vm['nll']:.6f} val_fde_m={vm['fde_m']:.4f}")
  if vm['nll']<best-1e-6:best=vm['nll'];state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};stale=0
  else:
   stale+=1
   if stale>=a.patience:break
 model.load_state_dict(state);vm,vs,vy=predictions(model,val,a.batch_size);scale=optimal_sigma_scale(vm,vs,vy);val_raw=metrics(model,val,a.batch_size);val_cal=metrics(model,val,a.batch_size,scale);test_raw=metrics(model,test,a.batch_size);test_cal=metrics(model,test,a.batch_size,scale);a.output.parent.mkdir(parents=True,exist_ok=True);split={'seed':a.seed,'train_ids':list(map(str,sorted(ti,key=str))),'validation_ids':list(map(str,sorted(vi,key=str))),'test_ids':list(map(str,sorted(qi,key=str)))};payload={'state_dict':model.state_dict(),'history':a.history,'horizon':a.horizon,'translation_normalized':True,'timing':{'mode':'contiguous_frame_steps','uses_physical_timestamps':False},'sigma_calibration':{'method':'global_validation_nll_mle','scale':scale,'fit_split':'validation'},'split':split,'validation_raw':val_raw,'validation_calibrated':val_cal,'test_raw':test_raw,'test_calibrated':test_cal};torch.save(payload,a.output);report={k:v for k,v in payload.items() if k!='state_dict'};report['checkpoint']=str(a.output);report['train_windows']=len(train);a.output.with_suffix('.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
