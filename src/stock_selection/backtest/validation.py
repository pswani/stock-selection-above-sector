from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from stock_selection.models import RankingResult


class ValidationPeriodInput(BaseModel):
    as_of: date
    ranking_results: list[RankingResult]
    realized_returns: dict[str, float] = Field(default_factory=dict)
    benchmark_return: float


class ValidationPeriodResult(BaseModel):
    as_of: date
    requested_top_k: int = Field(ge=1)
    available_rankings: int = Field(ge=0)
    selected_count: int = Field(ge=1)
    selected_tickers: list[str]
    invested_weight: float = Field(ge=0, le=1)
    cash_weight: float = Field(ge=0, le=1)
    portfolio_gross_return: float
    buy_turnover: float = Field(ge=0)
    sell_turnover: float = Field(ge=0)
    turnover: float = Field(ge=0)
    transaction_cost: float = Field(ge=0)
    portfolio_net_return: float
    benchmark_return: float
    excess_return: float


class ValidationReport(BaseModel):
    benchmark_name: str
    top_k: int = Field(ge=1)
    transaction_cost_bps: float = Field(ge=0)
    periods: list[ValidationPeriodResult] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    average_turnover: float = Field(ge=0)
    cumulative_portfolio_net_return: float
    cumulative_benchmark_return: float
    cumulative_excess_return: float


def run_validation_backtest(
    period_inputs: list[ValidationPeriodInput],
    *,
    top_k: int,
    transaction_cost_bps: float,
    benchmark_name: str,
) -> ValidationReport:
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    ordered_inputs = sorted(period_inputs, key=lambda item: item.as_of)
    if not ordered_inputs:
        raise ValueError("Validation backtest requires at least one period input")

    periods: list[ValidationPeriodResult] = []
    previous_weights: dict[str, float] = {}
    cumulative_portfolio = 1.0
    cumulative_benchmark = 1.0

    for period_input in ordered_inputs:
        selected = _select_top_ranked(period_input.ranking_results, top_k=top_k)
        selected_tickers = [result.ticker for result in selected]
        if not selected_tickers:
            raise ValueError(
                "Validation backtest requires at least one ranking result per period"
            )

        missing_returns = sorted(
            ticker for ticker in selected_tickers if ticker not in period_input.realized_returns
        )
        if missing_returns:
            raise ValueError(
                "Validation backtest missing realized returns for selected tickers "
                f"(missing={missing_returns}, as_of={period_input.as_of.isoformat()})"
            )

        target_weight = 1.0 / top_k
        current_weights = {ticker: target_weight for ticker in selected_tickers}
        buy_turnover, sell_turnover, turnover = _calculate_turnover_components(
            previous_weights,
            current_weights,
        )
        invested_weight = sum(current_weights.values())
        cash_weight = 1.0 - invested_weight
        gross_return = sum(
            period_input.realized_returns[ticker] * current_weights[ticker]
            for ticker in selected_tickers
        )
        transaction_cost = turnover * (transaction_cost_bps / 10_000.0)
        net_return = gross_return - transaction_cost
        excess_return = net_return - period_input.benchmark_return

        periods.append(
            ValidationPeriodResult(
                as_of=period_input.as_of,
                requested_top_k=top_k,
                available_rankings=len(period_input.ranking_results),
                selected_count=len(selected_tickers),
                selected_tickers=selected_tickers,
                invested_weight=invested_weight,
                cash_weight=cash_weight,
                portfolio_gross_return=gross_return,
                buy_turnover=buy_turnover,
                sell_turnover=sell_turnover,
                turnover=turnover,
                transaction_cost=transaction_cost,
                portfolio_net_return=net_return,
                benchmark_return=period_input.benchmark_return,
                excess_return=excess_return,
            )
        )

        cumulative_portfolio *= 1.0 + net_return
        cumulative_benchmark *= 1.0 + period_input.benchmark_return
        previous_weights = current_weights

    average_turnover = sum(period.turnover for period in periods) / len(periods)
    cumulative_portfolio_return = cumulative_portfolio - 1.0
    cumulative_benchmark_return = cumulative_benchmark - 1.0
    cumulative_excess_return = cumulative_portfolio_return - cumulative_benchmark_return

    return ValidationReport(
        benchmark_name=benchmark_name,
        top_k=top_k,
        transaction_cost_bps=transaction_cost_bps,
        periods=periods,
        assumptions=[
            "equal_weight_top_k_selection",
            "rebalance_on_each_as_of_snapshot",
            "transaction_costs_applied_from_turnover",
            "realized_returns_supplied_externally_and_assumed_forward_aligned",
            "unallocated_cash_when_fewer_than_top_k_rankings",
        ],
        limitations=[
            "no_live_data_validation",
            "no_slippage_model_beyond_transaction_cost_bps",
            "benchmark_return_must_be_supplied_explicitly",
            "cash_earns_zero_return_when_portfolio_is_underfilled",
        ],
        average_turnover=average_turnover,
        cumulative_portfolio_net_return=cumulative_portfolio_return,
        cumulative_benchmark_return=cumulative_benchmark_return,
        cumulative_excess_return=cumulative_excess_return,
    )


def _select_top_ranked(
    ranking_results: list[RankingResult],
    *,
    top_k: int,
) -> list[RankingResult]:
    ranked = sorted(
        ranking_results,
        key=lambda result: (-result.final_score, -result.weighted_score, str(result.ticker)),
    )
    return ranked[:top_k]


def _calculate_turnover_components(
    previous_weights: dict[str, float],
    current_weights: dict[str, float],
) -> tuple[float, float, float]:
    all_tickers = set(previous_weights) | set(current_weights)
    buy_turnover = sum(
        max(current_weights.get(ticker, 0.0) - previous_weights.get(ticker, 0.0), 0.0)
        for ticker in all_tickers
    )
    sell_turnover = sum(
        max(previous_weights.get(ticker, 0.0) - current_weights.get(ticker, 0.0), 0.0)
        for ticker in all_tickers
    )
    return buy_turnover, sell_turnover, max(buy_turnover, sell_turnover)
