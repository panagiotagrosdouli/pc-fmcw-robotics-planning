"""Compact Transformer trajectory forecaster with Gaussian uncertainty."""
from __future__ import annotations
import math
import torch
from torch import nn

class SinusoidalPE(nn.Module):
    def __init__(self,d_model:int,max_len:int=512):
        super().__init__(); pos=torch.arange(max_len,dtype=torch.float32).unsqueeze(1); div=torch.exp(torch.arange(0,d_model,2,dtype=torch.float32)*(-math.log(10000.0)/d_model)); pe=torch.zeros(max_len,d_model); pe[:,0::2]=torch.sin(pos*div); pe[:,1::2]=torch.cos(pos*div); self.register_buffer('pe',pe.unsqueeze(0))
    def forward(self,x): return x+self.pe[:,:x.size(1)]

class TrajectoryTransformer(nn.Module):
    """Translation-invariant history -> future displacement Gaussian parameters.

    Histories are internally centered on the last observed XY point. The model
    therefore cannot exploit arbitrary global-map translation as a shortcut;
    returned means remain future displacements relative to the last observation.
    """
    def __init__(self,d_model=128,nhead=4,layers=3,horizon=12):
        super().__init__(); self.horizon=horizon; self.in_proj=nn.Linear(2,d_model); self.pe=SinusoidalPE(d_model); enc=nn.TransformerEncoderLayer(d_model,nhead,dim_feedforward=4*d_model,batch_first=True,norm_first=True); self.encoder=nn.TransformerEncoder(enc,layers); self.head=nn.Sequential(nn.LayerNorm(d_model),nn.Linear(d_model,horizon*4))
    def forward(self,history):
        if history.ndim!=3 or history.shape[-1]!=2: raise ValueError('history must have shape (B,H,2)')
        relative=history-history[:,-1:,:]
        h=self.encoder(self.pe(self.in_proj(relative)))[:,-1]; out=self.head(h).view(-1,self.horizon,4); mean=out[...,:2]; log_sigma=torch.clamp(out[...,2:],-5.,3.); return mean,log_sigma

def gaussian_nll(pred_delta,target_delta,log_sigma):
    var=torch.exp(2.*log_sigma); return (log_sigma+.5*(target_delta-pred_delta).pow(2)/var).mean()
