from pathlib import Path

from typer.testing import CliRunner

from stock_selection.cli.main import app

runner = CliRunner()


def test_status_command() -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "stock-selection" in result.stdout


def test_export_sample_ranking(tmp_path: Path) -> None:
    out = tmp_path / "sample-ranking.csv"
    result = runner.invoke(app, ["export-sample-ranking", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_export_sample_relative_performance(tmp_path: Path) -> None:
    out = tmp_path / "sample-rp.csv"
    result = runner.invoke(app, ["export-sample-relative-performance", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_export_sample_relative_performance_preview(tmp_path: Path) -> None:
    out = tmp_path / "sample-rp-preview.csv"
    result = runner.invoke(
        app,
        ["export-sample-relative-performance-preview", "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.exists()
