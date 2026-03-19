from __future__ import annotations

from stock_selection.explainability.models import ExplanationCard
from stock_selection.models import RankingResult
from stock_selection.scoring.composite import PillarScoreAssembly


def build_explanation_cards(
    rankings: list[RankingResult],
    assemblies: list[PillarScoreAssembly],
    *,
    top_strengths: int = 2,
    top_risks: int = 2,
) -> list[ExplanationCard]:
    assembly_by_ticker = {assembly.ticker: assembly for assembly in assemblies}
    cards: list[ExplanationCard] = []
    for ranking in rankings:
        assembly = assembly_by_ticker.get(ranking.ticker)
        if assembly is None:
            raise ValueError(
                "Explanation cards require a matching pillar assembly for each ranking "
                f"result (missing={ranking.ticker})."
            )

        sorted_scores = sorted(
            ranking.pillar_scores.items(),
            key=lambda item: (-float(item[1]), str(item[0])),
        )
        weakest_scores = sorted(
            ranking.pillar_scores.items(),
            key=lambda item: (float(item[1]), str(item[0])),
        )

        strengths = [
            f"{pillar}={score:.2f}" for pillar, score in sorted_scores[:top_strengths]
        ]
        risks = [f"{pillar}={score:.2f}" for pillar, score in weakest_scores[:top_risks]]
        for trace in ranking.penalty_traces:
            risks.append(f"penalty:{trace.rule_name}")
        if assembly.missing_pillars:
            risks.append(f"missing:{','.join(assembly.missing_pillars)}")

        summary = (
            f"Final score {ranking.final_score:.2f} from weighted score "
            f"{ranking.weighted_score:.2f} with {len(ranking.penalty_traces)} penalties."
        )

        cards.append(
            ExplanationCard(
                ticker=ranking.ticker,
                summary=summary,
                strengths=strengths,
                risks=risks,
            )
        )

    return cards
