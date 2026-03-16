from pathlib import Path


def test_bootstrap_script_exists_and_uses_frozen_sync() -> None:
    script = Path("scripts/bootstrap.sh")
    assert script.exists()
    contents = script.read_text()
    assert "command -v uv" in contents
    assert "uv sync --dev --frozen" in contents
    assert "uv python install" in contents
    assert '"pydantic_settings"' in contents
    assert '"scipy"' in contents
    assert '"sklearn"' in contents
    assert "uv run pytest --version" in contents
    assert "uv run ruff --version" in contents
    assert "uv run pyright --version" in contents


def test_validate_env_script_runs_quality_gate_commands() -> None:
    script = Path("scripts/validate-env.sh")
    assert script.exists()
    contents = script.read_text()
    assert "command -v uv" in contents
    assert "uv sync --dev --frozen" in contents
    assert '"pydantic_settings"' in contents
    assert '"scipy"' in contents
    assert '"sklearn"' in contents
    assert "uv run pytest --version" in contents
    assert "uv run ruff --version" in contents
    assert "uv run pyright --version" in contents
    assert "uv run pytest -q" in contents
    assert "uv run ruff check ." in contents
    assert "uv run pyright" in contents
