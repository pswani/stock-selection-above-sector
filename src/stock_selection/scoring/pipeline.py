from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date

from stock_selection.config import WeightProfile
from stock_selection.models import (
    EstimateSnapshot,
    FundamentalSnapshot,
    PillarScoreCard,
    RankingResult,
)
from stock_selection.penalties.base import PenaltyRule
from stock_selection.scoring.composite import (
    PillarScoreAssembly,
    assemble_pillar_score_cards,
    build_ranking_result,
)
from stock_selection.scoring.growth import GrowthPillarEngine
from stock_selection.scoring.quality import QualityPillarEngine
from stock_selection.scoring.relative_performance import RelativePerformancePillarEngine
from stock_selection.scoring.risk import RiskPillarEngine
from stock_selection.scoring.sentiment import SentimentPillarEngine
from stock_selection.scoring.valuation import ValuationPillarEngine


@dataclass(slots=True)
class CompositeScoreInputs:
    peer_groups: Mapping[str, str | None]
    returns_6m: Mapping[str, float | None]
    volatility_3m: Mapping[str, float | None]
    fundamentals: Mapping[str, FundamentalSnapshot | None]
    estimates: Mapping[str, EstimateSnapshot | None]


def score_full_pillar_set(
    inputs: CompositeScoreInputs,
    *,
    tickers: Collection[str],
    as_of: date,
) -> list[PillarScoreCard]:
    ordered_tickers = sorted(set(tickers))
    engines = [
        RelativePerformancePillarEngine(
            returns_6m=inputs.returns_6m,
            peer_groups=inputs.peer_groups,
        ),
        GrowthPillarEngine(
            fundamentals=inputs.fundamentals,
            peer_groups=inputs.peer_groups,
        ),
        QualityPillarEngine(
            fundamentals=inputs.fundamentals,
            peer_groups=inputs.peer_groups,
        ),
        ValuationPillarEngine(
            estimates=inputs.estimates,
            peer_groups=inputs.peer_groups,
        ),
        RiskPillarEngine(
            volatility_3m=inputs.volatility_3m,
            peer_groups=inputs.peer_groups,
        ),
        SentimentPillarEngine(
            estimates=inputs.estimates,
            peer_groups=inputs.peer_groups,
        ),
    ]

    cards: list[PillarScoreCard] = []
    for engine in engines:
        cards.extend(engine.score_cards(ordered_tickers, as_of=as_of))
    return cards


def build_composite_rankings(
    inputs: CompositeScoreInputs,
    *,
    tickers: Collection[str],
    as_of: date,
    profile: WeightProfile,
    min_required_pillars: int,
    penalty_rules: list[PenaltyRule] | None = None,
) -> tuple[list[PillarScoreAssembly], list[RankingResult]]:
    cards = score_full_pillar_set(inputs, tickers=tickers, as_of=as_of)
    assemblies = assemble_pillar_score_cards(
        cards,
        min_required_pillars=min_required_pillars,
    )

    rankings = [
        build_ranking_result(
            ticker=assembly.ticker,
            as_of=assembly.as_of or as_of,
            profile=profile,
            pillar_scores=dict(assembly.pillar_scores),
            penalty_rules=penalty_rules,
        )
        for assembly in assemblies
        if assembly.meets_minimum_pillars
    ]
    rankings.sort(
        key=lambda result: (
            -result.final_score,
            -result.weighted_score,
            str(result.ticker),
        )
    )
    return assemblies, rankings
