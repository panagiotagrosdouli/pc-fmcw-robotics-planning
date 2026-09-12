from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor

FEATURES = ["utm_x_m", "utm_y_m", "velocity_mps", "heading_sin", "heading_cos", "sinr_lag1", "delay_lag1"]


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["heading_sin"] = np.sin(x["heading_rad"].astype(float))
    x["heading_cos"] = np.cos(x["heading_rad"].astype(float))
    # For measured one-step evaluation, derive lag features causally from the prior
    # sample. For counterfactual candidate trajectories, callers may explicitly
    # supply lag context; never overwrite it with future measured QoS.
    if "sinr_lag1" not in x or "delay_lag1" not in x:
        if "run_id" in x:
            sinr_lag = x.groupby("run_id")["sinr_db"].shift(1)
            delay_lag = x.groupby("run_id")["delay_ms"].shift(1)
        else:
            sinr_lag = x["sinr_db"].shift(1)
            delay_lag = x["delay_ms"].shift(1)
        if "sinr_lag1" not in x:
            x["sinr_lag1"] = sinr_lag.fillna(x["sinr_db"])
        if "delay_lag1" not in x:
            x["delay_lag1"] = delay_lag.fillna(x["delay_ms"])
    return x


@dataclass
class PersistencePredictor:
    target: str = "delay_ms"
    def fit(self, df: pd.DataFrame): return self
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        lag = "delay_lag1" if self.target == "delay_ms" else "sinr_lag1"
        return make_features(df)[lag].to_numpy(float)


class SpatialKNNPredictor:
    def __init__(self, target="delay_ms", n_neighbors=20, weights="distance"):
        self.target = target
        self.n_neighbors = int(n_neighbors)
        self.weights = weights
        self.model = KNeighborsRegressor(n_neighbors=self.n_neighbors, weights=weights)
        self._origin = None
    def _xy(self, df):
        xy = df[["utm_x_m", "utm_y_m"]].to_numpy(float)
        if self._origin is None: self._origin = xy.mean(axis=0)
        return xy - self._origin
    def fit(self, df):
        k = min(self.n_neighbors, len(df))
        if k < 1: raise ValueError("empty training data")
        if k != self.n_neighbors:
            self.model = KNeighborsRegressor(n_neighbors=k, weights=self.weights)
        self.model.fit(self._xy(df), df[self.target].to_numpy(float)); return self
    def predict(self, df): return self.model.predict(self._xy(df))


class ConditionedSpatialKNNPredictor:
    """Spatial QoS map conditioned on known communication/motion context.

    Separate maps are fitted for network band, travel direction and nominal speed.
    Queries with an unseen/sparse condition fall back to the global spatial map.
    This prevents physically different n8/n78 and direction/speed runs from being
    averaged into a single map merely because they share coordinates.
    """
    def __init__(self, target="delay_ms", n_neighbors=20, min_group_samples=100,
                 condition_cols=("network", "direction", "nominal_speed_kmh")):
        self.target=target; self.n_neighbors=int(n_neighbors); self.min_group_samples=int(min_group_samples); self.condition_cols=tuple(condition_cols)
        self.global_model=SpatialKNNPredictor(target,n_neighbors); self.models={}
    def _key(self,row):
        vals=[]
        for c in self.condition_cols:
            v=row[c]
            vals.append(None if pd.isna(v) else v)
        return tuple(vals)
    def fit(self,df):
        self.global_model.fit(df); self.models={}
        for key,g in df.groupby(list(self.condition_cols),dropna=False):
            if not isinstance(key,tuple): key=(key,)
            key=tuple(None if pd.isna(v) else v for v in key)
            if len(g)>=self.min_group_samples:
                self.models[key]=SpatialKNNPredictor(self.target,self.n_neighbors).fit(g)
        return self
    def predict(self,df):
        out=np.empty(len(df),float)
        # Preserve original row order while dispatching each context to its map.
        for key,idxs in df.groupby(list(self.condition_cols),dropna=False,sort=False).groups.items():
            if not isinstance(key,tuple): key=(key,)
            key=tuple(None if pd.isna(v) else v for v in key)
            pos=np.asarray([df.index.get_loc(i) for i in idxs],int)
            model=self.models.get(key,self.global_model)
            out[pos]=model.predict(df.loc[idxs])
        return out


class TreeQoSPredictor:
    def __init__(self, target="delay_ms", model="extra_trees", n_estimators=200, random_state=0):
        self.target = target
        cls = ExtraTreesRegressor if model == "extra_trees" else RandomForestRegressor
        self.model = cls(n_estimators=n_estimators, min_samples_leaf=3, n_jobs=-1, random_state=random_state)
        self.feature_medians = None
    def _matrix(self, df):
        f = make_features(df)[FEATURES].astype(float)
        if self.feature_medians is None: self.feature_medians = f.median()
        return f.fillna(self.feature_medians).to_numpy(float)
    def fit(self, df):
        self.model.fit(self._matrix(df), df[self.target].to_numpy(float)); return self
    def predict(self, df): return self.model.predict(self._matrix(df))
    def ensemble_predictions(self, df):
        X = self._matrix(df)
        return np.vstack([t.predict(X) for t in self.model.estimators_])
