from __future__ import annotations

import numpy as np
import pandas as pd

from stock_selection.normalize.utils import percentile_rank, robust_zscore, winsorize_series

NORMALIZATION_STATUS_OK = "ok"
NORMALIZATION_STATUS_MISSING_PEER_GROUP = "missing_peer_group"
NORMALIZATION_STATUS_MISSING_VALUE = "missing_value"
NORMALIZATION_STATUS_INSUFFICIENT_PEER_GROUP = "insufficient_peer_group"


def normalize_by_peer_group(
    frame: pd.DataFrame,
    *,
    value_column: str = "value",
    peer_group_column: str = "peer_group",
    min_group_size: int = 2,
    winsor_lower: float = 0.05,
    winsor_upper: float = 0.95,
) -> pd.DataFrame:
    required_columns = {value_column, peer_group_column}
    missing_columns = sorted(required_columns.difference(frame.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required normalization columns: {missing}")
    if min_group_size < 1:
        raise ValueError("min_group_size must be at least 1")

    result = frame.copy()

    numeric_values = pd.Series(
        pd.to_numeric(result[value_column], errors="coerce"),
        index=result.index,
        dtype=float,
    )
    finite_mask = pd.Series(
        np.isfinite(numeric_values.to_numpy(dtype=float, na_value=np.nan)),
        index=result.index,
    )
    valid_values = numeric_values.where(finite_mask, other=np.nan)
    result[value_column] = valid_values

    peer_groups = pd.Series(result[peer_group_column], index=result.index)
    peer_group_present = peer_groups.notna()

    group_size = peer_groups.groupby(peer_groups).transform("size")
    valid_group_size = valid_values.groupby(peer_groups).transform("count")

    result["peer_group_size"] = group_size.fillna(0).astype(int)
    result["peer_group_valid_size"] = valid_group_size.fillna(0).astype(int)
    result["coverage_ratio"] = pd.Series(np.nan, index=result.index, dtype=float)
    coverage_mask = result["peer_group_size"] > 0
    result.loc[coverage_mask, "coverage_ratio"] = (
        result.loc[coverage_mask, "peer_group_valid_size"]
        / result.loc[coverage_mask, "peer_group_size"]
    )

    result["winsorized_value"] = np.nan
    result["percentile_rank"] = np.nan
    result["robust_zscore"] = np.nan
    result["normalization_status"] = NORMALIZATION_STATUS_OK

    result.loc[~peer_group_present, "normalization_status"] = (
        NORMALIZATION_STATUS_MISSING_PEER_GROUP
    )
    result.loc[peer_group_present & valid_values.isna(), "normalization_status"] = (
        NORMALIZATION_STATUS_MISSING_VALUE
    )

    sufficient_group_mask = result["peer_group_valid_size"] >= min_group_size
    insufficient_rows = (
        peer_group_present
        & valid_values.notna()
        & ~sufficient_group_mask
    )
    result.loc[insufficient_rows, "normalization_status"] = (
        NORMALIZATION_STATUS_INSUFFICIENT_PEER_GROUP
    )

    eligible_rows = (
        peer_group_present
        & valid_values.notna()
        & sufficient_group_mask
    )

    for _, group_frame in result.loc[eligible_rows].groupby(peer_group_column, sort=True):
        group_index = group_frame.index
        group_values = valid_values.loc[group_index]
        winsorized = winsorize_series(group_values, lower=winsor_lower, upper=winsor_upper)
        result.loc[group_index, "winsorized_value"] = winsorized
        result.loc[group_index, "percentile_rank"] = percentile_rank(winsorized)
        result.loc[group_index, "robust_zscore"] = robust_zscore(winsorized)

    return result
