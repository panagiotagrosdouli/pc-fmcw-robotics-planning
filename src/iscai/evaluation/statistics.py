"""Paired statistical utilities for experiment reporting."""
from __future__ import annotations
import numpy as np
from scipy.stats import wilcoxon

def paired_bootstrap_delta(a,b,*,samples=10000,confidence=.95,rng=0):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=1: raise ValueError('a and b must be paired 1D arrays with identical shape')
    if len(a)==0: raise ValueError('empty paired arrays')
    d=b-a; gen=np.random.default_rng(rng); idx=gen.integers(0,len(d),size=(samples,len(d))); boot=d[idx].mean(axis=1); alpha=1-confidence
    return {'mean_delta':float(d.mean()),'ci_low':float(np.quantile(boot,alpha/2)),'ci_high':float(np.quantile(boot,1-alpha/2))}

def cluster_paired_bootstrap_delta(a,b,clusters,*,samples=10000,confidence=.95,rng=0):
    """Paired bootstrap of b-a resampling independent clusters, not rows.

    Each bootstrap draw samples cluster IDs with replacement and includes every
    paired observation belonging to the sampled cluster. This avoids treating
    overlapping windows/decisions from one CMHT track as independent units.
    """
    a=np.asarray(a,float); b=np.asarray(b,float); c=np.asarray(clusters)
    if a.shape!=b.shape or a.ndim!=1 or c.shape!=a.shape: raise ValueError('a, b, and clusters must be paired 1D arrays')
    if len(a)==0: raise ValueError('empty paired arrays')
    d=b-a; ids=np.unique(c); gen=np.random.default_rng(rng); boot=np.empty(samples,float)
    groups={k:d[c==k] for k in ids}
    for s in range(samples):
        chosen=gen.choice(ids,size=len(ids),replace=True); boot[s]=np.concatenate([groups[k] for k in chosen]).mean()
    alpha=1-confidence
    return {'mean_delta':float(d.mean()),'ci_low':float(np.quantile(boot,alpha/2)),'ci_high':float(np.quantile(boot,1-alpha/2)),'n_clusters':int(len(ids))}

def paired_wilcoxon(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=1: raise ValueError('a and b must be paired 1D arrays with identical shape')
    d=b-a
    if np.allclose(d,0.): return {'statistic':0.,'pvalue':1.}
    r=wilcoxon(a,b,alternative='two-sided',zero_method='wilcox'); return {'statistic':float(r.statistic),'pvalue':float(r.pvalue)}

def holm_adjust(pvalues):
    p=np.asarray(pvalues,float)
    if p.ndim!=1: raise ValueError('pvalues must be one-dimensional')
    if np.any((p<0)|(p>1)): raise ValueError('pvalues must lie in [0, 1]')
    m=len(p)
    if not m:return p.copy()
    order=np.argsort(p); ranked=p[order]; ar=np.maximum.accumulate((m-np.arange(m))*ranked); ar=np.clip(ar,0.,1.); out=np.empty_like(ar); out[order]=ar; return out

def pareto_mask(values,minimize=None):
    x=np.asarray(values,float)
    if x.ndim!=2: raise ValueError('values must have shape (N, D)')
    if minimize is None:minimize=np.ones(x.shape[1],bool)
    minimize=np.asarray(minimize,bool)
    if minimize.shape!=(x.shape[1],):raise ValueError('minimize must have length D')
    z=x.copy(); z[:,~minimize]*=-1.; keep=np.ones(len(z),bool)
    for i in range(len(z)):
        if keep[i] and np.any(np.all(z<=z[i],axis=1)&np.any(z<z[i],axis=1)):keep[i]=False
    return keep
