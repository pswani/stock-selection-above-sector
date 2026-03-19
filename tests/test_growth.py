from datetime import date

import pytest

from stock_selection.models import FundamentalSnapshot
from stock_selection.scoring import (
    GrowthPillarEngine,
    RelativePerformancePillarEngine,
    assemble_pillar_score_cards,
    build_growth_observations,
    score_growth,
)


def test_growth_scores_percentile_rank_end_to_end() -> None:
    observations = build_growth_observations(
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.20,
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.05,
            ),
            "CCC": FundamentalSnapshot(
                ticker="CCC",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.10,
            ),
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
            "CCC": "sector:tech",
        },
        as_of=date(2026, 1, 31),
    )

    cards = score_growth(observations)
    by_ticker = {card.ticker: card for card in cards}

    assert by_ticker["AAA"].score == pytest.approx(100.0)
    assert by_ticker["BBB"].score == pytest.approx(100.0 / 3.0)
    assert by_ticker["CCC"].score == pytest.approx(200.0 / 3.0)
    assert [card.coverage_ratio for card in cards] == pytest.approx([1.0, 1.0, 1.0])
    assert [card.pillar for card in cards] == ["G", "G", "G"]
    assert by_ticker["AAA"].diagnostics["factor_name"] == "revenue_growth_yoy"
    assert by_ticker["AAA"].diagnostics["normalization_status"] == "ok"


def test_growth_keeps_missing_data_and_as_of_mismatch_explicit() -> None:
    observations = build_growth_observations(
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.12,
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=None,
            ),
            "CCC": FundamentalSnapshot(
                ticker="CCC",
                as_of=date(2025, 12, 31),
                revenue_growth_yoy=0.08,
            ),
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
            "CCC": "sector:tech",
            "DDD": None,
        },
        tickers=["AAA", "BBB", "CCC", "DDD"],
        as_of=date(2026, 1, 31),
    )

    cards = score_growth(observations)
    by_ticker = {card.ticker: card for card in cards}

    assert by_ticker["AAA"].score is None
    assert by_ticker["AAA"].coverage_ratio == pytest.approx(1.0 / 3.0)
    assert by_ticker["AAA"].diagnostics["normalization_status"] == "insufficient_peer_group"

    assert by_ticker["BBB"].score is None
    assert by_ticker["BBB"].coverage_ratio == pytest.approx(1.0 / 3.0)
    assert by_ticker["BBB"].diagnostics["normalization_status"] == "missing_value"

    assert by_ticker["CCC"].score is None
    assert by_ticker["CCC"].coverage_ratio == pytest.approx(1.0 / 3.0)
    assert by_ticker["CCC"].diagnostics["normalization_status"] == "missing_value"

    assert by_ticker["DDD"].score is None
    assert by_ticker["DDD"].coverage_ratio is None
    assert by_ticker["DDD"].diagnostics["normalization_status"] == "missing_peer_group"


def test_growth_pillar_engine_scores_requested_tickers_only() -> None:
    engine = GrowthPillarEngine(
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.20,
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.05,
            ),
            "CCC": FundamentalSnapshot(
                ticker="CCC",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.10,
            ),
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
            "CCC": "sector:tech",
        },
    )

    cards = engine.score_cards(["CCC", "AAA"], as_of=date(2026, 1, 31))
    scores = engine.score(["CCC", "AAA"], as_of=date(2026, 1, 31))

    assert [card.ticker for card in cards] == ["AAA", "CCC"]
    assert [card.score for card in cards] == pytest.approx([100.0, 50.0])
    assert scores == {"AAA": 100.0, "CCC": 50.0}


def test_growth_and_relative_performance_assemble_without_final_ranking() -> None:
    growth_engine = GrowthPillarEngine(
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.20,
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB",
                as_of=date(2026, 1, 31),
                revenue_growth_yoy=0.05,
            ),
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
        },
    )
    rp_engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )

    cards = growth_engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    cards.extend(rp_engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31)))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=2)

    assert [assembly.ticker for assembly in assemblies] == ["AAA", "BBB"]
    assert [assembly.assembly_status for assembly in assemblies] == ["ok", "ok"]
    assert all(assembly.meets_minimum_pillars for assembly in assemblies)
    assert assemblies[0].pillar_scores.keys() == {"G", "RP"}
    assert assemblies[0].missing_pillars == ["Q", "V", "R", "S"]
