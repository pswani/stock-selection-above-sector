from __future__ import annotations

from datetime import date
from typing import Protocol

import pandas as pd

from stock_selection.config import load_env_settings
from stock_selection.models import (
    CorporateActionSnapshot,
    EstimateSnapshot,
    FundamentalSnapshot,
    OwnershipSnapshot,
    PeerGroup,
    PriceBar,
    Security,
)


class UniverseProvider(Protocol):
    def list_securities(self, as_of: date) -> list[Security]: ...


class ClassificationProvider(Protocol):
    def get_peer_groups(self, tickers: list[str], as_of: date) -> list[PeerGroup]: ...


class PriceDataProvider(Protocol):
    def get_price_history(self, tickers: list[str], start: date, end: date) -> list[PriceBar]: ...


class FundamentalsProvider(Protocol):
    def get_fundamentals(self, tickers: list[str], as_of: date) -> list[FundamentalSnapshot]: ...


class EstimatesProvider(Protocol):
    def get_estimates(self, tickers: list[str], as_of: date) -> list[EstimateSnapshot]: ...


class CorporateActionsProvider(Protocol):
    def get_corporate_actions(
        self,
        tickers: list[str],
        start: date,
        end: date,
    ) -> list[CorporateActionSnapshot]: ...


class OwnershipProvider(Protocol):
    def get_ownership_and_short_interest(
        self,
        tickers: list[str],
        as_of: date,
    ) -> list[OwnershipSnapshot]: ...


class ModelDumpable(Protocol):
    def model_dump(self) -> dict[str, object]: ...


def model_list_to_frame(records: list[ModelDumpable]) -> pd.DataFrame:
    return pd.DataFrame([record.model_dump() for record in records])


def build_primary_provider():
    from stock_selection.data.fmp import FinancialModelingPrepProvider

    env = load_env_settings()
    if not env.stock_selection_fmp_api_key:
        raise ValueError(
            "Missing FMP API key. Set STOCK_SELECTION_FMP_API_KEY in your environment or .env file."
        )
    return FinancialModelingPrepProvider(
        api_key=env.stock_selection_fmp_api_key,
        base_url=env.stock_selection_fmp_base_url,
    )
