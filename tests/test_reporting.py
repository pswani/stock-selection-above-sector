from datetime import date
from pathlib import Path

from stock_selection.models import PillarScoreCard, RankingResult
from stock_selection.reporting import (
    pillar_score_cards_to_frame,
    ranking_results_to_frame,
    write_pillar_score_cards_csv,
    write_ranking_csv,
)


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


def test_pillar_score_cards_to_frame() -> None:
    card = PillarScoreCard(
        ticker="AAA",
        pillar="RP",
        score=100,
        coverage_ratio=1.0,
        diagnostics={"normalization_status": "ok", "peer_group": "sector:tech"},
        as_of=date(2026, 1, 31),
    )

    frame = pillar_score_cards_to_frame([card])

    assert frame.loc[0, "ticker"] == "AAA"
    assert frame.loc[0, "diagnostic_normalization_status"] == "ok"
    assert frame.loc[0, "diagnostic_peer_group"] == "sector:tech"


def test_write_pillar_score_cards_csv(tmp_path: Path) -> None:
    card = PillarScoreCard(
        ticker="AAA",
        pillar="RP",
        score=100,
        coverage_ratio=1.0,
        diagnostics={"normalization_status": "ok"},
        as_of=date(2026, 1, 31),
    )

    path = write_pillar_score_cards_csv([card], tmp_path / "rp.csv")

    assert path.exists()
