from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from stock_selection.backtest.validation import BenchmarkType


class BenchmarkFixtureFamily(StrEnum):
    SECTOR_PEER_AVERAGE = "sector_peer_average"
    SECTOR_ETF = "sector_etf"
    MARKET_INDEX = "market_index"


class BenchmarkFixture(BaseModel):
    family: BenchmarkFixtureFamily
    benchmark_type: BenchmarkType
    benchmark_name: str
    methodology: str
    description: str
    returns_by_as_of: dict[date, float] = Field(default_factory=dict)

    @field_validator("benchmark_name", "methodology", "description")
    @classmethod
    def value_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("benchmark fixture metadata must not be blank")
        return normalized


def list_benchmark_fixtures() -> list[BenchmarkFixture]:
    return [
        BenchmarkFixture(
            family=BenchmarkFixtureFamily.MARKET_INDEX,
            benchmark_type=BenchmarkType.MARKET_INDEX,
            benchmark_name="sample_market_index",
            methodology="fixture_market_index_total_return",
            description=(
                "Deterministic market-index-style benchmark fixture for sample validation "
                "and reporting flows."
            ),
            returns_by_as_of={
                date(2026, 1, 31): 0.015,
                date(2026, 2, 28): 0.008,
            },
        ),
        BenchmarkFixture(
            family=BenchmarkFixtureFamily.SECTOR_ETF,
            benchmark_type=BenchmarkType.SECTOR_ETF,
            benchmark_name="sample_sector_etf",
            methodology="fixture_sector_etf_total_return",
            description=(
                "Deterministic sector-ETF-style benchmark fixture for sample validation "
                "and reporting flows."
            ),
            returns_by_as_of={
                date(2026, 1, 31): 0.012,
                date(2026, 2, 28): 0.009,
            },
        ),
        BenchmarkFixture(
            family=BenchmarkFixtureFamily.SECTOR_PEER_AVERAGE,
            benchmark_type=BenchmarkType.SECTOR_PEER_AVERAGE,
            benchmark_name="sample_sector_peer_average",
            methodology="fixture_sector_peer_average_total_return",
            description=(
                "Deterministic sector-peer-average benchmark fixture for sample validation "
                "and reporting flows."
            ),
            returns_by_as_of={
                date(2026, 1, 31): 0.011,
                date(2026, 2, 28): 0.007,
            },
        ),
    ]


def get_benchmark_fixture(family: BenchmarkFixtureFamily) -> BenchmarkFixture:
    for fixture in list_benchmark_fixtures():
        if fixture.family is family:
            return fixture
    raise ValueError(f"Unknown benchmark fixture family: {family}")
