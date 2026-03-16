import pandas as pd
import pytest

from stock_selection.normalize.utils import percentile_rank, robust_zscore, winsorize_series


def test_winsorize_series_clips_to_quantile_bounds() -> None:
    series = pd.Series([1.0, 2.0, 100.0])

    result = winsorize_series(series, lower=0.0, upper=0.5)

    assert result.tolist() == [1.0, 2.0, 2.0]


def test_percentile_rank_returns_percent_scale() -> None:
    series = pd.Series([10.0, 20.0, 30.0])

    result = percentile_rank(series)

    assert result.tolist() == pytest.approx([100.0 / 3.0, 200.0 / 3.0, 100.0])


def test_robust_zscore_returns_series_and_zero_when_mad_is_zero() -> None:
    series = pd.Series([5.0, 5.0, 5.0])

    result = robust_zscore(series)

    assert isinstance(result, pd.Series)
    assert result.tolist() == [0.0, 0.0, 0.0]
