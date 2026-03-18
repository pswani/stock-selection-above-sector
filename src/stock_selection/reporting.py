from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd

from stock_selection.models import PillarScoreCard, RankingResult
from stock_selection.scoring.composite import PillarScoreAssembly

PILLAR_SCORE_CARD_BASE_COLUMNS = [
    "ticker",
    "pillar",
    "score",
    "coverage_ratio",
    "as_of",
]
RANKING_RESULT_BASE_COLUMNS = [
    "ticker",
    "as_of",
    "profile_name",
    "weighted_score",
    "total_penalty",
    "final_score",
    "penalty_count",
]
PILLAR_ASSEMBLY_BASE_COLUMNS = [
    "ticker",
    "as_of",
    "available_pillar_count",
    "min_required_pillars",
    "meets_minimum_pillars",
    "assembly_status",
    "missing_pillars",
]


def pillar_score_cards_to_frame(cards: list[PillarScoreCard]) -> pd.DataFrame:
    diagnostic_columns = _prefixed_union_columns(
        dictionaries=[card.diagnostics for card in cards],
        prefix="diagnostic_",
    )
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
    columns = [*PILLAR_SCORE_CARD_BASE_COLUMNS, *diagnostic_columns]
    return pd.DataFrame(rows, columns=columns)


def ranking_results_to_frame(results: list[RankingResult]) -> pd.DataFrame:
    pillar_columns = _prefixed_union_columns(
        dictionaries=[result.pillar_scores for result in results],
        prefix="pillar_",
    )
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
    columns = [*RANKING_RESULT_BASE_COLUMNS, *pillar_columns]
    return pd.DataFrame(rows, columns=columns)


def pillar_score_assemblies_to_frame(
    assemblies: list[PillarScoreAssembly],
) -> pd.DataFrame:
    score_columns = _prefixed_union_columns(
        dictionaries=[assembly.pillar_scores for assembly in assemblies],
        prefix="pillar_score_",
    )
    coverage_columns = _prefixed_union_columns(
        dictionaries=[assembly.pillar_coverages for assembly in assemblies],
        prefix="pillar_coverage_",
    )
    rows = []
    for assembly in assemblies:
        rows.append(
            {
                "ticker": assembly.ticker,
                "as_of": assembly.as_of.isoformat() if assembly.as_of is not None else None,
                "available_pillar_count": assembly.available_pillar_count,
                "min_required_pillars": assembly.min_required_pillars,
                "meets_minimum_pillars": assembly.meets_minimum_pillars,
                "assembly_status": assembly.assembly_status,
                "missing_pillars": ",".join(assembly.missing_pillars),
                **{
                    f"pillar_score_{pillar}": score
                    for pillar, score in assembly.pillar_scores.items()
                },
                **{
                    f"pillar_coverage_{pillar}": coverage
                    for pillar, coverage in assembly.pillar_coverages.items()
                },
            }
        )
    columns = [
        *PILLAR_ASSEMBLY_BASE_COLUMNS,
        *score_columns,
        *coverage_columns,
    ]
    return pd.DataFrame(rows, columns=columns)


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


def write_pillar_score_assemblies_csv(
    assemblies: list[PillarScoreAssembly],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pillar_score_assemblies_to_frame(assemblies).to_csv(output, index=False)
    return output


def _prefixed_union_columns(
    *,
    dictionaries: Sequence[Mapping[str, object]],
    prefix: str,
) -> list[str]:
    keys = sorted({key for mapping in dictionaries for key in mapping})
    return [f"{prefix}{key}" for key in keys]
