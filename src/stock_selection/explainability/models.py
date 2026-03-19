"""Deterministic explainability models.

These types currently support summary cards derived from ranking outputs. The
layer is still intentionally lightweight, but it now provides a concrete,
testable explainability surface instead of a placeholder schema only.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class ExplanationPillarDetail(BaseModel):
    pillar: str
    score: float


class ExplanationCard(BaseModel):
    ticker: str
    as_of: date
    profile_name: str
    final_score: float
    weighted_score: float
    total_penalty: float
    assembly_status: str
    missing_pillars: list[str]
    top_pillars: list[ExplanationPillarDetail]
    weakest_pillars: list[ExplanationPillarDetail]
    penalty_rules: list[str]
    summary: str
    strengths: list[str]
    risks: list[str]
