from datetime import date

import pytest

from stock_selection.config import load_weight_profile
from stock_selection.models import PillarScoreCard
from stock_selection.penalties.rules import MinimumQualityPenalty
from stock_selection.scoring.composite import (
    assemble_pillar_score_cards,
    build_ranking_result,
    weighted_sum,
)
from stock_selection.scoring.relative_performance import RelativePerformancePillarEngine


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
    expected_penalty = profile.penalties.rules.get("minimum_quality", 0)
    assert result.total_penalty == expected_penalty
    assert result.final_score <= result.weighted_score


def test_assemble_pillar_score_cards_from_relative_performance_cards() -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={
            "AAA": 0.30,
            "BBB": 0.10,
            "CCC": 0.20,
        },
        peer_groups={
            "AAA": "sector:tech",
            "BBB": "sector:tech",
            "CCC": "sector:tech",
        },
    )

    cards = engine.score_cards(["CCC", "AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=1)

    assert [assembly.ticker for assembly in assemblies] == ["AAA", "BBB", "CCC"]
    assert [assembly.assembly_status for assembly in assemblies] == ["ok", "ok", "ok"]
    assert assemblies[0].pillar_scores == {"RP": pytest.approx(100.0)}
    assert assemblies[1].pillar_scores == {"RP": pytest.approx(100.0 / 3.0)}
    assert assemblies[2].pillar_scores == {"RP": pytest.approx(200.0 / 3.0)}
    assert assemblies[0].pillar_coverages == {"RP": pytest.approx(1.0)}
    assert assemblies[0].missing_pillars == ["G", "Q", "V", "R", "S"]
    assert all(assembly.meets_minimum_pillars for assembly in assemblies)


def test_assemble_pillar_score_cards_marks_insufficient_pillars_explicitly() -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )

    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))
    assemblies = assemble_pillar_score_cards(cards, min_required_pillars=2)

    assert [assembly.assembly_status for assembly in assemblies] == [
        "insufficient_pillars",
        "insufficient_pillars",
    ]
    assert [assembly.meets_minimum_pillars for assembly in assemblies] == [False, False]
    assert all(assembly.available_pillar_count == 1 for assembly in assemblies)


def test_assemble_pillar_score_cards_rejects_duplicate_ticker_pillar_pairs() -> None:
    engine = RelativePerformancePillarEngine(
        returns_6m={"AAA": 0.30, "BBB": 0.10},
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech"},
    )
    cards = engine.score_cards(["AAA", "BBB"], as_of=date(2026, 1, 31))

    with pytest.raises(ValueError, match="at most one score card per ticker/pillar pair"):
        assemble_pillar_score_cards(cards + [cards[0]], min_required_pillars=1)


def test_assemble_pillar_score_cards_excludes_missing_scores_from_availability() -> None:
    assemblies = assemble_pillar_score_cards(
        [
            PillarScoreCard(
                ticker="AAA",
                pillar="RP",
                score=None,
                coverage_ratio=0.5,
                diagnostics={"normalization_status": "insufficient_peer_group"},
                as_of=date(2026, 1, 31),
            ),
            PillarScoreCard(
                ticker="AAA",
                pillar="G",
                score=80.0,
                coverage_ratio=1.0,
                diagnostics={"normalization_status": "ok"},
                as_of=date(2026, 1, 31),
            ),
        ],
        min_required_pillars=2,
    )

    assert len(assemblies) == 1
    assembly = assemblies[0]
    assert assembly.available_pillar_count == 1
    assert assembly.pillar_scores == {"G": pytest.approx(80.0)}
    assert assembly.pillar_coverages == {"RP": pytest.approx(0.5), "G": pytest.approx(1.0)}
    assert assembly.missing_pillars == ["RP", "Q", "V", "R", "S"]
    assert assembly.assembly_status == "insufficient_pillars"
