from datetime import date

from stock_selection.config import load_weight_profile
from stock_selection.penalties.rules import MinimumQualityPenalty
from stock_selection.scoring.composite import build_ranking_result, weighted_sum


def test_weighted_sum() -> None:
    score = weighted_sum(
        {"RP": 80, "G": 70, "Q": 90, "V": 60, "R": 75, "S": 50},
        {"RP": 20, "G": 25, "Q": 20, "V": 15, "R": 15, "S": 5},
    )
    assert round(score, 2) == 74.25


def test_build_ranking_result_applies_penalty() -> None:
    profile = load_weight_profile("balanced")
    result = build_ranking_result(
        ticker="ABC",
        as_of=date(2026, 1, 31),
        profile=profile,
        pillar_scores={"RP": 70, "G": 70, "Q": 35, "V": 60, "R": 70, "S": 60},
        penalty_rules=[MinimumQualityPenalty()],
    )
    assert result.total_penalty == profile.penalties.rules["minimum_quality"] if "minimum_quality" in profile.penalties.rules else 0
    assert result.final_score <= result.weighted_score
