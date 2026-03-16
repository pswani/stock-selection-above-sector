from stock_selection.penalties.base import PenaltyContext, apply_penalties
from stock_selection.penalties.rules import MinimumQualityPenalty


def test_minimum_quality_penalty_fires() -> None:
    context = PenaltyContext(profile_name="balanced", available_rules={"minimum_quality": 6})
    traces = apply_penalties(
        ticker="ABC",
        pillar_scores={"Q": 32},
        context=context,
        rules=[MinimumQualityPenalty(threshold=40)],
    )
    assert len(traces) == 1
    assert traces[0].penalty_points == 6
