from datetime import date

import pytest
from pydantic import ValidationError

from stock_selection.models import Classification, PenaltyTrace, RankingResult


def test_ranking_result_accepts_valid_scores() -> None:
    result = RankingResult(
        ticker="NVDA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=5,
        final_score=75,
        pillar_scores={"RP": 90},
        penalty_traces=[PenaltyTrace(rule_name="x", penalty_points=5, reason="demo")],
    )
    assert result.final_score == 75


def test_ranking_result_rejects_final_score_above_weighted() -> None:
    with pytest.raises(ValidationError):
        RankingResult(
            ticker="NVDA",
            as_of=date(2026, 1, 31),
            profile_name="balanced",
            weighted_score=80,
            total_penalty=0,
            final_score=81,
            pillar_scores={},
        )


def test_classification_allows_missing_sector_when_only_exchange_is_known() -> None:
    classification = Classification(exchange="NASDAQ")

    assert classification.sector is None
    assert classification.exchange == "NASDAQ"
