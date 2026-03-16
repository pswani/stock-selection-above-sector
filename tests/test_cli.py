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
