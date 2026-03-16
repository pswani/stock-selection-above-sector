from __future__ import annotations

from pathlib import Path

import pandas as pd

from stock_selection.models import RankingResult


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
