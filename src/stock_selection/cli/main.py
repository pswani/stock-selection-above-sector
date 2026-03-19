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

DEMO_ONLY_RANKING_NOTICE = (
    "demo-only ranking export: writes hardcoded sample RankingResult rows and does not use "
    "the implemented scoring pipeline"
)
PIPELINE_BACKED_RP_NOTICE = (
    "pipeline-backed RP export: writes output from the implemented relative-performance "
    "normalization and scoring path"
)
PIPELINE_BACKED_RP_PREVIEW_NOTICE = (
    "pipeline-backed RP preview export: writes output from the implemented RP partial-assembly "
    "preview path, not a final multi-pillar ranking"
)

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


@app.command("export-demo-ranking")
def export_demo_ranking(
    output: str = typer.Option("outputs/reports/demo-ranking.csv", help="Destination CSV path"),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
    profile: str = typer.Option("balanced", help="Weight profile name"),
) -> None:
    """Export demo-only sample ranking rows.

    This command is intentionally not pipeline-backed.
    """
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
    print(f"[bold yellow]{DEMO_ONLY_RANKING_NOTICE}[/bold yellow]")
    print(f"[bold blue]wrote[/bold blue] {path}")


@app.command("export-sample-ranking", hidden=True)
def export_sample_ranking_alias(
    output: str = typer.Option("outputs/reports/sample-ranking.csv", help="Destination CSV path"),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
    profile: str = typer.Option("balanced", help="Weight profile name"),
) -> None:
    """Backward-compatible alias for the demo-only ranking export."""
    print(
        "[bold yellow]deprecated command alias:[/bold yellow] "
        "`export-sample-ranking` maps to `export-demo-ranking`."
    )
    export_demo_ranking(output=output, as_of=as_of, profile=profile)


@app.command()
def export_sample_relative_performance(
    output: str = typer.Option("outputs/reports/sample-rp.csv", help="Destination CSV path"),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
) -> None:
    """Export pipeline-backed sample RP pillar score cards."""
    as_of_date = date.fromisoformat(as_of)
    engine = RelativePerformancePillarEngine(
        returns_6m=SAMPLE_RP_RETURNS_6M,
        peer_groups=SAMPLE_RP_PEER_GROUPS,
    )
    cards = engine.score_cards(sorted(SAMPLE_RP_RETURNS_6M), as_of=as_of_date)
    path = write_pillar_score_cards_csv(cards, Path(output))
    print(f"[bold green]{PIPELINE_BACKED_RP_NOTICE}[/bold green]")
    print(f"[bold blue]wrote[/bold blue] {path}")


@app.command()
def export_sample_relative_performance_preview(
    output: str = typer.Option(
        "outputs/reports/sample-rp-preview.csv",
        help="Destination CSV path",
    ),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
) -> None:
    """Export pipeline-backed RP preview rankings from the partial-assembly path."""
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
    print(f"[bold green]{PIPELINE_BACKED_RP_PREVIEW_NOTICE}[/bold green]")
    print(f"[bold blue]wrote[/bold blue] {path}")


if __name__ == "__main__":
    app()
