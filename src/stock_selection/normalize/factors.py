from __future__ import annotations

from datetime import date

import pandas as pd

from stock_selection.models import (
    FactorObservation,
    MetricDirection,
    NormalizedFactorObservation,
)
from stock_selection.normalize.peer import normalize_by_peer_group

NORMALIZED_FACTOR_COLUMNS = [
    "ticker",
    "factor_name",
    "direction",
    "peer_group",
    "as_of",
    "source",
    "raw_value",
    "oriented_value",
    "winsorized_value",
    "percentile_rank",
    "robust_zscore",
    "peer_group_size",
    "peer_group_valid_size",
    "coverage_ratio",
    "normalization_status",
]


def normalize_factor_observations(
    observations: list[FactorObservation],
    *,
    min_group_size: int = 2,
    winsor_lower: float = 0.05,
    winsor_upper: float = 0.95,
) -> list[NormalizedFactorObservation]:
    if not observations:
        return []

    rows = [
        {
            "ticker": observation.ticker,
            "factor_name": observation.factor_name,
            "direction": observation.direction.value,
            "peer_group": observation.peer_group,
            "as_of": observation.as_of,
            "source": observation.source,
            "raw_value": observation.value,
        }
        for observation in observations
    ]
    frame = pd.DataFrame(rows)
    frame["oriented_value"] = frame["raw_value"]

    lower_is_better_mask = frame["direction"] == MetricDirection.LOWER_IS_BETTER.value
    lower_is_better_values = pd.Series(
        pd.to_numeric(frame.loc[lower_is_better_mask, "raw_value"], errors="coerce"),
        index=frame.loc[lower_is_better_mask].index,
        dtype=float,
    )
    frame.loc[lower_is_better_mask, "oriented_value"] = (
        0.0 - lower_is_better_values
    )

    normalized_frames: list[pd.DataFrame] = []
    for _, group_frame in frame.groupby(
        ["factor_name", "direction", "as_of"],
        sort=True,
        dropna=False,
    ):
        normalized = normalize_by_peer_group(
            group_frame,
            value_column="oriented_value",
            peer_group_column="peer_group",
            min_group_size=min_group_size,
            winsor_lower=winsor_lower,
            winsor_upper=winsor_upper,
        )
        normalized_frames.append(normalized)

    normalized_frame = pd.concat(normalized_frames, ignore_index=True)
    result = normalized_frame[NORMALIZED_FACTOR_COLUMNS]
    rows = list(result.itertuples(index=False, name=None))
    column_index = {column: position for position, column in enumerate(NORMALIZED_FACTOR_COLUMNS)}
    sorted_rows = sorted(
        rows,
        key=lambda record: (
            str(record[column_index["factor_name"]]),
            str(record[column_index["direction"]]),
            record[column_index["as_of"]] or date.min,
            str(record[column_index["peer_group"]] or ""),
            str(record[column_index["ticker"]]),
        ),
    )
    return [
        NormalizedFactorObservation(
            ticker=str(record[column_index["ticker"]]),
            factor_name=str(record[column_index["factor_name"]]),
            direction=MetricDirection(str(record[column_index["direction"]])),
            peer_group=(
                None
                if pd.isna(record[column_index["peer_group"]])
                else str(record[column_index["peer_group"]])
            ),
            as_of=record[column_index["as_of"]],
            source=(
                None
                if pd.isna(record[column_index["source"]])
                else str(record[column_index["source"]])
            ),
            raw_value=_optional_float(record[column_index["raw_value"]]),
            oriented_value=_optional_float(record[column_index["oriented_value"]]),
            winsorized_value=_optional_float(record[column_index["winsorized_value"]]),
            percentile_rank=_optional_float(record[column_index["percentile_rank"]]),
            robust_zscore=_optional_float(record[column_index["robust_zscore"]]),
            peer_group_size=int(record[column_index["peer_group_size"]]),
            peer_group_valid_size=int(record[column_index["peer_group_valid_size"]]),
            coverage_ratio=_optional_float(record[column_index["coverage_ratio"]]),
            normalization_status=str(record[column_index["normalization_status"]]),
        )
        for record in sorted_rows
    ]


def normalized_factor_observations_to_frame(
    observations: list[NormalizedFactorObservation],
) -> pd.DataFrame:
    if not observations:
        return pd.DataFrame(columns=NORMALIZED_FACTOR_COLUMNS)
    return pd.DataFrame([observation.model_dump(mode="python") for observation in observations])


def _optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        numeric = float(value)
        if pd.isna(numeric):
            return None
        return numeric
    return None
