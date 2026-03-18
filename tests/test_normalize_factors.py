from datetime import date

import pandas as pd
import pytest

from stock_selection.factors import normalize_factor_output, normalized_factor_output_frame
from stock_selection.models import (
    FactorObservation,
    MetricDirection,
    NormalizedFactorObservation,
)


def test_normalize_factor_output_orients_values_by_factor_direction() -> None:
    observations = [
        FactorObservation(
            ticker="AAA",
            factor_name="forward_pe",
            value=10.0,
            direction=MetricDirection.LOWER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
        FactorObservation(
            ticker="BBB",
            factor_name="forward_pe",
            value=20.0,
            direction=MetricDirection.LOWER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
        FactorObservation(
            ticker="AAA",
            factor_name="return_on_equity",
            value=0.10,
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
        FactorObservation(
            ticker="BBB",
            factor_name="return_on_equity",
            value=0.20,
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
    ]

    result = normalize_factor_output(observations)
    assert all(isinstance(item, NormalizedFactorObservation) for item in result)
    frame = normalized_factor_output_frame(result)

    forward_pe = frame[frame["factor_name"] == "forward_pe"].reset_index(drop=True)
    assert forward_pe["ticker"].tolist() == ["AAA", "BBB"]
    assert forward_pe["raw_value"].tolist() == pytest.approx([10.0, 20.0])
    assert forward_pe["oriented_value"].tolist() == pytest.approx([-10.0, -20.0])
    assert forward_pe["percentile_rank"].tolist() == pytest.approx([100.0, 50.0])

    roe = frame[frame["factor_name"] == "return_on_equity"].reset_index(drop=True)
    assert roe["ticker"].tolist() == ["AAA", "BBB"]
    assert roe["raw_value"].tolist() == pytest.approx([0.10, 0.20])
    assert roe["oriented_value"].tolist() == pytest.approx([0.10, 0.20])
    assert roe["percentile_rank"].tolist() == pytest.approx([50.0, 100.0])


def test_normalize_factor_output_keeps_missing_data_explicit() -> None:
    observations = [
        FactorObservation(
            ticker="AAA",
            factor_name="relative_strength_6m",
            value=0.12,
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
        FactorObservation(
            ticker="BBB",
            factor_name="relative_strength_6m",
            value=None,
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
        FactorObservation(
            ticker="CCC",
            factor_name="relative_strength_6m",
            value=0.08,
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group=None,
            as_of=date(2026, 1, 31),
        ),
    ]

    result = normalize_factor_output(observations)
    frame = normalized_factor_output_frame(result)

    missing_group = frame[frame["ticker"] == "CCC"].iloc[0]
    assert missing_group["normalization_status"] == "missing_peer_group"
    assert pd.isna(missing_group["percentile_rank"])
    assert pd.isna(missing_group["coverage_ratio"])

    valid_row = frame[frame["ticker"] == "AAA"].iloc[0]
    missing_value = frame[frame["ticker"] == "BBB"].iloc[0]
    assert valid_row["normalization_status"] == "insufficient_peer_group"
    assert missing_value["normalization_status"] == "missing_value"
    assert valid_row["coverage_ratio"] == pytest.approx(0.5)
    assert missing_value["coverage_ratio"] == pytest.approx(0.5)


def test_normalize_factor_output_frame_preserves_deterministic_order() -> None:
    observations = [
        FactorObservation(
            ticker="BBB",
            factor_name="return_on_equity",
            value=0.20,
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
        FactorObservation(
            ticker="AAA",
            factor_name="forward_pe",
            value=10.0,
            direction=MetricDirection.LOWER_IS_BETTER,
            peer_group="sector:tech",
            as_of=date(2026, 1, 31),
        ),
    ]

    normalized = normalize_factor_output(observations)
    frame = normalized_factor_output_frame(normalized)

    assert [(item.factor_name, item.ticker) for item in normalized] == [
        ("forward_pe", "AAA"),
        ("return_on_equity", "BBB"),
    ]
    assert frame[["factor_name", "ticker"]].values.tolist() == [
        ["forward_pe", "AAA"],
        ["return_on_equity", "BBB"],
    ]
