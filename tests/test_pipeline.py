from datetime import date

import pytest

from stock_selection.backtest.validation import ValidationPeriodInput, run_validation_backtest
from stock_selection.config import load_settings, load_weight_profile
from stock_selection.explainability import build_explanation_cards
from stock_selection.models import EstimateSnapshot, FundamentalSnapshot, RankingResult
from stock_selection.penalties.rules import MinimumQualityPenalty
from stock_selection.scoring import CompositeScoreInputs, build_composite_rankings


def _full_inputs(as_of: date) -> CompositeScoreInputs:
    return CompositeScoreInputs(
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
        returns_6m={"AAA": 0.30, "BBB": 0.10, "CCC": 0.20},
        volatility_3m={"AAA": 0.18, "BBB": 0.34, "CCC": 0.24},
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA",
                as_of=as_of,
                revenue_growth_yoy=0.24,
                return_on_equity=0.21,
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB",
                as_of=as_of,
                revenue_growth_yoy=0.07,
                return_on_equity=0.08,
            ),
            "CCC": FundamentalSnapshot(
                ticker="CCC",
                as_of=as_of,
                revenue_growth_yoy=0.15,
                return_on_equity=0.14,
            ),
        },
        estimates={
            "AAA": EstimateSnapshot(
                ticker="AAA",
                as_of=as_of,
                forward_pe=20.0,
                eps_revision_90d=0.12,
            ),
            "BBB": EstimateSnapshot(
                ticker="BBB",
                as_of=as_of,
                forward_pe=33.0,
                eps_revision_90d=-0.05,
            ),
            "CCC": EstimateSnapshot(
                ticker="CCC",
                as_of=as_of,
                forward_pe=26.0,
                eps_revision_90d=0.03,
            ),
        },
    )


def test_build_composite_rankings_produces_full_six_pillar_rankings() -> None:
    settings = load_settings()
    profile = load_weight_profile("balanced")
    assemblies, rankings = build_composite_rankings(
        _full_inputs(date(2026, 1, 31)),
        tickers=["AAA", "BBB", "CCC"],
        as_of=date(2026, 1, 31),
        profile=profile,
        min_required_pillars=settings.ranking.min_required_pillars,
        penalty_rules=[MinimumQualityPenalty()],
    )

    assert [assembly.available_pillar_count for assembly in assemblies] == [6, 6, 6]
    assert all(assembly.meets_minimum_pillars for assembly in assemblies)
    assert [result.ticker for result in rankings] == ["AAA", "CCC", "BBB"]
    assert set(rankings[0].pillar_scores) == {"RP", "G", "Q", "V", "R", "S"}
    assert rankings[-1].total_penalty == profile.penalties.rules["minimum_quality"]


def test_build_composite_rankings_excludes_tickers_with_missing_pillar_scores() -> None:
    settings = load_settings()
    profile = load_weight_profile("balanced")
    inputs = _full_inputs(date(2026, 1, 31))
    inputs.returns_6m = {"AAA": 0.30, "BBB": 0.10, "CCC": None}

    assemblies, rankings = build_composite_rankings(
        inputs,
        tickers=["AAA", "BBB", "CCC"],
        as_of=date(2026, 1, 31),
        profile=profile,
        min_required_pillars=settings.ranking.min_required_pillars,
        penalty_rules=[MinimumQualityPenalty()],
    )

    assembly_by_ticker = {assembly.ticker: assembly for assembly in assemblies}
    assert assembly_by_ticker["CCC"].available_pillar_count == 5
    assert assembly_by_ticker["CCC"].missing_pillars == ["RP"]
    assert assembly_by_ticker["CCC"].meets_minimum_pillars is False
    assert [result.ticker for result in rankings] == ["AAA", "BBB"]


def test_build_explanation_cards_derives_strengths_and_risks_from_rankings() -> None:
    settings = load_settings()
    assemblies, rankings = build_composite_rankings(
        _full_inputs(date(2026, 1, 31)),
        tickers=["AAA", "BBB", "CCC"],
        as_of=date(2026, 1, 31),
        profile=load_weight_profile("balanced"),
        min_required_pillars=settings.ranking.min_required_pillars,
        penalty_rules=[MinimumQualityPenalty()],
    )
    cards = build_explanation_cards(rankings, assemblies)

    assert cards[0].ticker == "AAA"
    assert cards[0].strengths
    assert "Final score" in cards[0].summary
    assert any(item.startswith("penalty:minimum_quality") for item in cards[-1].risks)


