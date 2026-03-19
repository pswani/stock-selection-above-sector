"""Deterministic explainability models.

These types currently support summary cards derived from ranking outputs. The
layer is still intentionally lightweight, but it now provides a concrete,
testable explainability surface instead of a placeholder schema only.
"""

from __future__ import annotations

from pydantic import BaseModel


class ExplanationCard(BaseModel):
    ticker: str
    summary: str
    strengths: list[str]
    risks: list[str]
