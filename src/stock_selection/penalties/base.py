from __future__ import annotations

from dataclasses import dataclass

from stock_selection.models import PenaltyTrace


@dataclass(slots=True)
class PenaltyContext:
    profile_name: str
    available_rules: dict[str, float]


class PenaltyRule:
    name: str

    def evaluate(
        self,
        ticker: str,
        pillar_scores: dict[str, float],
        context: PenaltyContext,
    ) -> PenaltyTrace | None:
        raise NotImplementedError


def apply_penalties(
    ticker: str,
    pillar_scores: dict[str, float],
    context: PenaltyContext,
    rules: list[PenaltyRule],
) -> list[PenaltyTrace]:
    traces: list[PenaltyTrace] = []
    for rule in rules:
        trace = rule.evaluate(ticker=ticker, pillar_scores=pillar_scores, context=context)
        if trace is not None:
            traces.append(trace)
    return traces
