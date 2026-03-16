from stock_selection.config import load_settings, load_weight_profile


def test_load_settings() -> None:
    settings = load_settings()
    assert settings.app.name == "stock-selection"
    assert settings.paths.sample_data_dir == "data/sample"


def test_load_profile() -> None:
    profile = load_weight_profile("balanced")
    assert profile.name == "balanced"
    assert profile.pillar_weights["G"] == 25
    assert profile.penalties.max_total_penalty == 25
