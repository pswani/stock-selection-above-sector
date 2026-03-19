from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd

from stock_selection.backtest.validation import ValidationReport
from stock_selection.explainability import ExplanationCard, ExplanationPillarDetail
from stock_selection.models import PillarScoreCard, RankingResult
from stock_selection.scoring.composite import PillarScoreAssembly
from stock_selection.scoring.relative_performance import RelativePerformancePreviewRank

PILLAR_SCORE_CARD_BASE_COLUMNS = [
    "ticker",
    "pillar",
    "score",
    "coverage_ratio",
    "as_of",
]
RANKING_RESULT_BASE_COLUMNS = [
    "ticker",
    "as_of",
    "profile_name",
    "weighted_score",
    "total_penalty",
    "final_score",
    "penalty_count",
]
PILLAR_ASSEMBLY_BASE_COLUMNS = [
    "ticker",
    "as_of",
    "available_pillar_count",
    "min_required_pillars",
    "meets_minimum_pillars",
    "assembly_status",
    "missing_pillars",
]
RP_PREVIEW_BASE_COLUMNS = [
    "ticker",
    "as_of",
    "preview_rank",
    "score",
    "assembly_status",
    "meets_minimum_pillars",
    "missing_pillars",
    "ranking_status",
]
EXPLANATION_CARD_BASE_COLUMNS = [
    "ticker",
    "as_of",
    "profile_name",
    "rank_position",
    "available_pillar_count",
    "minimum_required_pillars",
    "meets_minimum_pillars",
    "missing_pillar_count",
    "penalty_count",
    "score_gap_to_next_rank",
    "final_score",
    "weighted_score",
    "total_penalty",
    "assembly_status",
    "missing_pillars",
    "penalty_rules",
    "summary",
    "strengths",
    "risks",
]
VALIDATION_SUMMARY_BASE_COLUMNS = [
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
VALIDATION_PERIOD_BASE_COLUMNS = [
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


def pillar_score_cards_to_frame(cards: list[PillarScoreCard]) -> pd.DataFrame:
    diagnostic_columns = _prefixed_union_columns(
        dictionaries=[card.diagnostics for card in cards],
        prefix="diagnostic_",
    )
    rows = []
    for card in cards:
        rows.append(
            {
                "ticker": card.ticker,
                "pillar": card.pillar,
                "score": card.score,
                "coverage_ratio": card.coverage_ratio,
                "as_of": card.as_of.isoformat() if card.as_of is not None else None,
                **{f"diagnostic_{key}": value for key, value in card.diagnostics.items()},
            }
        )
    columns = [*PILLAR_SCORE_CARD_BASE_COLUMNS, *diagnostic_columns]
    return pd.DataFrame(rows, columns=columns)


def ranking_results_to_frame(results: list[RankingResult]) -> pd.DataFrame:
    pillar_columns = _prefixed_union_columns(
        dictionaries=[result.pillar_scores for result in results],
        prefix="pillar_",
    )
    rows = []
    for result in results:
        rows.append(
            {
                "ticker": result.ticker,
                "as_of": result.as_of.isoformat(),
                "profile_name": result.profile_name,
                "weighted_score": result.weighted_score,
                "total_penalty": result.total_penalty,
                "final_score": result.final_score,
                **{f"pillar_{k}": v for k, v in result.pillar_scores.items()},
                "penalty_count": len(result.penalty_traces),
            }
        )
    columns = [*RANKING_RESULT_BASE_COLUMNS, *pillar_columns]
    return pd.DataFrame(rows, columns=columns)


def pillar_score_assemblies_to_frame(
    assemblies: list[PillarScoreAssembly],
) -> pd.DataFrame:
    score_columns = _prefixed_union_columns(
        dictionaries=[assembly.pillar_scores for assembly in assemblies],
        prefix="pillar_score_",
    )
    coverage_columns = _prefixed_union_columns(
        dictionaries=[assembly.pillar_coverages for assembly in assemblies],
        prefix="pillar_coverage_",
    )
    rows = []
    for assembly in assemblies:
        rows.append(
            {
                "ticker": assembly.ticker,
                "as_of": assembly.as_of.isoformat() if assembly.as_of is not None else None,
                "available_pillar_count": assembly.available_pillar_count,
                "min_required_pillars": assembly.min_required_pillars,
                "meets_minimum_pillars": assembly.meets_minimum_pillars,
                "assembly_status": assembly.assembly_status,
                "missing_pillars": ",".join(assembly.missing_pillars),
                **{
                    f"pillar_score_{pillar}": score
                    for pillar, score in assembly.pillar_scores.items()
                },
                **{
                    f"pillar_coverage_{pillar}": coverage
                    for pillar, coverage in assembly.pillar_coverages.items()
                },
            }
        )
    columns = [
        *PILLAR_ASSEMBLY_BASE_COLUMNS,
        *score_columns,
        *coverage_columns,
    ]
    return pd.DataFrame(rows, columns=columns)


def relative_performance_preview_ranks_to_frame(
    preview_ranks: list[RelativePerformancePreviewRank],
) -> pd.DataFrame:
    rows = []
    for preview in preview_ranks:
        rows.append(
            {
                "ticker": preview.ticker,
                "as_of": preview.as_of.isoformat() if preview.as_of is not None else None,
                "preview_rank": preview.preview_rank,
                "score": preview.score,
                "assembly_status": preview.assembly_status,
                "meets_minimum_pillars": preview.meets_minimum_pillars,
                "missing_pillars": ",".join(preview.missing_pillars),
                "ranking_status": preview.ranking_status,
            }
        )
    return pd.DataFrame(rows, columns=RP_PREVIEW_BASE_COLUMNS)


def explanation_cards_to_frame(cards: list[ExplanationCard]) -> pd.DataFrame:
    top_pillar_columns = _detail_columns(cards, attribute="top_pillars")
    weakest_pillar_columns = _detail_columns(cards, attribute="weakest_pillars")
    rows = []
    for card in cards:
        row = {
            "ticker": card.ticker,
            "as_of": card.as_of.isoformat(),
            "profile_name": card.profile_name,
            "rank_position": card.rank_position,
            "available_pillar_count": card.available_pillar_count,
            "minimum_required_pillars": card.minimum_required_pillars,
            "meets_minimum_pillars": card.meets_minimum_pillars,
            "missing_pillar_count": card.missing_pillar_count,
            "penalty_count": card.penalty_count,
            "score_gap_to_next_rank": card.score_gap_to_next_rank,
            "final_score": card.final_score,
            "weighted_score": card.weighted_score,
            "total_penalty": card.total_penalty,
            "assembly_status": card.assembly_status,
            "missing_pillars": ",".join(card.missing_pillars),
            "penalty_rules": ",".join(card.penalty_rules),
            "summary": card.summary,
            "strengths": "|".join(card.strengths),
            "risks": "|".join(card.risks),
        }
        row.update(_detail_values(card.top_pillars, prefix="top_pillars"))
        row.update(_detail_values(card.weakest_pillars, prefix="weakest_pillars"))
        rows.append(row)
    columns = [
        *EXPLANATION_CARD_BASE_COLUMNS,
        *top_pillar_columns,
        *weakest_pillar_columns,
    ]
    return pd.DataFrame(rows, columns=columns)


def validation_report_summary_to_frame(report: ValidationReport) -> pd.DataFrame:
    rows = [
        {
            "benchmark_name": report.benchmark_name,
            "benchmark_type": report.benchmark_type,
            "benchmark_methodology": report.benchmark_methodology,
            "benchmark_return_alignment": report.benchmark_return_alignment,
            "top_k": report.top_k,
            "transaction_cost_bps": report.transaction_cost_bps,
            "period_count": len(report.periods),
            "periods_with_underfill": report.periods_with_underfill,
            "max_cash_weight": report.max_cash_weight,
            "min_holding_period_days": report.min_holding_period_days,
            "max_holding_period_days": report.max_holding_period_days,
            "average_turnover": report.average_turnover,
            "cumulative_portfolio_net_return": report.cumulative_portfolio_net_return,
            "cumulative_benchmark_return": report.cumulative_benchmark_return,
            "cumulative_excess_return": report.cumulative_excess_return,
            "assumptions": "|".join(report.assumptions),
            "limitations": "|".join(report.limitations),
        }
    ]
    return pd.DataFrame(rows, columns=VALIDATION_SUMMARY_BASE_COLUMNS)


def validation_report_periods_to_frame(report: ValidationReport) -> pd.DataFrame:
    rows = []
    for period in report.periods:
        rows.append(
            {
                "benchmark_name": report.benchmark_name,
                "benchmark_type": report.benchmark_type,
                "benchmark_methodology": report.benchmark_methodology,
                "benchmark_return_alignment": report.benchmark_return_alignment,
                "top_k": report.top_k,
                "transaction_cost_bps": report.transaction_cost_bps,
                "periods_with_underfill": report.periods_with_underfill,
                "max_cash_weight": report.max_cash_weight,
                "period_index": period.period_index,
                "as_of": period.as_of.isoformat(),
                "next_rebalance_as_of": (
                    period.next_rebalance_as_of.isoformat()
                    if period.next_rebalance_as_of is not None
                    else None
                ),
                "holding_period_days": period.holding_period_days,
                "requested_top_k": period.requested_top_k,
                "available_rankings": period.available_rankings,
                "selected_count": period.selected_count,
                "selection_fill_ratio": period.selection_fill_ratio,
                "underfilled": period.underfilled,
                "selected_tickers": ",".join(period.selected_tickers),
                "invested_weight": period.invested_weight,
                "cash_weight": period.cash_weight,
                "portfolio_gross_return": period.portfolio_gross_return,
                "buy_turnover": period.buy_turnover,
                "sell_turnover": period.sell_turnover,
                "turnover": period.turnover,
                "transaction_cost": period.transaction_cost,
                "portfolio_net_return": period.portfolio_net_return,
                "benchmark_return": period.benchmark_return,
                "excess_return": period.excess_return,
                "benchmark_relative_gap_bps": period.benchmark_relative_gap_bps,
            }
        )
    return pd.DataFrame(rows, columns=VALIDATION_PERIOD_BASE_COLUMNS)


def write_ranking_csv(results: list[RankingResult], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    ranking_results_to_frame(results).to_csv(output, index=False)
    return output


def write_pillar_score_cards_csv(cards: list[PillarScoreCard], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pillar_score_cards_to_frame(cards).to_csv(output, index=False)
    return output


def write_pillar_score_assemblies_csv(
    assemblies: list[PillarScoreAssembly],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pillar_score_assemblies_to_frame(assemblies).to_csv(output, index=False)
    return output


def write_relative_performance_preview_csv(
    preview_ranks: list[RelativePerformancePreviewRank],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    relative_performance_preview_ranks_to_frame(preview_ranks).to_csv(output, index=False)
    return output


def write_explanation_cards_csv(cards: list[ExplanationCard], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    explanation_cards_to_frame(cards).to_csv(output, index=False)
    return output


def write_validation_report_periods_csv(
    report: ValidationReport,
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    validation_report_periods_to_frame(report).to_csv(output, index=False)
    return output


def write_validation_report_summary_csv(
    report: ValidationReport,
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    validation_report_summary_to_frame(report).to_csv(output, index=False)
    return output


def write_validation_report_bundle_csvs(
    report: ValidationReport,
    *,
    output_prefix: str | Path,
) -> tuple[Path, Path]:
    prefix = Path(output_prefix)
    summary_path = write_validation_report_summary_csv(
        report,
        prefix.parent / f"{prefix.name}-summary.csv",
    )
    periods_path = write_validation_report_periods_csv(
        report,
        prefix.parent / f"{prefix.name}-periods.csv",
    )
    return summary_path, periods_path


def _prefixed_union_columns(
    *,
    dictionaries: Sequence[Mapping[str, object]],
    prefix: str,
) -> list[str]:
    keys = sorted({key for mapping in dictionaries for key in mapping})
    return [f"{prefix}{key}" for key in keys]


def _detail_columns(cards: list[ExplanationCard], *, attribute: str) -> list[str]:
    max_items = max((len(getattr(card, attribute)) for card in cards), default=0)
    columns: list[str] = []
    for index in range(max_items):
        columns.append(f"{attribute}_{index + 1}_pillar")
        columns.append(f"{attribute}_{index + 1}_score")
    return columns


def _detail_values(
    details: Sequence[ExplanationPillarDetail],
    *,
    prefix: str,
) -> dict[str, object]:
    values: dict[str, object] = {}
    for index, detail in enumerate(details, start=1):
        values[f"{prefix}_{index}_pillar"] = detail.pillar
        values[f"{prefix}_{index}_score"] = detail.score
    return values
