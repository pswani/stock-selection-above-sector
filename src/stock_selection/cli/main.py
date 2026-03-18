from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from rich import print

from stock_selection.config import load_settings, load_weight_profile
from stock_selection.penalties.rules import MinimumQualityPenalty
from stock_selection.reporting import (
    write_pillar_score_cards_csv,
    write_ranking_csv,
    write_relative_performance_preview_csv,
)
from stock_selection.scoring.composite import build_ranking_result
from stock_selection.scoring.relative_performance import RelativePerformancePillarEngine

app = typer.Typer(add_completion=False)

SAMPLE_RP_RETURNS_6M = {
    "AAA": 0.30,
    "BBB": 0.10,
    "CCC": 0.20,
}
SAMPLE_RP_PEER_GROUPS = {
    "AAA": "sector:tech",
    "BBB": "sector:tech",
    "CCC": "sector:tech",
}


@app.command()
def status() -> None:
    settings = load_settings()
    profile = settings.ranking.default_profile
    print(
        "[bold green]stock-selection[/bold green] "
        f":: env={settings.app.environment} "
        f":: profile={profile}"
    )


@app.command()
def export_sample_ranking(
    output: str = typer.Option("outputs/reports/sample-ranking.csv", help="Destination CSV path"),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
    profile: str = typer.Option("balanced", help="Weight profile name"),
) -> None:
    profile_obj = load_weight_profile(profile)
    as_of_date = date.fromisoformat(as_of)
    results = [
        build_ranking_result(
            ticker="NVDA",
            as_of=as_of_date,
            profile=profile_obj,
            pillar_scores={"RP": 92, "G": 95, "Q": 85, "V": 55, "R": 65, "S": 88},
            penalty_rules=[MinimumQualityPenalty()],
        ),
        build_ranking_result(
            ticker="COST",
            as_of=as_of_date,
            profile=profile_obj,
            pillar_scores={"RP": 68, "G": 58, "Q": 72, "V": 41, "R": 81, "S": 52},
            penalty_rules=[MinimumQualityPenalty()],
        ),
    ]
    path = write_ranking_csv(results, Path(output))
    print(f"[bold blue]wrote[/bold blue] {path}")


@app.command()
def export_sample_relative_performance(
    output: str = typer.Option("outputs/reports/sample-rp.csv", help="Destination CSV path"),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
) -> None:
    as_of_date = date.fromisoformat(as_of)
    engine = RelativePerformancePillarEngine(
        returns_6m=SAMPLE_RP_RETURNS_6M,
        peer_groups=SAMPLE_RP_PEER_GROUPS,
    )
    cards = engine.score_cards(sorted(SAMPLE_RP_RETURNS_6M), as_of=as_of_date)
    path = write_pillar_score_cards_csv(cards, Path(output))
    print(f"[bold blue]wrote[/bold blue] {path}")


@app.command()
def export_sample_relative_performance_preview(
    output: str = typer.Option(
        "outputs/reports/sample-rp-preview.csv",
        help="Destination CSV path",
    ),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
) -> None:
    settings = load_settings()
    as_of_date = date.fromisoformat(as_of)
    engine = RelativePerformancePillarEngine(
        returns_6m=SAMPLE_RP_RETURNS_6M,
        peer_groups=SAMPLE_RP_PEER_GROUPS,
    )
    preview_ranks = engine.preview_rankings(
        sorted(SAMPLE_RP_RETURNS_6M),
        as_of=as_of_date,
        min_required_pillars=settings.ranking.min_required_pillars,
    )
    path = write_relative_performance_preview_csv(preview_ranks, Path(output))
    print(f"[bold blue]wrote[/bold blue] {path}")


if __name__ == "__main__":
    app()
