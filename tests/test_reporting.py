from datetime import date
from pathlib import Path

from stock_selection.backtest.validation import (
    BenchmarkType,
    ValidationPeriodInput,
    run_validation_backtest,
)
from stock_selection.explainability import ExplanationCard, ExplanationPillarDetail
from stock_selection.models import PillarScoreCard, RankingResult
from stock_selection.reporting import (
    explanation_cards_to_frame,
    pillar_score_assemblies_to_frame,
    pillar_score_cards_to_frame,
    ranking_results_to_frame,
    relative_performance_preview_ranks_to_frame,
    validation_report_periods_to_frame,
    validation_report_summary_to_frame,
    write_explanation_cards_csv,
    write_pillar_score_assemblies_csv,
    write_pillar_score_cards_csv,
    write_ranking_csv,
    write_relative_performance_preview_csv,
    write_validation_report_bundle_csvs,
    write_validation_report_periods_csv,
    write_validation_report_summary_csv,
)
from stock_selection.scoring import (
    RelativePerformancePillarEngine,
    assemble_pillar_score_cards,
    rank_relative_performance_assemblies,
)


def test_ranking_results_to_frame() -> None:
    result = RankingResult(
        ticker="NVDA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=5,
        final_score=75,
        pillar_scores={"RP": 90, "G": 80},
    )
    frame = ranking_results_to_frame([result])
    assert frame.loc[0, "ticker"] == "NVDA"
    assert frame.loc[0, "penalty_count"] == 0


def test_write_ranking_csv(tmp_path: Path) -> None:
    result = RankingResult(
        ticker="NVDA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=5,
        final_score=75,
        pillar_scores={"RP": 90},
    )
    path = write_ranking_csv([result], tmp_path / "ranking.csv")
    assert path.exists()


def test_ranking_results_to_frame_has_deterministic_dynamic_columns() -> None:
    first = RankingResult(
        ticker="AAA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=0,
        final_score=80,
        pillar_scores={"S": 50, "RP": 90},
    )
    second = RankingResult(
        ticker="BBB",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=70,
        total_penalty=0,
        final_score=70,
        pillar_scores={"G": 60},
    )

    frame = ranking_results_to_frame([first, second])

    assert frame.columns.tolist() == [
        "ticker",
        "as_of",
        "profile_name",
        "weighted_score",
        "total_penalty",
        "final_score",
        "penalty_count",
        "pillar_G",
        "pillar_RP",
        "pillar_S",
    ]


def test_pillar_score_cards_to_frame() -> None:
    card = PillarScoreCard(
        ticker="AAA",
        pillar="RP",
        score=100,
        coverage_ratio=1.0,
        diagnostics={"normalization_status": "ok", "peer_group": "sector:tech"},
        as_of=date(2026, 1, 31),
    )

    frame = pillar_score_cards_to_frame([card])

    assert frame.loc[0, "ticker"] == "AAA"
    assert frame.loc[0, "diagnostic_normalization_status"] == "ok"
    assert frame.loc[0, "diagnostic_peer_group"] == "sector:tech"


def test_write_pillar_score_cards_csv(tmp_path: Path) -> None:
    card = PillarScoreCard(
        ticker="AAA",
        pillar="RP",
        score=100,
        coverage_ratio=1.0,
        diagnostics={"normalization_status": "ok"},
        as_of=date(2026, 1, 31),
    )

    path = write_pillar_score_cards_csv([card], tmp_path / "rp.csv")

    assert path.exists()


def test_pillar_score_cards_to_frame_has_schema_for_empty_input() -> None:
    frame = pillar_score_cards_to_frame([])

    assert frame.columns.tolist() == [
        "ticker",
        "pillar",
        "score",
        "coverage_ratio",
        "as_of",
    ]


def test_pillar_score_assemblies_to_frame_integrates_relative_performance_path() -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=2)

    frame = pillar_score_assemblies_to_frame(assemblies)

    assert frame.columns.tolist() == [
        "ticker",
        "as_of",
        "available_pillar_count",
        "min_required_pillars",
        "meets_minimum_pillars",
        "assembly_status",
        "missing_pillars",
        "pillar_score_RP",
        "pillar_coverage_RP",
    ]
    assert frame["assembly_status"].tolist() == [
        "insufficient_pillars",
        "insufficient_pillars",
    ]
    assert frame.loc[0, "missing_pillars"] == "G,Q,V,R,S"


def test_write_pillar_score_assemblies_csv(tmp_path: Path) -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=1)

    path = write_pillar_score_assemblies_csv(assemblies, tmp_path / "assembly.csv")

    assert path.exists()


