from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date

from stock_selection.factors import normalize_factor_output
from stock_selection.models import (
    EstimateSnapshot,
    FactorObservation,
    MetricDirection,
    PillarScoreCard,
)
from stock_selection.scoring.composite import PillarEngine

SENTIMENT_FACTOR_NAME = "eps_revision_90d"
SENTIMENT_FACTOR_SOURCE = "estimates.eps_revision_90d"


def build_sentiment_observations(
    estimates: Mapping[str, EstimateSnapshot | None],
    peer_groups: Mapping[str, str | None],
    *,
    tickers: Collection[str] | None = None,
    as_of: date,
    source: str = SENTIMENT_FACTOR_SOURCE,
) -> list[FactorObservation]:
    ordered_tickers = (
        sorted(set(tickers))
        if tickers is not None
        else sorted(set(estimates) | set(peer_groups))
    )
    return [
        FactorObservation(
            ticker=ticker,
            factor_name=SENTIMENT_FACTOR_NAME,
            value=_eps_revision_value(estimates.get(ticker), as_of=as_of),
            direction=MetricDirection.HIGHER_IS_BETTER,
            peer_group=peer_groups.get(ticker),
            as_of=as_of,
            source=source,
        )
        for ticker in ordered_tickers
    ]


def score_sentiment(observations: list[FactorObservation]) -> list[PillarScoreCard]:
    _validate_sentiment_observations(observations)

    normalized = normalize_factor_output(observations)
    return [
        PillarScoreCard(
            ticker=observation.ticker,
            pillar="S",
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


def _validate_sentiment_observations(observations: list[FactorObservation]) -> None:
    seen_tickers: set[str] = set()
    for observation in observations:
        if observation.factor_name != SENTIMENT_FACTOR_NAME:
            raise ValueError(
                "Sentiment scoring requires only "
                f"'{SENTIMENT_FACTOR_NAME}' observations."
            )
        if observation.ticker in seen_tickers:
            raise ValueError("Sentiment scoring requires at most one observation per ticker.")
        seen_tickers.add(observation.ticker)


def _eps_revision_value(
    snapshot: EstimateSnapshot | None,
    *,
    as_of: date,
) -> float | None:
    if snapshot is None or snapshot.as_of != as_of:
        return None
    return snapshot.eps_revision_90d


@dataclass(slots=True)
class SentimentPillarEngine(PillarEngine):
    estimates: Mapping[str, EstimateSnapshot | None]
    peer_groups: Mapping[str, str | None]
    source: str = SENTIMENT_FACTOR_SOURCE
    pillar_name: str = "S"

    def score_cards(self, tickers: list[str], as_of: date) -> list[PillarScoreCard]:
        observations = build_sentiment_observations(
            self.estimates,
            self.peer_groups,
            tickers=tickers,
            as_of=as_of,
            source=self.source,
        )
        return score_sentiment(observations)
