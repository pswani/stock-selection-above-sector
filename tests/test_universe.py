import pytest

from stock_selection.models import Classification, Currency, Security, SecurityType
from stock_selection.universe import (
    PeerLevel,
    UniverseFilterConfig,
    build_peer_groups,
    build_standard_peer_maps,
    evaluate_investability,
    filter_investable_universe,
)


def _security(
    ticker: str,
    *,
    active: bool = True,
    security_type: SecurityType = SecurityType.COMMON_STOCK,
    currency: Currency = Currency.USD,
    sector: str | None = "Information Technology",
    industry: str | None = "Software",
    sub_industry: str | None = "Application Software",
    exchange: str | None = "NASDAQ",
) -> Security:
    classification = None
    if (
        sector is not None
        or industry is not None
        or sub_industry is not None
        or exchange is not None
    ):
        classification = Classification(
            sector=sector or "Unknown",
            industry=industry,
            sub_industry=sub_industry,
            exchange=exchange,
        )

    return Security(
        ticker=ticker,
        is_active=active,
        security_type=security_type,
        currency=currency,
        classification=classification,
    )


def test_filter_investable_universe_defaults_to_active_common_with_classification() -> None:
    securities = [
        _security("AAPL"),
        _security("SPY", security_type=SecurityType.ETF),
        _security("X", active=False),
        Security(ticker="NOCLASS", is_active=True),
    ]

    result = filter_investable_universe(securities)
    assert [item.ticker for item in result] == ["AAPL"]


def test_evaluate_investability_returns_exclusion_reasons() -> None:
    securities = [
        _security("ADR1", security_type=SecurityType.ADR),
        _security("INR1", currency=Currency.INR),
        _security("NYSE1", exchange="NYSE"),
    ]
    config = UniverseFilterConfig(
        allowed_security_types=(SecurityType.COMMON_STOCK,),
        allowed_currencies=(Currency.USD,),
        allowed_exchanges=("NASDAQ",),
    )

    result = evaluate_investability(securities, config=config)

    assert result.eligible == []
    assert result.excluded_reasons["ADR1"] == ["security_type_not_allowed"]
    assert result.excluded_reasons["INR1"] == ["currency_not_allowed"]
    assert result.excluded_reasons["NYSE1"] == ["exchange_not_allowed"]


def test_build_peer_groups_groups_and_sorts_members_deterministically() -> None:
    securities = [
        _security(
            "MSFT",
            sector="Information Technology",
            industry="Software",
            sub_industry="Application Software",
        ),
        _security(
            "NVDA",
            sector="Information Technology",
            industry="Semiconductors",
            sub_industry="Semiconductor Devices",
        ),
        _security(
            "AAPL",
            sector="Information Technology",
            industry="Hardware",
            sub_industry="Consumer Electronics",
        ),
        _security(
            "LLY",
            sector="Health Care",
            industry="Biotechnology",
            sub_industry="Large Cap Pharma",
        ),
    ]

    groups = build_peer_groups(securities, level=PeerLevel.SECTOR)

    assert [group.name for group in groups] == [
        "sector:Health Care",
        "sector:Information Technology",
    ]
    assert groups[1].members == ["AAPL", "MSFT", "NVDA"]


def test_build_peer_groups_respects_min_group_size() -> None:
    securities = [
        _security("MSFT", industry="Software"),
        _security("ORCL", industry="Software"),
        _security("LLY", industry="Biotechnology"),
    ]

    groups = build_peer_groups(securities, level=PeerLevel.INDUSTRY, min_group_size=2)

    assert len(groups) == 1
    assert groups[0].name == "industry:Software"
    assert groups[0].members == ["MSFT", "ORCL"]


def test_build_standard_peer_maps_returns_sector_industry_sub_industry() -> None:
    securities = [
        _security("MSFT"),
        _security(
            "NVDA",
            industry="Semiconductors",
            sub_industry="Semiconductor Devices",
        ),
    ]

    peer_maps = build_standard_peer_maps(securities)

    assert set(peer_maps) == {PeerLevel.SECTOR, PeerLevel.INDUSTRY, PeerLevel.SUB_INDUSTRY}
    assert peer_maps[PeerLevel.SECTOR][0].name.startswith("sector:")


def test_build_peer_groups_rejects_invalid_min_group_size() -> None:
    with pytest.raises(ValueError, match="min_group_size must be >= 1"):
        build_peer_groups([_security("MSFT")], level=PeerLevel.SECTOR, min_group_size=0)
