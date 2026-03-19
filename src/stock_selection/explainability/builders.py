from __future__ import annotations

from stock_selection.explainability.models import ExplanationCard, ExplanationPillarDetail
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
    top_rank_score = rankings[0].final_score if rankings else 0.0
    cards: list[ExplanationCard] = []
    for rank_position, ranking in enumerate(rankings, start=1):
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

        top_pillars = [
            ExplanationPillarDetail(pillar=pillar, score=score)
            for pillar, score in sorted_scores[:top_strengths]
        ]
        weakest_pillars = [
            ExplanationPillarDetail(pillar=pillar, score=score)
            for pillar, score in weakest_scores[:top_risks]
        ]
        strengths = [f"{item.pillar}={item.score:.2f}" for item in top_pillars]
        risks = [f"{item.pillar}={item.score:.2f}" for item in weakest_pillars]
        penalty_rules = [trace.rule_name for trace in ranking.penalty_traces]
        for trace in ranking.penalty_traces:
            risks.append(f"penalty:{trace.rule_name}")
        if assembly.missing_pillars:
            risks.append(f"missing:{','.join(assembly.missing_pillars)}")

        summary = (
            f"Final score {ranking.final_score:.2f} from weighted score "
            f"{ranking.weighted_score:.2f} with {len(ranking.penalty_traces)} penalties "
            f"and assembly status {assembly.assembly_status}."
        )
        next_ranking = rankings[rank_position] if rank_position < len(rankings) else None
        score_gap_to_next_rank = (
            ranking.final_score - next_ranking.final_score
            if next_ranking is not None
            else None
        )

        cards.append(
            ExplanationCard(
                ticker=ranking.ticker,
                as_of=ranking.as_of,
                profile_name=ranking.profile_name,
                rank_position=rank_position,
                available_pillar_count=assembly.available_pillar_count,
                minimum_required_pillars=assembly.min_required_pillars,
                meets_minimum_pillars=assembly.meets_minimum_pillars,
                missing_pillar_count=len(assembly.missing_pillars),
                penalty_count=len(ranking.penalty_traces),
                score_gap_to_top_rank=top_rank_score - ranking.final_score,
                score_gap_to_next_rank=score_gap_to_next_rank,
                final_score=ranking.final_score,
                weighted_score=ranking.weighted_score,
                total_penalty=ranking.total_penalty,
                assembly_status=assembly.assembly_status,
                missing_pillars=list(assembly.missing_pillars),
                top_pillars=top_pillars,
                weakest_pillars=weakest_pillars,
                penalty_rules=penalty_rules,
                summary=summary,
                strengths=strengths,
                risks=risks,
            )
        )

    return cards
