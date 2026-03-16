from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from rich import print

from stock_selection.config import load_settings, load_weight_profile
from stock_selection.penalties.rules import MinimumQualityPenalty
from stock_selection.reporting import write_ranking_csv
from stock_selection.scoring.composite import build_ranking_result

app = typer.Typer(add_completion=False)


@app.command()
def status() -> None:
    settings = load_settings()
    print(
        f"[bold green]stock-selection[/bold green] :: env={settings.app.environment} :: profile={settings.ranking.default_profile}"
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


if __name__ == "__main__":
    app()
