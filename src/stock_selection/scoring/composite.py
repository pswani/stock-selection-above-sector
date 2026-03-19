from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date

from stock_selection.config import WeightProfile
from stock_selection.constants import REQUIRED_PILLARS
from stock_selection.models import PillarScoreCard, RankingResult
from stock_selection.penalties.base import PenaltyContext, PenaltyRule, apply_penalties

ASSEMBLY_STATUS_OK = "ok"
ASSEMBLY_STATUS_INSUFFICIENT_PILLARS = "insufficient_pillars"


@dataclass(slots=True)
class ScoreRequest:
    as_of: date
    profile_name: str
    tickers: list[str]
    notes: str | None = None


@dataclass(slots=True)
class ScoreContext:
    request: ScoreRequest
    profile: WeightProfile
    trace_enabled: bool = True


@dataclass(slots=True)
class Scorecard:
    ticker: str
    pillar_scores: dict[str, float]
    weighted_score: float
    total_penalty: float = 0.0
    final_score: float = 0.0
    traces: list[object] = field(default_factory=list)


@dataclass(slots=True)
class PillarScoreAssembly:
    ticker: str
    as_of: date | None
    pillar_scores: dict[str, float]
    pillar_coverages: dict[str, float | None]
    pillar_diagnostics: dict[str, dict[str, float | str | None]]
    available_pillar_count: int
    min_required_pillars: int
    missing_pillars: list[str]
    meets_minimum_pillars: bool
    assembly_status: str


class PillarEngine:
    pillar_name: str

    def score_cards(self, tickers: list[str], as_of: date) -> list[PillarScoreCard]:
        raise NotImplementedError

    def score(self, tickers: list[str], as_of: date) -> dict[str, float | None]:
        return {
            card.ticker: card.score
            for card in self.score_cards(tickers=tickers, as_of=as_of)
        }


def weighted_sum(scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
    missing = [
        pillar
        for pillar in REQUIRED_PILLARS
        if pillar not in scores or pillar not in weights
    ]
    if missing:
        msg = f"Missing pillars in score calculation: {missing}"
        raise ValueError(msg)
    total_weight = sum(float(weights[p]) for p in REQUIRED_PILLARS)
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")
    return sum(float(scores[p]) * float(weights[p]) for p in REQUIRED_PILLARS) / total_weight


def assemble_pillar_score_cards(
    cards: list[PillarScoreCard],
    *,
    min_required_pillars: int,
    required_pillars: tuple[str, ...] = REQUIRED_PILLARS,
) -> list[PillarScoreAssembly]:
    if len(set(required_pillars)) != len(required_pillars):
        raise ValueError("required_pillars must not contain duplicates")
    if min_required_pillars < 1 or min_required_pillars > len(required_pillars):
        raise ValueError(
            "min_required_pillars must be between 1 and the number of required pillars"
        )

    grouped_cards: dict[str, dict[str, PillarScoreCard]] = {}
    for card in cards:
        if card.pillar not in required_pillars:
            raise ValueError(f"Unknown pillar in score-card assembly: {card.pillar}")
        ticker_cards = grouped_cards.setdefault(card.ticker, {})
        if card.pillar in ticker_cards:
            raise ValueError(
                "Pillar score-card assembly requires at most one score card per "
                f"ticker/pillar pair: {card.ticker}/{card.pillar}"
            )
        ticker_cards[card.pillar] = card

    assemblies: list[PillarScoreAssembly] = []
    for ticker in sorted(grouped_cards):
        ticker_cards = grouped_cards[ticker]
        as_of_values = {card.as_of for card in ticker_cards.values()}
        if len(as_of_values) > 1:
            raise ValueError(
                "Pillar score-card assembly requires a consistent as_of per ticker: "
                f"{ticker}"
            )

        pillar_scores = {
            pillar: card.score
            for pillar in required_pillars
            if (card := ticker_cards.get(pillar)) is not None and card.score is not None
        }
        pillar_coverages = {
            pillar: ticker_cards[pillar].coverage_ratio
            for pillar in required_pillars
            if pillar in ticker_cards
        }
        pillar_diagnostics = {
            pillar: dict(ticker_cards[pillar].diagnostics)
            for pillar in required_pillars
            if pillar in ticker_cards
        }
        missing_pillars = [
            pillar
            for pillar in required_pillars
            if pillar not in ticker_cards or ticker_cards[pillar].score is None
        ]
        available_pillar_count = len(pillar_scores)
        meets_minimum_pillars = available_pillar_count >= min_required_pillars
        assembly_status = (
            ASSEMBLY_STATUS_OK
            if meets_minimum_pillars
            else ASSEMBLY_STATUS_INSUFFICIENT_PILLARS
        )

        assemblies.append(
            PillarScoreAssembly(
                ticker=ticker,
                as_of=next(iter(as_of_values), None),
                pillar_scores=pillar_scores,
                pillar_coverages=pillar_coverages,
                pillar_diagnostics=pillar_diagnostics,
                available_pillar_count=available_pillar_count,
                min_required_pillars=min_required_pillars,
                missing_pillars=missing_pillars,
                meets_minimum_pillars=meets_minimum_pillars,
                assembly_status=assembly_status,
            )
        )

    return assemblies


def build_ranking_result(
    ticker: str,
    as_of: date,
    profile: WeightProfile,
    pillar_scores: dict[str, float],
    penalty_rules: list[PenaltyRule] | None = None,
) -> RankingResult:
    weighted = weighted_sum(pillar_scores, profile.pillar_weights)
    penalty_context = PenaltyContext(
        profile_name=profile.name,
        available_rules=profile.penalties.rules,
    )
    traces = apply_penalties(
        ticker,
        pillar_scores,
        penalty_context,
        penalty_rules or [],
    )
    total_penalty = min(
        sum(trace.penalty_points for trace in traces),
        profile.penalties.max_total_penalty,
    )
    final_score = max(weighted - total_penalty, 0.0)
    return RankingResult(
        ticker=ticker,
        as_of=as_of,
        profile_name=profile.name,
        weighted_score=weighted,
        total_penalty=total_penalty,
        final_score=final_score,
        pillar_scores=dict(pillar_scores),
        penalty_traces=traces,
    )
