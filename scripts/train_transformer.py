"""Train/evaluate uncertainty-aware Transformer on object-disjoint CMHT splits."""
import argparse,sys,json,random
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader,TensorDataset
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_dataset import make_windows
from iscai.prediction.transformer import TrajectoryTransformer,gaussian_nll

def tensors(samples):
 return torch.tensor(np.stack([s['history'] for s in samples]),dtype=torch.float32),torch.tensor(np.stack([s['future'] for s in samples]),dtype=torch.float32)

def evaluate(model,samples,batch=256):
 X,Y=tensors(samples); loader=DataLoader(TensorDataset(X,Y),batch_size=batch); nll=ade=fde=0.; n=0; model.eval()
 with torch.no_grad():
  for h,f in loader:
   target=f-h[:,-1:,:]; mean,logs=model(h); loss=gaussian_nll(mean,target,logs); err=torch.linalg.norm(mean-target,dim=-1); k=len(h); n+=k; nll+=float(loss)*k; ade+=float(err.mean())*k; fde+=float(err[:,-1].mean())*k
 return {'nll':nll/n,'ade_m':ade/n,'fde_m':fde/n,'windows':n}

def main():
 p=argparse.ArgumentParser(); p.add_argument('--labels',type=Path,required=True); p.add_argument('--history',type=int,default=8); p.add_argument('--horizon',type=int,default=12); p.add_argument('--epochs',type=int,default=50); p.add_argument('--patience',type=int,default=7); p.add_argument('--batch-size',type=int,default=128); p.add_argument('--lr',type=float,default=2e-4); p.add_argument('--seed',type=int,default=7); p.add_argument('--output',type=Path,default=Path('artifacts/trajectory_transformer.pt')); a=p.parse_args()
 random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
 samples=make_windows(extract_object_positions(a.labels),a.history,a.horizon); ids=np.array(sorted(set(s['object_id'] for s in samples)),dtype=object)
 if len(ids)<3: raise RuntimeError('Need at least three object IDs for train/validation/test')
 rng=np.random.default_rng(a.seed); rng.shuffle(ids); n=len(ids); ntrain=max(1,int(.7*n)); nval=max(1,int(.15*n)); ntrain=min(ntrain,n-2); nval=min(nval,n-ntrain-1)
 train_ids=set(ids[:ntrain]); val_ids=set(ids[ntrain:ntrain+nval]); test_ids=set(ids[ntrain+nval:]); train=[s for s in samples if s['object_id'] in train_ids]; val=[s for s in samples if s['object_id'] in val_ids]; test=[s for s in samples if s['object_id'] in test_ids]
 if not train or not val or not test: raise RuntimeError('One object-disjoint split has no windows')
 X,Y=tensors(train); loader=DataLoader(TensorDataset(X,Y),batch_size=a.batch_size,shuffle=True); model=TrajectoryTransformer(horizon=a.horizon); opt=torch.optim.AdamW(model.parameters(),lr=a.lr,weight_decay=1e-4); best=float('inf'); best_state=None; stale=0
 for epoch in range(a.epochs):
  model.train(); total=0.
  for h,f in loader:
   target=f-h[:,-1:,:]; mean,logs=model(h); loss=gaussian_nll(mean,target,logs); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.); opt.step(); total+=float(loss)*len(h)
  vm=evaluate(model,val,a.batch_size); print(f"epoch={epoch+1:03d} train_nll={total/len(train):.6f} val_nll={vm['nll']:.6f} val_fde_m={vm['fde_m']:.4f}")
  if vm['nll']<best-1e-6: best=vm['nll']; best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}; stale=0
  else:
   stale+=1
   if stale>=a.patience: break
 model.load_state_dict(best_state); val_metrics=evaluate(model,val,a.batch_size); test_metrics=evaluate(model,test,a.batch_size); a.output.parent.mkdir(parents=True,exist_ok=True)
 split={'seed':a.seed,'train_ids':[str(x) for x in sorted(train_ids,key=str)],'validation_ids':[str(x) for x in sorted(val_ids,key=str)],'test_ids':[str(x) for x in sorted(test_ids,key=str)]}
 torch.save({'state_dict':model.state_dict(),'history':a.history,'horizon':a.horizon,'translation_normalized':True,'split':split,'validation_metrics':val_metrics,'test_metrics':test_metrics},a.output)
 report={'checkpoint':str(a.output),'split':split,'train_windows':len(train),'validation':val_metrics,'test':test_metrics}; a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
if __name__=='__main__':main()
