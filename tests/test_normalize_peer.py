import pandas as pd
import pytest

from stock_selection.normalize.peer import (
    NORMALIZATION_STATUS_INSUFFICIENT_PEER_GROUP,
    NORMALIZATION_STATUS_MISSING_PEER_GROUP,
    NORMALIZATION_STATUS_MISSING_VALUE,
    NORMALIZATION_STATUS_OK,
    normalize_by_peer_group,
)


def test_normalize_by_peer_group_handles_ties_deterministically() -> None:
    frame = pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D"],
            "peer_group": ["sector:tech"] * 4,
            "value": [10.0, 20.0, 20.0, 30.0],
        }
    )

    result = normalize_by_peer_group(frame)

    assert result["normalization_status"].tolist() == [NORMALIZATION_STATUS_OK] * 4
    assert result["percentile_rank"].tolist() == pytest.approx([25.0, 62.5, 62.5, 100.0])
    assert result["peer_group_size"].tolist() == [4, 4, 4, 4]
    assert result["peer_group_valid_size"].tolist() == [4, 4, 4, 4]
    assert result["coverage_ratio"].tolist() == pytest.approx([1.0, 1.0, 1.0, 1.0])


def test_normalize_by_peer_group_marks_tiny_groups_as_insufficient() -> None:
    frame = pd.DataFrame(
        {
            "ticker": ["A"],
            "peer_group": ["sector:energy"],
            "value": [5.0],
        }
    )

    result = normalize_by_peer_group(frame, min_group_size=2)

    assert result.loc[0, "normalization_status"] == NORMALIZATION_STATUS_INSUFFICIENT_PEER_GROUP
    assert result.loc[0, "percentile_rank"] != result.loc[0, "percentile_rank"]
    assert result.loc[0, "robust_zscore"] != result.loc[0, "robust_zscore"]
    assert result.loc[0, "peer_group_size"] == 1
    assert result.loc[0, "peer_group_valid_size"] == 1
    assert result.loc[0, "coverage_ratio"] == pytest.approx(1.0)


def test_normalize_by_peer_group_preserves_null_and_missing_group_behavior() -> None:
    frame = pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D"],
            "peer_group": ["sector:health", "sector:health", "sector:health", None],
            "value": [10.0, None, 30.0, 15.0],
        }
    )

    result = normalize_by_peer_group(frame)

    assert result.loc[0, "normalization_status"] == NORMALIZATION_STATUS_OK
    assert result.loc[1, "normalization_status"] == NORMALIZATION_STATUS_MISSING_VALUE
    assert result.loc[2, "normalization_status"] == NORMALIZATION_STATUS_OK
    assert result.loc[3, "normalization_status"] == NORMALIZATION_STATUS_MISSING_PEER_GROUP

    assert result.loc[0, "coverage_ratio"] == pytest.approx(2.0 / 3.0)
    assert result.loc[1, "coverage_ratio"] == pytest.approx(2.0 / 3.0)
    assert result.loc[2, "coverage_ratio"] == pytest.approx(2.0 / 3.0)
    assert pd.isna(result.loc[3, "coverage_ratio"])

    assert result.loc[0, "percentile_rank"] == pytest.approx(50.0)
    assert pd.isna(result.loc[1, "percentile_rank"])
    assert result.loc[2, "percentile_rank"] == pytest.approx(100.0)
    assert pd.isna(result.loc[3, "percentile_rank"])


def test_normalize_by_peer_group_winsorizes_outliers_before_scoring() -> None:
    frame = pd.DataFrame(
        {
            "ticker": ["A", "B", "C"],
            "peer_group": ["sector:industrial"] * 3,
            "value": [1.0, 2.0, 100.0],
        }
    )

    result = normalize_by_peer_group(frame, winsor_lower=0.0, winsor_upper=0.5)

    assert result["winsorized_value"].tolist() == pytest.approx([1.0, 2.0, 2.0])
    assert result["percentile_rank"].tolist() == pytest.approx(
        [100.0 / 3.0, 250.0 / 3.0, 250.0 / 3.0]
    )
    assert result["normalization_status"].tolist() == [NORMALIZATION_STATUS_OK] * 3


def test_normalize_by_peer_group_validates_required_columns() -> None:
    frame = pd.DataFrame({"ticker": ["A"], "value": [1.0]})

    with pytest.raises(ValueError, match="Missing required normalization columns: peer_group"):
        normalize_by_peer_group(frame)
