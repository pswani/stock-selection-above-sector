from __future__ import annotations

from stock_selection.config import WeightProfile, load_weight_profile


AVAILABLE_PROFILES = ("balanced", "conservative", "aggressive")


def get_profile(name: str) -> WeightProfile:
    if name not in AVAILABLE_PROFILES:
        raise ValueError(f"Unknown profile: {name}")
    return load_weight_profile(name)
