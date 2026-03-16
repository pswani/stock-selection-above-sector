from __future__ import annotations

from dataclasses import dataclass, field

from stock_selection.models import Currency, Security, SecurityType


@dataclass(frozen=True, slots=True)
class UniverseFilterConfig:
    require_active: bool = True
    allowed_security_types: tuple[SecurityType, ...] = (SecurityType.COMMON_STOCK,)
    allowed_currencies: tuple[Currency, ...] | None = None
    allowed_exchanges: tuple[str, ...] | None = None
    require_classification: bool = True


@dataclass(frozen=True, slots=True)
class UniverseFilterResult:
    eligible: list[Security]
    excluded_reasons: dict[str, list[str]] = field(default_factory=dict)


def evaluate_investability(
    securities: list[Security],
    config: UniverseFilterConfig | None = None,
) -> UniverseFilterResult:
    effective = config or UniverseFilterConfig()
    excluded: dict[str, list[str]] = {}
    eligible: list[Security] = []

    for security in securities:
        reasons: list[str] = []
        if effective.require_active and not security.is_active:
            reasons.append("inactive_security")

        if security.security_type not in effective.allowed_security_types:
            reasons.append("security_type_not_allowed")

        if effective.allowed_currencies is not None and security.currency not in effective.allowed_currencies:
            reasons.append("currency_not_allowed")

        if effective.allowed_exchanges is not None:
            exchange = security.classification.exchange if security.classification else None
            if exchange not in effective.allowed_exchanges:
                reasons.append("exchange_not_allowed")

        if effective.require_classification and security.classification is None:
            reasons.append("missing_classification")

        if reasons:
            excluded[security.ticker] = reasons
            continue

        eligible.append(security)

    eligible_sorted = sorted(eligible, key=lambda item: item.ticker)
    return UniverseFilterResult(eligible=eligible_sorted, excluded_reasons=excluded)


def filter_investable_universe(
    securities: list[Security],
    config: UniverseFilterConfig | None = None,
) -> list[Security]:
    return evaluate_investability(securities, config=config).eligible
