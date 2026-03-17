from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from stock_selection.factors import normalize_factor_output
from stock_selection.models import FactorObservation, MetricDirection, PillarScoreCard

RP_FACTOR_NAME = "relative_strength_6m"
RP_FACTOR_SOURCE = "price_returns_6m"


def build_relative_performance_observations(
    returns_6m: Mapping[str, float | None],
    peer_groups: Mapping[str, str | None],
    *,
    as_of: date,
    source: str = RP_FACTOR_SOURCE,
) -> list[FactorObservation]:
    tickers = sorted(set(returns_6m) | set(peer_groups))
    return [
        FactorObservation(
            ticker=ticker,
            factor_name=RP_FACTOR_NAME,
            value=returns_6m.get(ticker),
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group=peer_groups.get(ticker),
            as_of=as_of,
            source=source,
        )
        for ticker in tickers
    ]


def score_relative_performance(
    observations: list[FactorObservation],
) -> list[PillarScoreCard]:
    _validate_relative_performance_observations(observations)

    normalized = normalize_factor_output(observations)
    return [
        PillarScoreCard(
            ticker=observation.ticker,
            pillar="RP",
            score=observation.percentile_rank or 0.0,
            coverage_ratio=observation.coverage_ratio,
            diagnostics={
                "factor_name": observation.factor_name,
                "normalization_status": observation.normalization_status,
                "peer_group": observation.peer_group,
                "raw_value": observation.raw_value,
                "winsorized_value": observation.winsorized_value,
                "robust_zscore": observation.robust_zscore,
                "source": observation.source,
            },
            as_of=observation.as_of,
        )
        for observation in normalized
    ]


def _validate_relative_performance_observations(
    observations: list[FactorObservation],
) -> None:
    seen_tickers: set[str] = set()
    for observation in observations:
        if observation.factor_name != RP_FACTOR_NAME:
            raise ValueError(
                "Relative Performance scoring requires only "
                f"'{RP_FACTOR_NAME}' observations."
            )
        if observation.ticker in seen_tickers:
            raise ValueError(
                "Relative Performance scoring requires at most one observation per ticker."
            )
        seen_tickers.add(observation.ticker)
