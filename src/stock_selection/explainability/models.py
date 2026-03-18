"""Scaffolded explainability models.

These types support simple human-readable summaries, but they are not yet a
full explainability layer with factor traces, confidence handling, or ranking
diagnostics.
"""

from __future__ import annotations

from pydantic import BaseModel


class ExplanationCard(BaseModel):
    ticker: str
    summary: str
    strengths: list[str]
    risks: list[str]
