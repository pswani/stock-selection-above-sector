from datetime import date
from pathlib import Path

from stock_selection.models import RankingResult
from stock_selection.reporting import ranking_results_to_frame, write_ranking_csv


def test_ranking_results_to_frame() -> None:
    result = RankingResult(
        ticker="NVDA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=5,
        final_score=75,
        pillar_scores={"RP": 90, "G": 80},
    )
    frame = ranking_results_to_frame([result])
    assert frame.loc[0, "ticker"] == "NVDA"
    assert frame.loc[0, "penalty_count"] == 0


def test_write_ranking_csv(tmp_path: Path) -> None:
    result = RankingResult(
        ticker="NVDA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=5,
        final_score=75,
        pillar_scores={"RP": 90},
    )
    path = write_ranking_csv([result], tmp_path / "ranking.csv")
    assert path.exists()
