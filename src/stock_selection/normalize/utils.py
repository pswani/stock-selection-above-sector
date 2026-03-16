from __future__ import annotations

import numpy as np
import pandas as pd


def winsorize_series(series: pd.Series, lower: float = 0.05, upper: float = 0.95) -> pd.Series:
    lower_bound = series.quantile(lower)
    upper_bound = series.quantile(upper)
    return series.clip(lower=lower_bound, upper=upper_bound)


def percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(pct=True) * 100.0


def robust_zscore(series: pd.Series) -> pd.Series:
    median = float(series.median())
    mad = float(np.median(np.abs(series - median)))
    if mad == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    zscores = 0.6745 * (series - median) / mad
    return pd.Series(zscores, index=series.index, dtype=float)
