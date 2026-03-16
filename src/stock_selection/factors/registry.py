from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from stock_selection.models import MetricDirection


class PillarName(str, Enum):
    RP = "RP"
    G = "G"
    Q = "Q"
    V = "V"
    R = "R"
    S = "S"


class MissingDataPolicy(str, Enum):
    SKIP_FACTOR = "skip_factor"
    DROP_SECURITY = "drop_security"


class FactorDefinition(BaseModel):
    name: str = Field(min_length=3, pattern=r"^[a-z0-9_]+$")
    pillar: PillarName
    direction: MetricDirection
    description: str = Field(min_length=5)
    required_inputs: list[str] = Field(min_length=1)
    missing_data_policy: MissingDataPolicy = MissingDataPolicy.SKIP_FACTOR

    @field_validator("required_inputs")
    @classmethod
    def validate_required_inputs(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value if item.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("required_inputs must not contain duplicates")
        return normalized


@dataclass(slots=True)
class FactorRegistry:
    _definitions: dict[str, FactorDefinition] = field(default_factory=dict)

    def register(self, definition: FactorDefinition) -> None:
        if definition.name in self._definitions:
            raise ValueError(f"factor '{definition.name}' is already registered")
        self._definitions[definition.name] = definition

    def get(self, factor_name: str) -> FactorDefinition:
        if factor_name not in self._definitions:
            raise KeyError(f"Unknown factor: {factor_name}")
        return self._definitions[factor_name]

    def list_all(self) -> list[FactorDefinition]:
        names = sorted(self._definitions)
        return [self._definitions[name] for name in names]


CANONICAL_FACTOR_DEFINITIONS: tuple[FactorDefinition, ...] = (
    FactorDefinition(
        name="relative_strength_6m",
        pillar=PillarName.RP,
        direction=MetricDirection.HIGHER_IS_BETTER,
        description="Six-month peer-relative price performance.",
        required_inputs=["price_returns_6m", "peer_group"],
    ),
    FactorDefinition(
        name="revenue_growth_yoy",
        pillar=PillarName.G,
        direction=MetricDirection.HIGHER_IS_BETTER,
        description="Year-over-year revenue growth.",
        required_inputs=["fundamentals.revenue_growth_yoy"],
    ),
    FactorDefinition(
        name="return_on_equity",
        pillar=PillarName.Q,
        direction=MetricDirection.HIGHER_IS_BETTER,
        description="Return on equity from latest fundamentals snapshot.",
        required_inputs=["fundamentals.return_on_equity"],
    ),
    FactorDefinition(
        name="forward_pe",
        pillar=PillarName.V,
        direction=MetricDirection.LOWER_IS_BETTER,
        description="Forward price-to-earnings ratio.",
        required_inputs=["estimates.forward_pe"],
    ),
    FactorDefinition(
        name="volatility_3m",
        pillar=PillarName.R,
        direction=MetricDirection.LOWER_IS_BETTER,
        description="Three-month realized volatility of daily returns.",
        required_inputs=["price_returns_3m"],
    ),
    FactorDefinition(
        name="eps_revision_90d",
        pillar=PillarName.S,
        direction=MetricDirection.HIGHER_IS_BETTER,
        description="Ninety-day EPS estimate revision trend.",
        required_inputs=["estimates.eps_revision_90d"],
    ),
)


def build_canonical_registry() -> FactorRegistry:
    registry = FactorRegistry()
    for definition in CANONICAL_FACTOR_DEFINITIONS:
        registry.register(definition)
    return registry

