from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from stock_selection.constants import REQUIRED_PILLARS


class PathSettings(BaseModel):
    reports_dir: str
    snapshots_dir: str
    sample_data_dir: str


class RankingSettings(BaseModel):
    default_profile: str
    min_required_pillars: int = Field(ge=1, le=6)
    max_penalty_points: int = Field(ge=0)

    @field_validator("default_profile")
    @classmethod
    def default_profile_not_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("default_profile must not be blank")
        return normalized


class AppSettings(BaseModel):
    name: str
    environment: str
    default_currency: str


class PenaltyProfile(BaseModel):
    max_total_penalty: float = Field(ge=0)
    rules: dict[str, float] = Field(default_factory=dict)

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, value: dict[str, float]) -> dict[str, float]:
        normalized: dict[str, float] = {}
        invalid_names: list[str] = []

        for rule_name, weight in value.items():
            normalized_name = rule_name.strip()
            if not normalized_name:
                invalid_names.append(rule_name)
                continue
            normalized[normalized_name] = float(weight)

        if invalid_names:
            raise ValueError("penalty rule names must not be blank")

        negative = sorted(name for name, weight in normalized.items() if weight < 0)
        if negative:
            raise ValueError(
                "penalty rule weights must be non-negative "
                f"(negative={negative})"
            )
        return normalized


class WeightProfile(BaseModel):
    name: str
    pillar_weights: dict[str, float]
    penalties: PenaltyProfile

    @field_validator("name")
    @classmethod
    def profile_name_not_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be blank")
        return normalized

    @field_validator("pillar_weights")
    @classmethod
    def validate_pillar_weights(
        cls, value: dict[str, float]
    ) -> dict[str, float]:
        expected = set(REQUIRED_PILLARS)
        provided = set(value)
        missing = sorted(expected.difference(provided))
        extra = sorted(provided.difference(expected))
        if missing or extra:
            details: list[str] = []
            if missing:
                details.append(f"missing={missing}")
            if extra:
                details.append(f"extra={extra}")
            detail_text = ", ".join(details)
            raise ValueError(
                "pillar_weights must define exactly the required pillars "
                f"{list(REQUIRED_PILLARS)} ({detail_text})"
            )

        normalized = {pillar: float(weight) for pillar, weight in value.items()}
        negative = sorted(
            pillar for pillar, weight in normalized.items() if weight < 0
        )
        if negative:
            raise ValueError(
                "pillar_weights must be non-negative for all pillars "
                f"(negative={negative})"
            )
        return normalized

    @model_validator(mode="after")
    def validate_total_weight(self) -> WeightProfile:
        total_weight = sum(self.pillar_weights.values())
        if total_weight <= 0:
            raise ValueError("pillar_weights total weight must be positive")
        return self


class SettingsModel(BaseModel):
    app: AppSettings
    ranking: RankingSettings
    paths: PathSettings


class EnvSettings(BaseSettings):
    stock_selection_settings: str = "config/settings.yaml"
    app_env: str = "development"
    stock_selection_fmp_api_key: str = ""
    stock_selection_fmp_base_url: str = "https://financialmodelingprep.com/api/v3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in config file: {config_path}") from exc

    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(
            "Config file must contain a top-level mapping "
            f"(got {type(payload).__name__}): {config_path}"
        )
    return payload


def load_settings(path: str | Path = "config/settings.yaml") -> SettingsModel:
    payload = load_yaml(path)
    return SettingsModel.model_validate(payload)


def load_weight_profile(name: str, root: str | Path = "config/weights") -> WeightProfile:
    payload = load_yaml(Path(root) / f"{name}.yaml")
    return WeightProfile.model_validate(payload)


def load_env_settings() -> EnvSettings:
    return EnvSettings()
