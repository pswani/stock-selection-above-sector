from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from stock_selection.models import FactorObservation


@dataclass(slots=True)
class FactorInputBundle:
    as_of: date
    tickers: list[str]


class FactorCalculator:
    name: str

    def compute(self, bundle: FactorInputBundle) -> list[FactorObservation]:
        raise NotImplementedError