def test_run_validation_backtest_models_turnover_costs_and_benchmark() -> None:
    settings = load_settings()
    profile = load_weight_profile("balanced")
    _, january_rankings = build_composite_rankings(
        _full_inputs(date(2026, 1, 31)),
        tickers=["AAA", "BBB", "CCC"],
        as_of=date(2026, 1, 31),
        profile=profile,
        min_required_pillars=settings.ranking.min_required_pillars,
        penalty_rules=[MinimumQualityPenalty()],
    )
    feb_inputs = _full_inputs(date(2026, 2, 28))
    feb_inputs.returns_6m = {"AAA": 0.28, "BBB": 0.14, "CCC": 0.19}
    feb_inputs.volatility_3m = {"AAA": 0.20, "BBB": 0.29, "CCC": 0.23}
    feb_inputs.fundamentals = {
        "AAA": FundamentalSnapshot(
            ticker="AAA",
            as_of=date(2026, 2, 28),
            revenue_growth_yoy=0.22,
            return_on_equity=0.20,
        ),
        "BBB": FundamentalSnapshot(
            ticker="BBB",
            as_of=date(2026, 2, 28),
            revenue_growth_yoy=0.09,
            return_on_equity=0.10,
        ),
        "CCC": FundamentalSnapshot(
            ticker="CCC",
            as_of=date(2026, 2, 28),
            revenue_growth_yoy=0.17,
            return_on_equity=0.16,
        ),
    }
    feb_inputs.estimates = {
        "AAA": EstimateSnapshot(
            ticker="AAA",
            as_of=date(2026, 2, 28),
            forward_pe=21.0,
            eps_revision_90d=0.08,
        ),
        "BBB": EstimateSnapshot(
            ticker="BBB",
            as_of=date(2026, 2, 28),
            forward_pe=30.0,
            eps_revision_90d=0.01,
        ),
        "CCC": EstimateSnapshot(
            ticker="CCC",
            as_of=date(2026, 2, 28),
            forward_pe=24.0,
            eps_revision_90d=0.04,
        ),
    }
    _, february_rankings = build_composite_rankings(
        feb_inputs,
        tickers=["AAA", "BBB", "CCC"],
        as_of=date(2026, 2, 28),
        profile=profile,
        min_required_pillars=settings.ranking.min_required_pillars,
        penalty_rules=[MinimumQualityPenalty()],
    )

    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=january_rankings,
                realized_returns={"AAA": 0.04, "BBB": -0.02, "CCC": 0.01},
                benchmark_return=0.012,
            ),
            ValidationPeriodInput(
                as_of=date(2026, 2, 28),
                ranking_results=february_rankings,
                realized_returns={"AAA": 0.01, "BBB": 0.03, "CCC": -0.01},
                benchmark_return=0.009,
            ),
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
    )

    assert report.benchmark_name == "sample_sector_benchmark"
    assert len(report.periods) == 2
    assert report.periods[0].turnover == pytest.approx(1.0)
    assert report.periods[0].buy_turnover == pytest.approx(1.0)
    assert report.periods[0].sell_turnover == pytest.approx(0.0)
    assert report.periods[0].selected_tickers == ["AAA", "CCC"]
    assert report.periods[0].cash_weight == pytest.approx(0.0)
    assert report.average_turnover >= 0
    assert report.cumulative_excess_return == pytest.approx(
        report.cumulative_portfolio_net_return - report.cumulative_benchmark_return
    )


def test_run_validation_backtest_preserves_cash_when_fewer_than_top_k_rankings() -> None:
    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=[
                    _ranking_result("AAA", date(2026, 1, 31), final_score=90.0),
                ],
                realized_returns={"AAA": 0.04},
                benchmark_return=0.01,
            ),
            ValidationPeriodInput(
                as_of=date(2026, 2, 28),
                ranking_results=[
                    _ranking_result("AAA", date(2026, 2, 28), final_score=88.0),
                    _ranking_result("BBB", date(2026, 2, 28), final_score=82.0),
                ],
                realized_returns={"AAA": 0.02, "BBB": 0.03},
                benchmark_return=0.005,
            ),
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
    )

    first_period = report.periods[0]
    assert first_period.requested_top_k == 2
    assert first_period.available_rankings == 1
    assert first_period.selected_count == 1
    assert first_period.invested_weight == pytest.approx(0.5)
    assert first_period.cash_weight == pytest.approx(0.5)
    assert first_period.portfolio_gross_return == pytest.approx(0.02)
    assert first_period.buy_turnover == pytest.approx(0.5)
    assert first_period.sell_turnover == pytest.approx(0.0)
    assert first_period.turnover == pytest.approx(0.5)

    second_period = report.periods[1]
    assert second_period.invested_weight == pytest.approx(1.0)
    assert second_period.cash_weight == pytest.approx(0.0)
    assert second_period.buy_turnover == pytest.approx(0.5)
    assert second_period.sell_turnover == pytest.approx(0.0)
    assert second_period.turnover == pytest.approx(0.5)
    assert "unallocated_cash_when_fewer_than_top_k_rankings" in report.assumptions
    assert "cash_earns_zero_return_when_portfolio_is_underfilled" in report.limitations


def _ranking_result(ticker: str, as_of: date, *, final_score: float) -> RankingResult:
    return RankingResult(
        ticker=ticker,
        as_of=as_of,
        profile_name="balanced",
        weighted_score=final_score,
        total_penalty=0.0,
        final_score=final_score,
        pillar_scores={"RP": final_score},
    )
