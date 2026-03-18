from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date

from stock_selection.factors import normalize_factor_output
from stock_selection.models import FactorObservation, MetricDirection, PillarScoreCard
from stock_selection.scoring.composite import (
    PillarEngine,
    PillarScoreAssembly,
    assemble_pillar_score_cards,
)

RP_FACTOR_NAME = "relative_strength_6m"
RP_FACTOR_SOURCE = "price_returns_6m"
RP_PREVIEW_STATUS_RANKED = "preview_ranked"
RP_PREVIEW_STATUS_MISSING_SCORE = "missing_rp_score"


@dataclass(slots=True)
class RelativePerformancePreviewRank:
    ticker: str
    as_of: date | None
    preview_rank: int | None
    score: float | None
    assembly_status: str
    meets_minimum_pillars: bool
    missing_pillars: list[str]
    ranking_status: str


def build_relative_performance_observations(
    returns_6m: Mapping[str, float | None],
    peer_groups: Mapping[str, str | None],
    *,
    tickers: Collection[str] | None = None,
    as_of: date,
    source: str = RP_FACTOR_SOURCE,
) -> list[FactorObservation]:
    ordered_tickers = (
        sorted(set(tickers))
        if tickers is not None
        else sorted(set(returns_6m) | set(peer_groups))
    )
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
        for ticker in ordered_tickers
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


def rank_relative_performance_assemblies(
    assemblies: list[PillarScoreAssembly],
) -> list[RelativePerformancePreviewRank]:
    ranked_candidates = [
        assembly for assembly in assemblies if assembly.pillar_scores.get("RP") is not None
    ]
    ranked_candidates.sort(
        key=lambda assembly: (
            -float(assembly.pillar_scores["RP"]),
            str(assembly.ticker),
        )
    )
    preview_ranks = {
        assembly.ticker: rank
        for rank, assembly in enumerate(ranked_candidates, start=1)
    }

    preview_rows: list[RelativePerformancePreviewRank] = []
    for assembly in sorted(assemblies, key=lambda item: str(item.ticker)):
        score = assembly.pillar_scores.get("RP")
        ranking_status = (
            RP_PREVIEW_STATUS_RANKED
            if score is not None
            else RP_PREVIEW_STATUS_MISSING_SCORE
        )
        preview_rows.append(
            RelativePerformancePreviewRank(
                ticker=assembly.ticker,
                as_of=assembly.as_of,
                preview_rank=preview_ranks.get(assembly.ticker),
                score=score,
                assembly_status=assembly.assembly_status,
                meets_minimum_pillars=assembly.meets_minimum_pillars,
                missing_pillars=list(assembly.missing_pillars),
                ranking_status=ranking_status,
            )
        )
    return preview_rows


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


@dataclass(slots=True)
class RelativePerformancePillarEngine(PillarEngine):
    returns_6m: Mapping[str, float | None]
    peer_groups: Mapping[str, str | None]
    source: str = RP_FACTOR_SOURCE
    pillar_name: str = "RP"

    def score_cards(self, tickers: list[str], as_of: date) -> list[PillarScoreCard]:
        observations = build_relative_performance_observations(
            self.returns_6m,
            self.peer_groups,
            tickers=tickers,
            as_of=as_of,
            source=self.source,
        )
        return score_relative_performance(observations)

    def preview_rankings(
        self,
        tickers: list[str],
        *,
        as_of: date,
        min_required_pillars: int,
    ) -> list[RelativePerformancePreviewRank]:
        cards = self.score_cards(tickers=tickers, as_of=as_of)
        assemblies = assemble_pillar_score_cards(
            cards,
            min_required_pillars=min_required_pillars,
        )
        return rank_relative_performance_assemblies(assemblies)
