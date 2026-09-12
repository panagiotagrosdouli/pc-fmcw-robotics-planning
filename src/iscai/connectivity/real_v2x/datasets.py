from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
import numpy as np

_CANONICAL = [
    "pub_time_ms", "sub_time_ms", "delay_ms", "utm_x_m", "utm_y_m",
    "heading_rad", "velocity_mps", "cell_id", "sinr_db", "rsrp_db",
]


def _normalize_header(name: str) -> str:
    table = {
        "pub_time(ms)": "pub_time_ms", "sub_time(ms)": "sub_time_ms",
        "delay(ms)": "delay_ms", "utmX(m)": "utm_x_m", "utmY(m)": "utm_y_m",
        "heading(rad)": "heading_rad", "velocity(m/s)": "velocity_mps",
        "cellid(db)": "cell_id", "sinr(db)": "sinr_db", "rsrp(db)": "rsrp_db",
        "currentX(m)": "current_x_m", "currentY(m)": "current_y_m",
    }
    return table.get(name, name)


def load_cicv5g_file(path: str | Path) -> pd.DataFrame:
    """Load one CICV5G whitespace-delimited run robustly.

    Some released files contain two position-deviation columns after the ten-column
    header. We infer those columns rather than dropping them silently.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        header = f.readline().strip().split()
        first = f.readline().strip().split()
    n = len(first)
    names = [_normalize_header(x) for x in header]
    if n > len(names):
        extras = ["current_x_m", "current_y_m"][: n - len(names)]
        extras += [f"extra_{i}" for i in range(max(0, n - len(names) - len(extras)))]
        names = names + extras
    df = pd.read_csv(path, sep=r"\s+", skiprows=1, names=names, engine="python")
    required = set(_CANONICAL)
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CICV5G file missing required columns: {sorted(missing)}")
    numeric = [c for c in df.columns if c != "cell_id"]
    for c in numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["pub_time_ms", "delay_ms", "utm_x_m", "utm_y_m", "sinr_db", "rsrp_db"])
    df = df.sort_values("pub_time_ms", kind="stable").reset_index(drop=True)
    return df


def discover_cicv5g_files(root: str | Path) -> list[Path]:
    root = Path(root)
    return sorted(p for p in root.rglob("*.txt") if p.is_file())


def add_run_metadata(df: pd.DataFrame, path: str | Path) -> pd.DataFrame:
    path = Path(path)
    out = df.copy()
    s = path.as_posix().lower()
    out["run_id"] = path.stem
    out["source_file"] = path.as_posix()
    out["scenario"] = "W2S" if ("w2s" in s or "s2w" in s) else next((x for x in ["urban", "arterial", "rural"] if x in s), "unknown")
    out["direction"] = "s2w" if "s2w" in s else ("w2s" if "w2s" in s else "unknown")
    out["network"] = "n78" if "n78" in s else ("n8" if re.search(r"(^|[/_])n8([/_]|$)", s) else "unknown")
    m = re.search(r"(?:^|[/_])v(\d+)(?:[/_]|$)", s)
    out["nominal_speed_kmh"] = float(m.group(1)) if m else np.nan
    return out


def blocked_run_split(df: pd.DataFrame, train_frac: float = 0.6, cal_frac: float = 0.2, seed: int = 0):
    """Leakage-resistant split by whole run IDs, preserving deterministic order."""
    if "run_id" not in df:
        raise ValueError("run_id required for grouped split")
    runs = sorted(df["run_id"].dropna().unique().tolist())
    rng = np.random.default_rng(seed)
    runs = [runs[i] for i in rng.permutation(len(runs))]
    if len(runs) < 3:
        raise ValueError("at least three independent runs are required")
    n = len(runs)
    n_train = max(1, int(np.floor(n * train_frac)))
    n_cal = max(1, int(np.floor(n * cal_frac)))
    if n_train + n_cal >= n:
        n_cal = 1
        n_train = n - 2
    train_runs = set(runs[:n_train])
    cal_runs = set(runs[n_train:n_train+n_cal])
    test_runs = set(runs[n_train+n_cal:])
    return (
        df[df.run_id.isin(train_runs)].copy(),
        df[df.run_id.isin(cal_runs)].copy(),
        df[df.run_id.isin(test_runs)].copy(),
        {"train_runs": sorted(train_runs), "cal_runs": sorted(cal_runs), "test_runs": sorted(test_runs)},
    )
