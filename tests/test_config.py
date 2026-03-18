from pathlib import Path

import pytest
from pydantic import ValidationError

from stock_selection.config import load_env_settings, load_settings, load_weight_profile


def test_load_settings() -> None:
    settings = load_settings()
    assert settings.app.name == "stock-selection"
    assert settings.paths.sample_data_dir == "data/sample"


def test_load_profile() -> None:
    profile = load_weight_profile("balanced")
    assert profile.name == "balanced"
    assert profile.pillar_weights["G"] == 25
    assert profile.penalties.max_total_penalty == 25


def test_load_env_settings_defaults() -> None:
    env = load_env_settings()
    assert env.stock_selection_fmp_base_url.endswith("/api/v3")


def test_load_yaml_rejects_non_mapping_root(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")

    from stock_selection.config import load_yaml

    with pytest.raises(ValueError, match="top-level mapping .*got list"):
        load_yaml(path)


def test_load_weight_profile_requires_all_required_pillars(tmp_path: Path) -> None:
    profile_path = tmp_path / "invalid.yaml"
    profile_path.write_text(
        "\n".join(
            [
                "name: invalid",
                "pillar_weights:",
                "  RP: 20",
                "  G: 20",
                "  Q: 20",
                "  V: 20",
                "  R: 20",
                "penalties:",
                "  max_total_penalty: 10",
                "  rules: {}",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="must define exactly the required pillars"):
        load_weight_profile("invalid", root=tmp_path)


def test_load_weight_profile_rejects_non_positive_total_weight(tmp_path: Path) -> None:
    profile_path = tmp_path / "zero.yaml"
    profile_path.write_text(
        "\n".join(
            [
                "name: zero",
                "pillar_weights:",
                "  RP: 0",
                "  G: 0",
                "  Q: 0",
                "  V: 0",
                "  R: 0",
                "  S: 0",
                "penalties:",
                "  max_total_penalty: 10",
                "  rules: {}",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="total weight must be positive"):
        load_weight_profile("zero", root=tmp_path)


def test_load_yaml_reports_invalid_yaml_with_file_path(tmp_path: Path) -> None:
    path = tmp_path / "broken.yaml"
    path.write_text("app:\n  name: test\n  bad: [\n", encoding="utf-8")

    from stock_selection.config import load_yaml

    with pytest.raises(ValueError, match=f"Invalid YAML in config file: {path}"):
        load_yaml(path)


def test_load_yaml_reports_missing_file_path(tmp_path: Path) -> None:
    path = tmp_path / "missing.yaml"

    from stock_selection.config import load_yaml

    with pytest.raises(FileNotFoundError, match=f"Config file not found: {path}"):
        load_yaml(path)


def test_load_weight_profile_rejects_negative_penalty_rule_weights(tmp_path: Path) -> None:
    profile_path = tmp_path / "invalid.yaml"
    profile_path.write_text(
        "\n".join(
            [
                "name: invalid",
                "pillar_weights:",
                "  RP: 20",
                "  G: 20",
                "  Q: 20",
                "  V: 20",
                "  R: 10",
                "  S: 10",
                "penalties:",
                "  max_total_penalty: 10",
                "  rules:",
                "    minimum_quality: -1",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="penalty rule weights must be non-negative"):
        load_weight_profile("invalid", root=tmp_path)
