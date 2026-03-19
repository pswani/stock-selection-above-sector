from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator

from stock_selection.models import RankingResult


class ValidationPeriodInput(BaseModel):
    as_of: date
    ranking_results: list[RankingResult]
    realized_returns: dict[str, float] = Field(default_factory=dict)
    benchmark_return: float

    @field_validator("ranking_results")
    @classmethod
    def ranking_results_not_empty(cls, value: list[RankingResult]) -> list[RankingResult]:
        if not value:
            raise ValueError("Validation period input requires at least one ranking result")
        tickers = [result.ticker for result in value]
        if len(tickers) != len(set(tickers)):
            raise ValueError(
                "Validation period input requires unique ranking-result tickers per period"
            )
        return value


class ValidationPeriodResult(BaseModel):
    as_of: date
    next_rebalance_as_of: date | None = None
    holding_period_days: int | None = Field(default=None, ge=1)
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
    benchmark_relative_gap_bps: float


class ValidationReport(BaseModel):
    benchmark_name: str
    top_k: int = Field(ge=1)
    transaction_cost_bps: float = Field(ge=0)
    periods_with_underfill: int = Field(ge=0)
    max_cash_weight: float = Field(ge=0, le=1)
    min_holding_period_days: int | None = Field(default=None, ge=1)
    max_holding_period_days: int | None = Field(default=None, ge=1)
    periods: list[ValidationPeriodResult] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    average_turnover: float = Field(ge=0)
    cumulative_portfolio_net_return: float
    cumulative_benchmark_return: float
    cumulative_excess_return: float

    @field_validator("benchmark_name")
    @classmethod
    def benchmark_name_not_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("benchmark_name must not be blank")
        return normalized


def run_validation_backtest(
    period_inputs: list[ValidationPeriodInput],
    *,
    top_k: int,
    transaction_cost_bps: float,
    benchmark_name: str,
) -> ValidationReport:
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    if not benchmark_name.strip():
        raise ValueError("benchmark_name must not be blank")
    ordered_inputs = sorted(period_inputs, key=lambda item: item.as_of)
    if not ordered_inputs:
        raise ValueError("Validation backtest requires at least one period input")
    if len({item.as_of for item in ordered_inputs}) != len(ordered_inputs):
        raise ValueError("Validation backtest requires unique as_of dates per period")

    periods: list[ValidationPeriodResult] = []
    previous_weights: dict[str, float] = {}
    cumulative_portfolio = 1.0
    cumulative_benchmark = 1.0

    for index, period_input in enumerate(ordered_inputs):
        _validate_period_alignment(period_input)
        next_rebalance_as_of = (
            ordered_inputs[index + 1].as_of if index + 1 < len(ordered_inputs) else None
        )
        holding_period_days = (
            (next_rebalance_as_of - period_input.as_of).days
            if next_rebalance_as_of is not None
            else None
        )
        selected = _select_top_ranked(period_input.ranking_results, top_k=top_k)
        selected_tickers = [result.ticker for result in selected]
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
        benchmark_relative_gap_bps = excess_return * 10_000.0

        periods.append(
            ValidationPeriodResult(
                as_of=period_input.as_of,
                next_rebalance_as_of=next_rebalance_as_of,
                holding_period_days=holding_period_days,
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
                benchmark_relative_gap_bps=benchmark_relative_gap_bps,
            )
        )

        cumulative_portfolio *= 1.0 + net_return
        cumulative_benchmark *= 1.0 + period_input.benchmark_return
        previous_weights = current_weights

    average_turnover = sum(period.turnover for period in periods) / len(periods)
    periods_with_underfill = sum(1 for period in periods if period.cash_weight > 0)
    max_cash_weight = max(period.cash_weight for period in periods)
    holding_period_values = [
        period.holding_period_days
        for period in periods
        if period.holding_period_days is not None
    ]
    cumulative_portfolio_return = cumulative_portfolio - 1.0
    cumulative_benchmark_return = cumulative_benchmark - 1.0
    cumulative_excess_return = cumulative_portfolio_return - cumulative_benchmark_return

    return ValidationReport(
        benchmark_name=benchmark_name.strip(),
        top_k=top_k,
        transaction_cost_bps=transaction_cost_bps,
        periods_with_underfill=periods_with_underfill,
        max_cash_weight=max_cash_weight,
        min_holding_period_days=min(holding_period_values, default=None),
        max_holding_period_days=max(holding_period_values, default=None),
        periods=periods,
        assumptions=[
            "equal_weight_top_k_selection",
            "rebalance_on_each_as_of_snapshot",
            "transaction_costs_applied_from_turnover",
            "realized_returns_supplied_externally_and_assumed_forward_aligned",
            "benchmark_return_assumed_forward_aligned_to_same_period",
            "next_rebalance_as_of_used_as_period_end_when_subsequent_period_exists",
            "unallocated_cash_when_fewer_than_top_k_rankings",
        ],
        limitations=[
            "no_live_data_validation",
            "no_slippage_model_beyond_transaction_cost_bps",
            "benchmark_return_must_be_supplied_explicitly",
            "benchmark_series_type_and_construction_are_external_to_this_harness",
            "cash_earns_zero_return_when_portfolio_is_underfilled",
            "final_period_has_no_inferred_period_end_without_a_subsequent_rebalance_date",
        ],
        average_turnover=average_turnover,
        cumulative_portfolio_net_return=cumulative_portfolio_return,
        cumulative_benchmark_return=cumulative_benchmark_return,
        cumulative_excess_return=cumulative_excess_return,
    )


def _validate_period_alignment(period_input: ValidationPeriodInput) -> None:
    mismatched = sorted(
        result.ticker
        for result in period_input.ranking_results
        if result.as_of != period_input.as_of
    )
    if mismatched:
        raise ValueError(
            "Validation backtest requires ranking_results as_of to match the period input "
            f"(as_of={period_input.as_of.isoformat()}, mismatched={mismatched})"
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
