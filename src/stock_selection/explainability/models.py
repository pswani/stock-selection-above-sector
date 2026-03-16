from __future__ import annotations

from pydantic import BaseModel


class ExplanationCard(BaseModel):
    ticker: str
    summary: str
    strengths: list[str]
    risks: list[str]
