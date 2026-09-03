import numpy as np
from iscai.evaluation.statistics import cluster_paired_bootstrap_delta

def test_cluster_bootstrap_identical_constant_delta():
    a=np.array([1.,2.,3.,4.]); b=a+2.; c=np.array(['x','x','y','y'])
    r=cluster_paired_bootstrap_delta(a,b,c,samples=200,rng=1)
    assert r['mean_delta']==2.0
    assert r['ci_low']==2.0 and r['ci_high']==2.0
    assert r['n_clusters']==2

def test_cluster_bootstrap_validates_shapes():
    try: cluster_paired_bootstrap_delta([1,2],[2,3],['x'],samples=10)
    except ValueError: pass
    else: raise AssertionError('expected ValueError')
