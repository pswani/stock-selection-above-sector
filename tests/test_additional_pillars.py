from datetime import date

import pytest

from stock_selection.models import EstimateSnapshot, FundamentalSnapshot
from stock_selection.scoring import (
    QualityPillarEngine,
    RiskPillarEngine,
    SentimentPillarEngine,
    ValuationPillarEngine,
    build_quality_observations,
    build_risk_observations,
    build_sentiment_observations,
    build_valuation_observations,
    score_quality,
    score_risk,
    score_sentiment,
    score_valuation,
)


def test_quality_scores_percentile_rank_end_to_end() -> None:
    observations = build_quality_observations(
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA", as_of=date(2026, 1, 31), return_on_equity=0.20
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB", as_of=date(2026, 1, 31), return_on_equity=0.08
            ),
            "CCC": FundamentalSnapshot(
                ticker="CCC", as_of=date(2026, 1, 31), return_on_equity=0.14
            ),
        },
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
        as_of=date(2026, 1, 31),
    )
    cards = score_quality(observations)
    assert [card.pillar for card in cards] == ["Q", "Q", "Q"]
    assert [card.score for card in cards] == pytest.approx([100.0, 100.0 / 3.0, 200.0 / 3.0])


def test_quality_engine_keeps_stale_data_explicit() -> None:
    engine = QualityPillarEngine(
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA", as_of=date(2025, 12, 31), return_on_equity=0.20
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB", as_of=date(2026, 1, 31), return_on_equity=0.08
            ),
        },
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    by_ticker = {card.ticker: card for card in cards}
    assert by_ticker["AAA"].score == 0.0
    assert by_ticker["AAA"].diagnostics["normalization_status"] == "missing_value"


def test_valuation_scores_lower_is_better() -> None:
    observations = build_valuation_observations(
        estimates={
            "AAA": EstimateSnapshot(ticker="AAA", as_of=date(2026, 1, 31), forward_pe=18.0),
            "BBB": EstimateSnapshot(ticker="BBB", as_of=date(2026, 1, 31), forward_pe=30.0),
            "CCC": EstimateSnapshot(ticker="CCC", as_of=date(2026, 1, 31), forward_pe=24.0),
        },
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
        as_of=date(2026, 1, 31),
    )
    cards = score_valuation(observations)
    by_ticker = {card.ticker: card for card in cards}
    assert by_ticker["AAA"].score == pytest.approx(100.0)
    assert by_ticker["BBB"].score == pytest.approx(100.0 / 3.0)


def test_risk_scores_lower_volatility_as_better() -> None:
    observations = build_risk_observations(
        volatility_3m={"AAA": 0.18, "BBB": 0.34, "CCC": 0.24},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
        as_of=date(2026, 1, 31),
    )
    cards = score_risk(observations)
    by_ticker = {card.ticker: card for card in cards}
    assert by_ticker["AAA"].score == pytest.approx(100.0)
    assert by_ticker["BBB"].score == pytest.approx(100.0 / 3.0)


def test_sentiment_scores_revision_trend() -> None:
    observations = build_sentiment_observations(
        estimates={
            "AAA": EstimateSnapshot(
                ticker="AAA", as_of=date(2026, 1, 31), eps_revision_90d=0.12
            ),
            "BBB": EstimateSnapshot(
                ticker="BBB", as_of=date(2026, 1, 31), eps_revision_90d=-0.05
            ),
            "CCC": EstimateSnapshot(
                ticker="CCC", as_of=date(2026, 1, 31), eps_revision_90d=0.03
            ),
        },
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
        as_of=date(2026, 1, 31),
    )
    cards = score_sentiment(observations)
    by_ticker = {card.ticker: card for card in cards}
    assert by_ticker["AAA"].score == pytest.approx(100.0)
    assert by_ticker["BBB"].score == pytest.approx(100.0 / 3.0)


def test_additional_pillar_engines_score_requested_tickers_only() -> None:
    valuation_engine = ValuationPillarEngine(
        estimates={
            "AAA": EstimateSnapshot(ticker="AAA", as_of=date(2026, 1, 31), forward_pe=18.0),
            "BBB": EstimateSnapshot(ticker="BBB", as_of=date(2026, 1, 31), forward_pe=30.0),
            "CCC": EstimateSnapshot(ticker="CCC", as_of=date(2026, 1, 31), forward_pe=24.0),
        },
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
    )
    sentiment_engine = SentimentPillarEngine(
        estimates={
            "AAA": EstimateSnapshot(
                ticker="AAA", as_of=date(2026, 1, 31), eps_revision_90d=0.12
            ),
            "BBB": EstimateSnapshot(
                ticker="BBB", as_of=date(2026, 1, 31), eps_revision_90d=-0.05
            ),
            "CCC": EstimateSnapshot(
                ticker="CCC", as_of=date(2026, 1, 31), eps_revision_90d=0.03
            ),
        },
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
    )
    risk_engine = RiskPillarEngine(
        volatility_3m={"AAA": 0.18, "BBB": 0.34, "CCC": 0.24},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
    )

    assert valuation_engine.score(["CCC", "AAA"], as_of=date(2026, 1, 31)) == {
        "AAA": 100.0,
        "CCC": 50.0,
    }
    assert sentiment_engine.score(["CCC", "AAA"], as_of=date(2026, 1, 31)) == {
        "AAA": 100.0,
        "CCC": 50.0,
    }
    assert risk_engine.score(["CCC", "AAA"], as_of=date(2026, 1, 31)) == {
        "AAA": 100.0,
        "CCC": 50.0,
    }
