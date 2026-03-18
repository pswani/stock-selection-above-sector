from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Currency(StrEnum):
    USD = "USD"
    INR = "INR"


class SecurityType(StrEnum):
    COMMON_STOCK = "common_stock"
    ADR = "adr"
    ETF = "etf"


class MetricDirection(StrEnum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


class Classification(BaseModel):
    sector: str | None = None
    industry_group: str | None = None
    industry: str | None = None
    sub_industry: str | None = None
    country: str | None = None
    exchange: str | None = None
    benchmark: str | None = None


class PeerGroup(BaseModel):
    name: str
    level: str = Field(description="sector, industry_group, industry, or custom")
    members: list[str] = Field(default_factory=list)


class Security(BaseModel):
    ticker: str = Field(min_length=1)
    company_name: str | None = None
    security_type: SecurityType = SecurityType.COMMON_STOCK
    currency: Currency = Currency.USD
    classification: Classification | None = None
    is_active: bool = True


class PriceBar(BaseModel):
    ticker: str
    as_of: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float
    adjusted_close: float | None = None
    volume: float | None = None


class FundamentalSnapshot(BaseModel):
    ticker: str
    as_of: date
    revenue_growth_yoy: float | None = None
    eps_growth_yoy: float | None = None
    operating_margin: float | None = None
    gross_margin: float | None = None
    return_on_equity: float | None = None
    free_cash_flow_margin: float | None = None
    debt_to_equity: float | None = None
    net_debt_to_ebitda: float | None = None
    diluted_share_count_growth_3y: float | None = None


class EstimateSnapshot(BaseModel):
    ticker: str
    as_of: date
    forward_pe: float | None = None
    peg_ratio: float | None = None
    price_to_sales: float | None = None
    ev_to_ebitda: float | None = None
    next_year_revenue_growth: float | None = None
    next_year_eps_growth: float | None = None
    eps_revision_90d: float | None = None
    revenue_revision_90d: float | None = None


class CorporateActionSnapshot(BaseModel):
    ticker: str
    as_of: date
    action_type: str
    value: float | None = None
    currency: Currency = Currency.USD


class OwnershipSnapshot(BaseModel):
    ticker: str
    as_of: date
    institutional_ownership: float | None = None
    insider_ownership: float | None = None
    short_interest_percent_float: float | None = None


class FactorObservation(BaseModel):
    ticker: str
    factor_name: str
    value: float | None
    direction: MetricDirection
    peer_group: str | None = None
    as_of: date | None = None
    source: str | None = None


class NormalizedFactorObservation(BaseModel):
    ticker: str
    factor_name: str
    direction: MetricDirection
    peer_group: str | None = None
    as_of: date | None = None
    source: str | None = None
    raw_value: float | None = None
    oriented_value: float | None = None
    winsorized_value: float | None = None
    percentile_rank: float | None = Field(default=None, ge=0, le=100)
    robust_zscore: float | None = None
    peer_group_size: int = Field(ge=0)
    peer_group_valid_size: int = Field(ge=0)
    coverage_ratio: float | None = Field(default=None, ge=0, le=1)
    normalization_status: str

    @field_validator("peer_group_valid_size")
    @classmethod
    def valid_size_not_above_group_size(cls, value: int, info):
        group_size = info.data.get("peer_group_size")
        if group_size is not None and value > group_size:
            raise ValueError("peer_group_valid_size cannot exceed peer_group_size")
        return value


class PillarScoreCard(BaseModel):
    ticker: str
    pillar: str
    score: float = Field(ge=0, le=100)
    coverage_ratio: float | None = Field(default=None, ge=0, le=1)
    diagnostics: dict[str, float | str | None] = Field(default_factory=dict)
    as_of: date | None = None


class PenaltyTrace(BaseModel):
    rule_name: str
    penalty_points: float = Field(ge=0)
    reason: str
    evidence: dict[str, float | str | None] = Field(default_factory=dict)


class RankingResult(BaseModel):
    ticker: str
    as_of: date
    profile_name: str
    weighted_score: float = Field(ge=0, le=100)
    total_penalty: float = Field(ge=0)
    final_score: float = Field(ge=0, le=100)
    pillar_scores: dict[str, float] = Field(default_factory=dict)
    penalty_traces: list[PenaltyTrace] = Field(default_factory=list)

    @field_validator("final_score")
    @classmethod
    def final_score_not_above_weighted(cls, value: float, info):
        weighted = info.data.get("weighted_score")
        if weighted is not None and value > weighted:
            raise ValueError("final_score cannot exceed weighted_score")
        return value
