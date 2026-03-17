from datetime import date

import pytest

from stock_selection.scoring import (
    build_relative_performance_observations,
    score_relative_performance,
)


def test_relative_performance_scores_percentile_rank_end_to_end() -> None:
    observations = build_relative_performance_observations(
        returns_6m={
            "AAA": 0.30,
            "BBB": 0.10,
            "CCC": 0.20,
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
            "CCC": "sector:tech",
        },
        as_of=date(2026, 1, 31),
    )

    cards = score_relative_performance(observations)
    by_ticker = {card.ticker: card for card in cards}

    assert by_ticker["AAA"].score == pytest.approx(100.0)
    assert by_ticker["BBB"].score == pytest.approx(100.0 / 3.0)
    assert by_ticker["CCC"].score == pytest.approx(200.0 / 3.0)
    assert [card.coverage_ratio for card in cards] == pytest.approx([1.0, 1.0, 1.0])
    assert [card.pillar for card in cards] == ["RP", "RP", "RP"]
    assert by_ticker["AAA"].diagnostics["normalization_status"] == "ok"
    assert by_ticker["AAA"].diagnostics["factor_name"] == "relative_strength_6m"


def test_relative_performance_keeps_missing_data_explicit() -> None:
    observations = build_relative_performance_observations(
        returns_6m={
            "AAA": 0.12,
            "BBB": None,
            "CCC": 0.08,
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
            "CCC": None,
        },
        as_of=date(2026, 1, 31),
    )

    cards = score_relative_performance(observations)
    by_ticker = {card.ticker: card for card in cards}

    assert by_ticker["AAA"].score == 0.0
    assert by_ticker["AAA"].coverage_ratio == pytest.approx(0.5)
    assert by_ticker["AAA"].diagnostics["normalization_status"] == "insufficient_peer_group"

    assert by_ticker["BBB"].score == 0.0
    assert by_ticker["BBB"].coverage_ratio == pytest.approx(0.5)
    assert by_ticker["BBB"].diagnostics["normalization_status"] == "missing_value"

    assert by_ticker["CCC"].score == 0.0
    assert by_ticker["CCC"].coverage_ratio is None
    assert by_ticker["CCC"].diagnostics["normalization_status"] == "missing_peer_group"
