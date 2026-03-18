from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date

from stock_selection.factors import normalize_factor_output
from stock_selection.models import (
    FactorObservation,
    FundamentalSnapshot,
    MetricDirection,
    PillarScoreCard,
)
from stock_selection.scoring.composite import PillarEngine

GROWTH_FACTOR_NAME = "revenue_growth_yoy"
GROWTH_FACTOR_SOURCE = "fundamentals.revenue_growth_yoy"


def build_growth_observations(
    fundamentals: Mapping[str, FundamentalSnapshot | None],
    peer_groups: Mapping[str, str | None],
    *,
    tickers: Collection[str] | None = None,
    as_of: date,
    source: str = GROWTH_FACTOR_SOURCE,
) -> list[FactorObservation]:
    ordered_tickers = (
        sorted(set(tickers))
        if tickers is not None
        else sorted(set(fundamentals) | set(peer_groups))
    )
    return [
        FactorObservation(
            ticker=ticker,
            factor_name=GROWTH_FACTOR_NAME,
            value=_revenue_growth_value(fundamentals.get(ticker), as_of=as_of),
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group=peer_groups.get(ticker),
            as_of=as_of,
            source=source,
        )
        for ticker in ordered_tickers
    ]


def score_growth(
    observations: list[FactorObservation],
) -> list[PillarScoreCard]:
    _validate_growth_observations(observations)

    normalized = normalize_factor_output(observations)
    return [
        PillarScoreCard(
            ticker=observation.ticker,
            pillar="G",
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


def _validate_growth_observations(observations: list[FactorObservation]) -> None:
    seen_tickers: set[str] = set()
    for observation in observations:
        if observation.factor_name != GROWTH_FACTOR_NAME:
            raise ValueError(
                "Growth scoring requires only "
                f"'{GROWTH_FACTOR_NAME}' observations."
            )
        if observation.ticker in seen_tickers:
            raise ValueError(
                "Growth scoring requires at most one observation per ticker."
            )
        seen_tickers.add(observation.ticker)


def _revenue_growth_value(
    snapshot: FundamentalSnapshot | None,
    *,
    as_of: date,
) -> float | None:
    if snapshot is None:
        return None
    if snapshot.as_of != as_of:
        return None
    return snapshot.revenue_growth_yoy


@dataclass(slots=True)
class GrowthPillarEngine(PillarEngine):
    fundamentals: Mapping[str, FundamentalSnapshot | None]
    peer_groups: Mapping[str, str | None]
    source: str = GROWTH_FACTOR_SOURCE
    pillar_name: str = "G"

    def score_cards(self, tickers: list[str], as_of: date) -> list[PillarScoreCard]:
        observations = build_growth_observations(
            self.fundamentals,
            self.peer_groups,
            tickers=tickers,
            as_of=as_of,
            source=self.source,
        )
        return score_growth(observations)

    def score(self, tickers: list[str], as_of: date) -> dict[str, float]:
        return {
            card.ticker: card.score
            for card in self.score_cards(tickers=tickers, as_of=as_of)
        }
