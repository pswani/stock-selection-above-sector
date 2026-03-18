from datetime import date
from pathlib import Path

from stock_selection.models import PillarScoreCard, RankingResult
from stock_selection.reporting import (
    pillar_score_assemblies_to_frame,
    pillar_score_cards_to_frame,
    ranking_results_to_frame,
    write_pillar_score_assemblies_csv,
    write_pillar_score_cards_csv,
    write_ranking_csv,
)
from stock_selection.scoring import (
    RelativePerformancePillarEngine,
    assemble_pillar_score_cards,
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


def test_ranking_results_to_frame_has_deterministic_dynamic_columns() -> None:
    first = RankingResult(
        ticker="AAA",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=80,
        total_penalty=0,
        final_score=80,
        pillar_scores={"S": 50, "RP": 90},
    )
    second = RankingResult(
        ticker="BBB",
        as_of=date(2026, 1, 31),
        profile_name="balanced",
        weighted_score=70,
        total_penalty=0,
        final_score=70,
        pillar_scores={"G": 60},
    )

    frame = ranking_results_to_frame([first, second])

    assert frame.columns.tolist() == [
        "ticker",
        "as_of",
        "profile_name",
        "weighted_score",
        "total_penalty",
        "final_score",
        "penalty_count",
        "pillar_G",
        "pillar_RP",
        "pillar_S",
    ]


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


def test_pillar_score_cards_to_frame_has_schema_for_empty_input() -> None:
    frame = pillar_score_cards_to_frame([])

    assert frame.columns.tolist() == [
        "ticker",
        "pillar",
        "score",
        "coverage_ratio",
        "as_of",
    ]


def test_pillar_score_assemblies_to_frame_integrates_relative_performance_path() -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=2)

    frame = pillar_score_assemblies_to_frame(assemblies)

    assert frame.columns.tolist() == [
        "ticker",
        "as_of",
        "available_pillar_count",
        "min_required_pillars",
        "meets_minimum_pillars",
        "assembly_status",
        "missing_pillars",
        "pillar_score_RP",
        "pillar_coverage_RP",
    ]
    assert frame["assembly_status"].tolist() == [
        "insufficient_pillars",
        "insufficient_pillars",
    ]
    assert frame.loc[0, "missing_pillars"] == "G,Q,V,R,S"


def test_write_pillar_score_assemblies_csv(tmp_path: Path) -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=1)

    path = write_pillar_score_assemblies_csv(assemblies, tmp_path / "assembly.csv")

    assert path.exists()
