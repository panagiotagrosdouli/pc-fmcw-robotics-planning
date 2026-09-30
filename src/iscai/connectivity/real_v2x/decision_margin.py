from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from .matched_replay import CrossRunSpeedMatcher


def _spatial_thin(g: pd.DataFrame, spacing_m: float) -> pd.DataFrame:
    if g.empty or spacing_m <= 0:
        return g
    g = g.sort_values("pub_time_ms", kind="stable").reset_index(drop=True)
    keep = [0]
    last = g.loc[0, ["utm_x_m", "utm_y_m"]].to_numpy(float)
    for i in range(1, len(g)):
        p = g.loc[i, ["utm_x_m", "utm_y_m"]].to_numpy(float)
        if float(np.linalg.norm(p - last)) >= spacing_m:
            keep.append(i)
            last = p
    return g.iloc[keep].copy()


def build_matched_margin_table(
    fit_df: pd.DataFrame,
    slow_speed_kmh: float = 30.0,
    fast_speed_kmh: float = 50.0,
    caliper_m: float = 2.0,
    k_donors: int = 3,
    anchor_spacing_m: float = 5.0,
) -> pd.DataFrame:
    """Build training-only paired action margins from repeated field runs.

    Positive target values mean the FAST action has higher measured delay than SLOW,
    i.e. a communication benefit may exist for slowing down.

    Each anchor run is excluded by CrossRunSpeedMatcher from its own donor outcome.
    The table is for model development only and is not a causal speed-effect dataset.
    """
    matcher = CrossRunSpeedMatcher(caliper_m=caliper_m, k_donors=k_donors).fit(fit_df)
    rows: list[dict] = []
    for run_id, g0 in fit_df.groupby("run_id", sort=False):
        g = _spatial_thin(g0, anchor_spacing_m)
        for _, q in g.iterrows():
            slow = matcher.match(q, slow_speed_kmh)
            fast = matcher.match(q, fast_speed_kmh)
            if slow is None or fast is None:
                continue
            rows.append({
                "anchor_run_id": str(run_id),
                "network": str(q["network"]),
                "direction": str(q["direction"]),
                "utm_x_m": float(q["utm_x_m"]),
                "utm_y_m": float(q["utm_y_m"]),
                "fast_minus_slow_delay_gain_ms": float(fast.delay_ms - slow.delay_ms),
                "slow_delay_ms": float(slow.delay_ms),
                "fast_delay_ms": float(fast.delay_ms),
                "slow_nearest_m": float(slow.nearest_distance_m),
                "fast_nearest_m": float(fast.nearest_distance_m),
                "slow_donor_runs": int(slow.n_donor_runs),
                "fast_donor_runs": int(fast.n_donor_runs),
            })
    return pd.DataFrame(rows)


class ConditionedMarginKNN:
    """Spatial KNN for the pairwise communication action margin.

    Models are conditioned on network and travel direction. The training objective is
    the action margin itself rather than absolute QoS regression error.
    """

    def __init__(self, n_neighbors: int = 25, min_group_samples: int = 50):
        self.n_neighbors = int(n_neighbors)
        self.min_group_samples = int(min_group_samples)
        self._groups: dict[tuple[str, str], dict] = {}

    @staticmethod
    def _key(network, direction):
        return str(network), str(direction)

    def fit(self, margin_df: pd.DataFrame):
        required = {
            "network", "direction", "utm_x_m", "utm_y_m",
            "fast_minus_slow_delay_gain_ms",
        }
        missing = required.difference(margin_df.columns)
        if missing:
            raise ValueError(f"margin dataframe missing: {sorted(missing)}")
        self._groups = {}
        for key, g in margin_df.groupby(["network", "direction"], sort=False):
            if len(g) < self.min_group_samples:
                continue
            g = g.reset_index(drop=True)
            k = min(self.n_neighbors, len(g))
            nn = NearestNeighbors(n_neighbors=k).fit(
                g[["utm_x_m", "utm_y_m"]].to_numpy(float)
            )
            self._groups[self._key(*key)] = {
                "frame": g,
                "nn": nn,
                "k": k,
            }
        return self

    def predict_stats(
        self,
        query: pd.Series | dict,
        lower_q: float = 0.10,
        upper_q: float = 0.90,
    ) -> dict | None:
        payload = self._groups.get(self._key(query["network"], query["direction"]))
        if payload is None:
            return None
        xy = np.asarray([[float(query["utm_x_m"]), float(query["utm_y_m"])]])
        distances, indices = payload["nn"].kneighbors(xy)
        g = payload["frame"].iloc[indices[0]]
        y = g["fast_minus_slow_delay_gain_ms"].to_numpy(float)
        return {
            "mean_gain_ms": float(np.mean(y)),
            "median_gain_ms": float(np.median(y)),
            "lower_gain_ms": float(np.quantile(y, lower_q)),
            "upper_gain_ms": float(np.quantile(y, upper_q)),
            "nearest_margin_train_m": float(np.min(distances[0])),
            "mean_margin_train_m": float(np.mean(distances[0])),
            "n_margin_neighbors": int(len(y)),
        }