def test_relative_performance_preview_ranks_to_frame() -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=1)
    preview = rank_relative_performance_assemblies(assemblies)

    frame = relative_performance_preview_ranks_to_frame(preview)

    assert frame.columns.tolist() == [
        "ticker",
        "as_of",
        "preview_rank",
        "score",
        "assembly_status",
        "meets_minimum_pillars",
        "missing_pillars",
        "ranking_status",
    ]
    assert frame.loc[0, "ranking_status"] == "preview_ranked"


def test_write_relative_performance_preview_csv(tmp_path: Path) -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    preview = engine.preview_rankings(
        ["AAA", "BBB"],
        as_of=date(2026, 1, 31),
        min_required_pillars=2,
    )

    path = write_relative_performance_preview_csv(preview, tmp_path / "rp-preview.csv")

    assert path.exists()


def test_explanation_cards_to_frame_has_richer_columns() -> None:
    card = ExplanationCard(
        ticker="AAA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        rank_position=1,
        available_pillar_count=6,
        minimum_required_pillars=6,
        meets_minimum_pillars=True,
        missing_pillar_count=0,
        penalty_count=1,
        score_gap_to_next_rank=2.5,
        final_score=88.0,
        weighted_score=90.0,
        total_penalty=2.0,
        assembly_status="ok",
        missing_pillars=[],
        top_pillars=[
            ExplanationPillarDetail(pillar="G", score=100.0),
            ExplanationPillarDetail(pillar="RP", score=95.0),
        ],
        weakest_pillars=[
            ExplanationPillarDetail(pillar="V", score=55.0),
        ],
        penalty_rules=["minimum_quality"],
        summary=(
            "Final score 88.00 from weighted score 90.00 with 1 penalties "
            "and assembly status ok."
        ),
        strengths=["G=100.00", "RP=95.00"],
        risks=["V=55.00", "penalty:minimum_quality"],
    )

    frame = explanation_cards_to_frame([card])

    assert frame.loc[0, "ticker"] == "AAA"
    assert frame.loc[0, "profile_name"] == "balanced"
    assert frame.loc[0, "rank_position"] == 1
    assert frame.loc[0, "available_pillar_count"] == 6
    assert frame.loc[0, "penalty_count"] == 1
    assert frame.loc[0, "score_gap_to_next_rank"] == 2.5
    assert frame.loc[0, "penalty_rules"] == "minimum_quality"
    assert frame.loc[0, "top_pillars_1_pillar"] == "G"
    assert frame.loc[0, "top_pillars_2_score"] == 95.0
    assert frame.loc[0, "weakest_pillars_1_pillar"] == "V"


def test_write_explanation_cards_csv(tmp_path: Path) -> None:
    card = ExplanationCard(
        ticker="AAA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        rank_position=1,
        available_pillar_count=6,
        minimum_required_pillars=6,
        meets_minimum_pillars=True,
        missing_pillar_count=0,
        penalty_count=1,
        score_gap_to_next_rank=2.5,
        final_score=88.0,
        weighted_score=90.0,
        total_penalty=2.0,
        assembly_status="ok",
        missing_pillars=[],
        top_pillars=[ExplanationPillarDetail(pillar="G", score=100.0)],
        weakest_pillars=[ExplanationPillarDetail(pillar="V", score=55.0)],
        penalty_rules=["minimum_quality"],
        summary="Summary",
        strengths=["G=100.00"],
        risks=["V=55.00"],
    )

    path = write_explanation_cards_csv([card], tmp_path / "explanations.csv")

    assert path.exists()


