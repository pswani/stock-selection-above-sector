from pathlib import Path

from typer.testing import CliRunner

from stock_selection.cli.main import app

runner = CliRunner()


def test_status_command() -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "stock-selection" in result.stdout


def test_export_demo_ranking_is_explicitly_demo_only(tmp_path: Path) -> None:
    out = tmp_path / "demo-ranking.csv"
    result = runner.invoke(app, ["export-demo-ranking", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "demo-only ranking export" in result.stdout
    assert "hardcoded sample RankingResult rows" in result.stdout
    assert "implemented scoring pipeline" in result.stdout


def test_export_sample_ranking_alias_is_deprecated_and_demo_only(tmp_path: Path) -> None:
    out = tmp_path / "sample-ranking.csv"
    result = runner.invoke(app, ["export-sample-ranking", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "deprecated command alias" in result.stdout
    assert "export-demo-ranking" in result.stdout
    assert "demo-only ranking export" in result.stdout


def test_export_sample_relative_performance(tmp_path: Path) -> None:
    out = tmp_path / "sample-rp.csv"
    result = runner.invoke(app, ["export-sample-relative-performance", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "pipeline-backed RP export" in result.stdout


def test_export_sample_relative_performance_preview(tmp_path: Path) -> None:
    out = tmp_path / "sample-rp-preview.csv"
    result = runner.invoke(
        app,
        ["export-sample-relative-performance-preview", "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.exists()
    assert "pipeline-backed RP preview export" in result.stdout
    assert "not a final multi-pillar ranking" in result.stdout
