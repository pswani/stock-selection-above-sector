from __future__ import annotations

from pathlib import Path

import pandas as pd

from stock_selection.models import PillarScoreCard, RankingResult


def pillar_score_cards_to_frame(cards: list[PillarScoreCard]) -> pd.DataFrame:
    rows = []
    for card in cards:
        rows.append(
            {
                "ticker": card.ticker,
                "pillar": card.pillar,
                "score": card.score,
                "coverage_ratio": card.coverage_ratio,
                "as_of": card.as_of.isoformat() if card.as_of is not None else None,
                **{f"diagnostic_{key}": value for key, value in card.diagnostics.items()},
            }
        )
    return pd.DataFrame(rows)


def ranking_results_to_frame(results: list[RankingResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append(
            {
                "ticker": result.ticker,
                "as_of": result.as_of.isoformat(),
                "profile_name": result.profile_name,
                "weighted_score": result.weighted_score,
                "total_penalty": result.total_penalty,
                "final_score": result.final_score,
                **{f"pillar_{k}": v for k, v in result.pillar_scores.items()},
                "penalty_count": len(result.penalty_traces),
            }
        )
    return pd.DataFrame(rows)


def write_ranking_csv(results: list[RankingResult], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    ranking_results_to_frame(results).to_csv(output, index=False)
    return output


def write_pillar_score_cards_csv(cards: list[PillarScoreCard], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pillar_score_cards_to_frame(cards).to_csv(output, index=False)
    return output