def test_validation_report_periods_to_frame_exposes_benchmark_and_cash_diagnostics() -> None:
    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=[
                    RankingResult(
                        ticker="AAA",
                        as_of=date(2026, 1, 31),
                        profile_name="balanced",
                        weighted_score=90.0,
                        total_penalty=0.0,
                        final_score=90.0,
                        pillar_scores={"RP": 90.0},
                    )
                ],
                realized_returns={"AAA": 0.04},
                benchmark_return=0.01,
            )
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
        benchmark_type=BenchmarkType.SECTOR_PEER_AVERAGE,
        benchmark_methodology="sample_sector_average_total_return",
    )

    frame = validation_report_periods_to_frame(report)

    assert frame.columns.tolist() == [
        "benchmark_name",
        "benchmark_type",
        "benchmark_methodology",
        "benchmark_return_alignment",
        "top_k",
        "transaction_cost_bps",
        "periods_with_underfill",
        "max_cash_weight",
        "period_index",
        "as_of",
        "next_rebalance_as_of",
        "holding_period_days",
        "requested_top_k",
        "available_rankings",
        "selected_count",
        "selection_fill_ratio",
        "underfilled",
        "selected_tickers",
        "invested_weight",
        "cash_weight",
        "portfolio_gross_return",
        "buy_turnover",
        "sell_turnover",
        "turnover",
        "transaction_cost",
        "portfolio_net_return",
        "benchmark_return",
        "excess_return",
        "benchmark_relative_gap_bps",
    ]
    assert frame.loc[0, "benchmark_name"] == "sample_sector_benchmark"
    assert frame.loc[0, "benchmark_type"] == BenchmarkType.SECTOR_PEER_AVERAGE
    assert frame.loc[0, "cash_weight"] == 0.5
    assert frame.loc[0, "next_rebalance_as_of"] is None
    assert bool(frame.loc[0, "underfilled"]) is True
    assert frame.loc[0, "benchmark_relative_gap_bps"] == 95.0


def test_validation_report_summary_to_frame_exposes_assumptions_and_periodization() -> None:
    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=[
                    RankingResult(
                        ticker="AAA",
                        as_of=date(2026, 1, 31),
                        profile_name="balanced",
                        weighted_score=90.0,
                        total_penalty=0.0,
                        final_score=90.0,
                        pillar_scores={"RP": 90.0},
                    )
                ],
                realized_returns={"AAA": 0.04},
                benchmark_return=0.01,
            )
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
        benchmark_type=BenchmarkType.SECTOR_ETF,
        benchmark_methodology="sample_sector_etf_total_return",
    )

    frame = validation_report_summary_to_frame(report)

    assert frame.columns.tolist() == [
        "benchmark_name",
        "benchmark_type",
        "benchmark_methodology",
        "benchmark_return_alignment",
        "top_k",
        "transaction_cost_bps",
        "period_count",
        "periods_with_underfill",
        "max_cash_weight",
        "min_holding_period_days",
        "max_holding_period_days",
        "average_turnover",
        "cumulative_portfolio_net_return",
        "cumulative_benchmark_return",
        "cumulative_excess_return",
        "assumptions",
        "limitations",
    ]
    assert frame.loc[0, "period_count"] == 1
    assert frame.loc[0, "benchmark_type"] == BenchmarkType.SECTOR_ETF
    assert frame.loc[0, "benchmark_methodology"] == "sample_sector_etf_total_return"
    assert "unallocated_cash_when_fewer_than_top_k_rankings" in frame.loc[0, "assumptions"]


def test_write_validation_report_periods_csv(tmp_path: Path) -> None:
    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=[
                    RankingResult(
                        ticker="AAA",
                        as_of=date(2026, 1, 31),
                        profile_name="balanced",
                        weighted_score=90.0,
                        total_penalty=0.0,
                        final_score=90.0,
                        pillar_scores={"RP": 90.0},
                    )
                ],
                realized_returns={"AAA": 0.04},
                benchmark_return=0.01,
            )
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
    )

    path = write_validation_report_periods_csv(report, tmp_path / "validation-periods.csv")

    assert path.exists()


def test_write_validation_report_summary_csv(tmp_path: Path) -> None:
    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=[
                    RankingResult(
                        ticker="AAA",
                        as_of=date(2026, 1, 31),
                        profile_name="balanced",
                        weighted_score=90.0,
                        total_penalty=0.0,
                        final_score=90.0,
                        pillar_scores={"RP": 90.0},
                    )
                ],
                realized_returns={"AAA": 0.04},
                benchmark_return=0.01,
            )
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
    )

    path = write_validation_report_summary_csv(report, tmp_path / "validation-summary.csv")

    assert path.exists()


def test_write_validation_report_bundle_csvs(tmp_path: Path) -> None:
    report = run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=[
                    RankingResult(
                        ticker="AAA",
                        as_of=date(2026, 1, 31),
                        profile_name="balanced",
                        weighted_score=90.0,
                        total_penalty=0.0,
                        final_score=90.0,
                        pillar_scores={"RP": 90.0},
                    )
                ],
                realized_returns={"AAA": 0.04},
                benchmark_return=0.01,
            )
        ],
        top_k=1,
        transaction_cost_bps=10.0,
        benchmark_name="sample_sector_benchmark",
    )

    summary_path, periods_path = write_validation_report_bundle_csvs(
        report,
        output_prefix=tmp_path / "bundle/validation",
    )

    assert summary_path.exists()
    assert periods_path.exists()
