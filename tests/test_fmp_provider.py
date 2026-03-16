from datetime import date

import pytest

from stock_selection.data.fmp import (
    FinancialModelingPrepProvider,
    FmpProviderError,
    FmpProviderUnsupportedCapabilityError,
)
from stock_selection.data.providers import build_primary_provider


class StubFmpProvider(FinancialModelingPrepProvider):
    def __init__(self) -> None:
        super().__init__(api_key="demo")

    def _get_json(self, path: str, query=None):  # type: ignore[override]
        if path == "stock/list":
            return [
                {
                    "symbol": "MSFT",
                    "name": "Microsoft",
                    "currency": "USD",
                    "exchangeShortName": "NASDAQ",
                    "type": "stock",
                    "isActivelyTrading": True,
                }
            ]
        if path.startswith("historical-price-full/"):
            return {
                "historical": [
                    {
                        "date": "2026-01-30",
                        "open": 100.0,
                        "high": 110.0,
                        "low": 95.0,
                        "close": 105.0,
                        "adjClose": 104.5,
                        "volume": 1234,
                    }
                ]
            }
        if path.startswith("ratios-ttm/"):
            return [
                {
                    "peRatioTTM": 22.0,
                    "pegRatioTTM": 1.2,
                    "priceToSalesRatioTTM": 4.0,
                    "enterpriseValueMultipleTTM": 12.0,
                    "operatingProfitMarginTTM": 0.32,
                    "grossProfitMarginTTM": 0.7,
                    "returnOnEquityTTM": 0.3,
                    "debtEquityRatioTTM": 0.4,
                }
            ]
        if path.startswith("financial-growth/"):
            return [{"revenueGrowth": 0.1, "epsgrowth": 0.2}]
        if path.startswith("analyst-estimates/"):
            return [{"estimatedRevenueAvg": 0.11, "estimatedEpsAvg": 0.15}]
        if path.startswith("profile/"):
            return [{"sector": "Information Technology", "industry": "Software"}]
        if path.startswith("historical-price-full/stock_dividend/"):
            return {"historical": [{"date": "2026-01-15", "dividend": 0.75}]}
        if path.startswith("historical-price-full/stock_split/"):
            return {"historical": [{"date": "2026-01-20", "numerator": 2, "denominator": 1}]}
        if path.startswith("key-metrics-ttm/"):
            return [
                {
                    "institutionalOwnershipPercentageTTM": 0.72,
                    "insiderOwnershipPercentageTTM": 0.03,
                }
            ]
        if path.startswith("short-interest/"):
            return [{"shortPercentFloat": 1.5}]
        return []


class NoOwnershipOrCorporateActionsStub(FinancialModelingPrepProvider):
    def __init__(self) -> None:
        super().__init__(api_key="demo")

    def _get_json(self, path: str, query=None):  # type: ignore[override]
        if path.startswith(("historical-price-full/stock_dividend/", "historical-price-full/stock_split/")):
            raise FmpProviderError("not supported")
        if path.startswith(("key-metrics-ttm/", "short-interest/")):
            raise FmpProviderError("not supported")
        return []


class PartialOwnershipStub(FinancialModelingPrepProvider):
    def __init__(self) -> None:
        super().__init__(api_key="demo")

    def _get_json(self, path: str, query=None):  # type: ignore[override]
        if path.startswith("key-metrics-ttm/"):
            return [{}]
        if path.startswith("short-interest/"):
            return []
        return []


def test_fmp_provider_parses_price_fundamental_and_estimate_snapshots() -> None:
    provider = StubFmpProvider()

    prices = provider.get_price_history(["MSFT"], start=date(2026, 1, 1), end=date(2026, 1, 31))
    fundamentals = provider.get_fundamentals(["MSFT"], as_of=date(2026, 1, 31))
    estimates = provider.get_estimates(["MSFT"], as_of=date(2026, 1, 31))

    assert prices[0].ticker == "MSFT"
    assert prices[0].close == 105.0
    assert fundamentals[0].return_on_equity == 0.3
    assert fundamentals[0].revenue_growth_yoy == 0.1
    assert estimates[0].forward_pe == 22.0
    assert estimates[0].next_year_eps_growth == 0.15


def test_fmp_provider_builds_peer_groups() -> None:
    provider = StubFmpProvider()
    groups = provider.get_peer_groups(["MSFT", "ADBE"], as_of=date(2026, 1, 31))

    assert len(groups) == 2
    by_level = {group.level: group for group in groups}
    assert by_level["industry"].members == ["ADBE", "MSFT"]
    assert by_level["sector"].members == ["ADBE", "MSFT"]


def test_build_primary_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STOCK_SELECTION_FMP_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Missing FMP API key"):
        build_primary_provider()


def test_fmp_provider_parses_corporate_actions_when_supported() -> None:
    provider = StubFmpProvider()
    actions = provider.get_corporate_actions(["MSFT"], start=date(2026, 1, 1), end=date(2026, 1, 31))

    assert [item.action_type for item in actions] == ["dividend", "split"]
    assert actions[0].value == 0.75
    assert actions[1].value == 2.0


def test_fmp_provider_parses_ownership_and_short_interest_when_supported() -> None:
    provider = StubFmpProvider()
    snapshots = provider.get_ownership_and_short_interest(["MSFT"], as_of=date(2026, 1, 31))

    assert len(snapshots) == 1
    assert snapshots[0].institutional_ownership == 0.72
    assert snapshots[0].insider_ownership == 0.03
    assert snapshots[0].short_interest_percent_float == 1.5


def test_fmp_provider_returns_none_for_missing_ownership_fields() -> None:
    provider = PartialOwnershipStub()
    snapshots = provider.get_ownership_and_short_interest(["MSFT"], as_of=date(2026, 1, 31))

    assert len(snapshots) == 1
    assert snapshots[0].institutional_ownership is None
    assert snapshots[0].insider_ownership is None
    assert snapshots[0].short_interest_percent_float is None


def test_fmp_provider_explicitly_reports_unsupported_corporate_actions() -> None:
    provider = NoOwnershipOrCorporateActionsStub()
    with pytest.raises(FmpProviderUnsupportedCapabilityError, match="corporate actions endpoint"):
        provider.get_corporate_actions(["MSFT"], start=date(2026, 1, 1), end=date(2026, 1, 31))


def test_fmp_provider_explicitly_reports_unsupported_ownership() -> None:
    provider = NoOwnershipOrCorporateActionsStub()
    with pytest.raises(FmpProviderUnsupportedCapabilityError, match="ownership/short-interest endpoint"):
        provider.get_ownership_and_short_interest(["MSFT"], as_of=date(2026, 1, 31))
