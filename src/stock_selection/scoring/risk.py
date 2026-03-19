from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date

from stock_selection.factors import normalize_factor_output
from stock_selection.models import FactorObservation, MetricDirection, PillarScoreCard
from stock_selection.scoring.composite import PillarEngine

RISK_FACTOR_NAME = "volatility_3m"
RISK_FACTOR_SOURCE = "price_returns_3m.volatility_3m"


def build_risk_observations(
    volatility_3m: Mapping[str, float | None],
    peer_groups: Mapping[str, str | None],
    *,
    tickers: Collection[str] | None = None,
    as_of: date,
    source: str = RISK_FACTOR_SOURCE,
) -> list[FactorObservation]:
    ordered_tickers = (
        sorted(set(tickers))
        if tickers is not None
        else sorted(set(volatility_3m) | set(peer_groups))
    )
    return [
        FactorObservation(
            ticker=ticker,
            factor_name=RISK_FACTOR_NAME,
            value=volatility_3m.get(ticker),
            direction=MetricDirection.LOWER_IS_BETTER,
            peer_group=peer_groups.get(ticker),
            as_of=as_of,
            source=source,
        )
        for ticker in ordered_tickers
    ]


def score_risk(observations: list[FactorObservation]) -> list[PillarScoreCard]:
    _validate_risk_observations(observations)

    normalized = normalize_factor_output(observations)
    return [
        PillarScoreCard(
            ticker=observation.ticker,
            pillar="R",
            score=observation.percentile_rank,
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


def _validate_risk_observations(observations: list[FactorObservation]) -> None:
    seen_tickers: set[str] = set()
    for observation in observations:
        if observation.factor_name != RISK_FACTOR_NAME:
            raise ValueError("Risk scoring requires only 'volatility_3m' observations.")
        if observation.ticker in seen_tickers:
            raise ValueError("Risk scoring requires at most one observation per ticker.")
        seen_tickers.add(observation.ticker)


@dataclass(slots=True)
class RiskPillarEngine(PillarEngine):
    volatility_3m: Mapping[str, float | None]
    peer_groups: Mapping[str, str | None]
    source: str = RISK_FACTOR_SOURCE
    pillar_name: str = "R"

    def score_cards(self, tickers: list[str], as_of: date) -> list[PillarScoreCard]:
        observations = build_risk_observations(
            self.volatility_3m,
            self.peer_groups,
            tickers=tickers,
            as_of=as_of,
            source=self.source,
        )
        return score_risk(observations)
