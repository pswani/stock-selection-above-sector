from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PathSettings(BaseModel):
    reports_dir: str
    snapshots_dir: str
    sample_data_dir: str


class RankingSettings(BaseModel):
    default_profile: str
    min_required_pillars: int = Field(ge=1, le=6)
    max_penalty_points: int = Field(ge=0)


class AppSettings(BaseModel):
    name: str
    environment: str
    default_currency: str


class PenaltyProfile(BaseModel):
    max_total_penalty: float = Field(ge=0)
    rules: dict[str, float] = Field(default_factory=dict)


class WeightProfile(BaseModel):
    name: str
    pillar_weights: dict[str, float]
    penalties: PenaltyProfile


class SettingsModel(BaseModel):
    app: AppSettings
    ranking: RankingSettings
    paths: PathSettings


class EnvSettings(BaseSettings):
    stock_selection_settings: str = "config/settings.yaml"
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_settings(path: str | Path = "config/settings.yaml") -> SettingsModel:
    payload = load_yaml(path)
    return SettingsModel.model_validate(payload)


def load_weight_profile(name: str, root: str | Path = "config/weights") -> WeightProfile:
    payload = load_yaml(Path(root) / f"{name}.yaml")
    return WeightProfile.model_validate(payload)
