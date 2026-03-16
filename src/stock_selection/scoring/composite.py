from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date

from stock_selection.config import WeightProfile
from stock_selection.models import RankingResult
from stock_selection.penalties.base import PenaltyContext, PenaltyRule, apply_penalties

REQUIRED_PILLARS = ("RP", "G", "Q", "V", "R", "S")


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


class PillarEngine:
    pillar_name: str

    def score(self, tickers: list[str], as_of: date) -> dict[str, float]:
        raise NotImplementedError


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
