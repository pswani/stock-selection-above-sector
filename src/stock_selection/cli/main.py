from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from rich import print

from stock_selection.backtest import (
    BenchmarkFixtureFamily,
    get_benchmark_fixture,
    list_benchmark_fixtures,
)
from stock_selection.backtest.validation import (
    BenchmarkType,
    ValidationPeriodInput,
    run_validation_backtest,
)
from stock_selection.config import load_settings, load_weight_profile
from stock_selection.explainability import build_explanation_cards
from stock_selection.models import EstimateSnapshot, FundamentalSnapshot
from stock_selection.penalties.rules import MinimumQualityPenalty
from stock_selection.reporting import (
    write_analysis_bundle_manifest_csv,
    write_benchmark_fixtures_csv,
    write_explanation_cards_csv,
    write_pillar_score_cards_csv,
    write_ranking_csv,
    write_relative_performance_preview_csv,
    write_validation_report_bundle_csvs,
)
from stock_selection.scoring.composite import build_ranking_result
from stock_selection.scoring.pipeline import CompositeScoreInputs, build_composite_rankings
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
PIPELINE_BACKED_EXPLANATION_NOTICE = (
    "pipeline-backed explanation export: writes deterministic explanation cards from the "
    "implemented composite ranking and explainability paths"
)
PIPELINE_BACKED_VALIDATION_NOTICE = (
    "pipeline-backed validation export: writes deterministic validation report outputs from "
    "the implemented composite ranking and validation paths"
)
PIPELINE_BACKED_ANALYSIS_BUNDLE_NOTICE = (
    "pipeline-backed analysis bundle export: writes deterministic ranking, explanation, "
    "and validation report outputs from the implemented composite and validation paths"
)
PIPELINE_BACKED_BENCHMARK_FIXTURES_NOTICE = (
    "pipeline-backed benchmark fixture export: writes deterministic benchmark-family fixtures "
    "used by the implemented sample validation and reporting flows"
)
VALIDATION_BENCHMARK_TYPE_OPTION = typer.Option(
    BenchmarkType.SECTOR_PEER_AVERAGE,
    help="Benchmark type for the validation metadata",
)
VALIDATION_BENCHMARK_FAMILY_OPTION = typer.Option(
    BenchmarkFixtureFamily.SECTOR_PEER_AVERAGE,
    help="Benchmark fixture family for the sample validation flow",
)
VALIDATION_BENCHMARK_METHODOLOGY_OPTION = typer.Option(
    None,
    help="Optional benchmark methodology override for the validation metadata",
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


def _sample_composite_inputs(as_of: date) -> CompositeScoreInputs:
    return CompositeScoreInputs(
        peer_groups={"AAA": "sector:tech", "BBB": "sector:tech", "CCC": "sector:tech"},
        returns_6m={"AAA": 0.30, "BBB": 0.10, "CCC": 0.20},
        volatility_3m={"AAA": 0.18, "BBB": 0.34, "CCC": 0.24},
        fundamentals={
            "AAA": FundamentalSnapshot(
                ticker="AAA",
                as_of=as_of,
                revenue_growth_yoy=0.24,
                return_on_equity=0.21,
            ),
            "BBB": FundamentalSnapshot(
                ticker="BBB",
                as_of=as_of,
                revenue_growth_yoy=0.07,
                return_on_equity=0.08,
            ),
            "CCC": FundamentalSnapshot(
                ticker="CCC",
                as_of=as_of,
                revenue_growth_yoy=0.15,
                return_on_equity=0.14,
            ),
        },
        estimates={
            "AAA": EstimateSnapshot(
                ticker="AAA",
                as_of=as_of,
                forward_pe=20.0,
                eps_revision_90d=0.12,
            ),
            "BBB": EstimateSnapshot(
                ticker="BBB",
                as_of=as_of,
                forward_pe=33.0,
                eps_revision_90d=-0.05,
            ),
            "CCC": EstimateSnapshot(
                ticker="CCC",
                as_of=as_of,
                forward_pe=26.0,
                eps_revision_90d=0.03,
            ),
        },
    )


def _sample_rankings_for(as_of: date):
    settings = load_settings()
    profile = load_weight_profile("balanced")
    return build_composite_rankings(
        _sample_composite_inputs(as_of),
        tickers=["AAA", "BBB", "CCC"],
        as_of=as_of,
        profile=profile,
        min_required_pillars=settings.ranking.min_required_pillars,
        penalty_rules=[MinimumQualityPenalty()],
    )


def _sample_validation_report(
    *,
    benchmark_family: BenchmarkFixtureFamily = BenchmarkFixtureFamily.SECTOR_PEER_AVERAGE,
    benchmark_type: BenchmarkType = BenchmarkType.SECTOR_PEER_AVERAGE,
    benchmark_methodology: str | None = None,
):
    fixture = get_benchmark_fixture(benchmark_family)
    if benchmark_type is not fixture.benchmark_type:
        raise ValueError(
            "benchmark_type must match the selected benchmark fixture family "
            f"(family={benchmark_family}, expected_type={fixture.benchmark_type}, "
            f"received_type={benchmark_type})"
        )
    _, january_rankings = _sample_rankings_for(date(2026, 1, 31))
    _, february_rankings = _sample_rankings_for(date(2026, 2, 28))
    return run_validation_backtest(
        [
            ValidationPeriodInput(
                as_of=date(2026, 1, 31),
                ranking_results=january_rankings,
                realized_returns={"AAA": 0.04, "BBB": -0.02, "CCC": 0.01},
                benchmark_return=fixture.returns_by_as_of[date(2026, 1, 31)],
            ),
            ValidationPeriodInput(
                as_of=date(2026, 2, 28),
                ranking_results=february_rankings,
                realized_returns={"AAA": 0.01, "BBB": 0.03, "CCC": -0.01},
                benchmark_return=fixture.returns_by_as_of[date(2026, 2, 28)],
            ),
        ],
        top_k=2,
        transaction_cost_bps=10.0,
        benchmark_name=fixture.benchmark_name,
        benchmark_type=benchmark_type,
        benchmark_fixture_family=benchmark_family,
        benchmark_methodology=benchmark_methodology or fixture.methodology,
    )


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


@app.command()
def export_sample_explanations(
    output: str = typer.Option(
        "outputs/reports/sample-explanations.csv",
        help="Destination CSV path",
    ),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
) -> None:
    """Export pipeline-backed explanation cards from the composite ranking path."""
    as_of_date = date.fromisoformat(as_of)
    assemblies, rankings = _sample_rankings_for(as_of_date)
    cards = build_explanation_cards(rankings, assemblies)
    path = write_explanation_cards_csv(cards, Path(output))
    print(f"[bold green]{PIPELINE_BACKED_EXPLANATION_NOTICE}[/bold green]")
    print(f"[bold blue]wrote[/bold blue] {path}")


@app.command()
def export_sample_validation_report(
    output_prefix: str = typer.Option(
        "outputs/reports/sample-validation",
        help="Destination prefix for summary and periods CSVs",
    ),
    benchmark_family: BenchmarkFixtureFamily = VALIDATION_BENCHMARK_FAMILY_OPTION,
    benchmark_type: BenchmarkType = VALIDATION_BENCHMARK_TYPE_OPTION,
    benchmark_methodology: str | None = VALIDATION_BENCHMARK_METHODOLOGY_OPTION,
) -> None:
    """Export a pipeline-backed sample validation report from the implemented paths."""
    report = _sample_validation_report(
        benchmark_family=benchmark_family,
        benchmark_type=benchmark_type,
        benchmark_methodology=benchmark_methodology,
    )
    summary_path, periods_path = write_validation_report_bundle_csvs(
        report,
        output_prefix=output_prefix,
    )
    print(f"[bold green]{PIPELINE_BACKED_VALIDATION_NOTICE}[/bold green]")
    print(f"[bold blue]wrote[/bold blue] {summary_path}")
    print(f"[bold blue]wrote[/bold blue] {periods_path}")


@app.command()
def export_sample_benchmark_fixtures(
    output: str = typer.Option(
        "outputs/reports/sample-benchmark-fixtures.csv",
        help="Destination CSV path",
    ),
) -> None:
    """Export deterministic benchmark-family fixtures used by sample validation flows."""
    path = write_benchmark_fixtures_csv(list_benchmark_fixtures(), Path(output))
    print(f"[bold green]{PIPELINE_BACKED_BENCHMARK_FIXTURES_NOTICE}[/bold green]")
    print(f"[bold blue]wrote[/bold blue] {path}")


@app.command()
def export_sample_analysis_bundle(
    output_dir: str = typer.Option(
        "outputs/reports/sample-analysis-bundle",
        help="Destination directory for ranking, explanation, and validation outputs",
    ),
    as_of: str = typer.Option("2026-01-31", help="As-of date in YYYY-MM-DD format"),
    benchmark_family: BenchmarkFixtureFamily = VALIDATION_BENCHMARK_FAMILY_OPTION,
    benchmark_type: BenchmarkType = VALIDATION_BENCHMARK_TYPE_OPTION,
    benchmark_methodology: str | None = VALIDATION_BENCHMARK_METHODOLOGY_OPTION,
) -> None:
    """Export a pipeline-backed bundle of ranking, explanation, and validation outputs."""
    as_of_date = date.fromisoformat(as_of)
    output_path = Path(output_dir)
    assemblies, rankings = _sample_rankings_for(as_of_date)
    cards = build_explanation_cards(rankings, assemblies)
    report = _sample_validation_report(
        benchmark_family=benchmark_family,
        benchmark_type=benchmark_type,
        benchmark_methodology=benchmark_methodology,
    )

    ranking_path = write_ranking_csv(rankings, output_path / "sample-ranking.csv")
    explanation_path = write_explanation_cards_csv(
        cards,
        output_path / "sample-explanations.csv",
    )
    summary_path, periods_path = write_validation_report_bundle_csvs(
        report,
        output_prefix=output_path / "sample-validation",
    )
    benchmark_fixtures_path = write_benchmark_fixtures_csv(
        list_benchmark_fixtures(),
        output_path / "sample-benchmark-fixtures.csv",
    )
    manifest_path = write_analysis_bundle_manifest_csv(
        as_of=as_of_date.isoformat(),
        report=report,
        top_rank_ticker=rankings[0].ticker if rankings else None,
        top_rank_score=rankings[0].final_score if rankings else None,
        ranking_path=ranking_path,
        explanation_path=explanation_path,
        validation_summary_path=summary_path,
        validation_periods_path=periods_path,
        benchmark_fixtures_path=benchmark_fixtures_path,
        path=output_path / "sample-analysis-manifest.csv",
    )
    print(f"[bold green]{PIPELINE_BACKED_ANALYSIS_BUNDLE_NOTICE}[/bold green]")
    print(f"[bold blue]wrote[/bold blue] {ranking_path}")
    print(f"[bold blue]wrote[/bold blue] {explanation_path}")
    print(f"[bold blue]wrote[/bold blue] {summary_path}")
    print(f"[bold blue]wrote[/bold blue] {periods_path}")
    print(f"[bold blue]wrote[/bold blue] {benchmark_fixtures_path}")
    print(f"[bold blue]wrote[/bold blue] {manifest_path}")


if __name__ == "__main__":
    app()
