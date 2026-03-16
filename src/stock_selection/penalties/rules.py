from __future__ import annotations

from stock_selection.models import PenaltyTrace
from stock_selection.penalties.base import PenaltyContext, PenaltyRule


class MinimumQualityPenalty(PenaltyRule):
    name = "minimum_quality"

    def __init__(self, threshold: float = 40.0) -> None:
        self.threshold = threshold

    def evaluate(self, ticker: str, pillar_scores: dict[str, float], context: PenaltyContext) -> PenaltyTrace | None:
        quality = pillar_scores.get("Q")
        if quality is None or quality >= self.threshold:
            return None
        points = context.available_rules.get(self.name, 0.0)
        if points <= 0:
            return None
        return PenaltyTrace(
            rule_name=self.name,
            penalty_points=points,
            reason="Quality score fell below minimum threshold",
            evidence={"threshold": self.threshold, "quality_score": quality, "ticker": ticker},
        )
