from __future__ import annotations
import numpy as np
from sklearn.neighbors import NearestNeighbors

class SpatialSupportModel:
    """Quantify whether counterfactual positions are supported by measured training data."""
    def __init__(self, radius_m=15.0, min_neighbors=5):
        self.radius_m=float(radius_m); self.min_neighbors=int(min_neighbors); self.nn=None
    def fit(self, df):
        xy=df[["utm_x_m","utm_y_m"]].to_numpy(float)
        self.nn=NearestNeighbors(n_neighbors=1).fit(xy); self.xy_=xy; return self
    def evaluate(self, df):
        if self.nn is None: raise RuntimeError("fit support model first")
        xy=df[["utm_x_m","utm_y_m"]].to_numpy(float)
        d,_=self.nn.kneighbors(xy, n_neighbors=1)
        d=d[:,0]
        density=np.array([np.sum(np.linalg.norm(self.xy_-p,axis=1)<=self.radius_m) for p in xy],dtype=int)
        supported=(d<=self.radius_m)&(density>=self.min_neighbors)
        return {"nearest_distance_m":d,"local_count":density,"supported":supported}
