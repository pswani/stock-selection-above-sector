from __future__ import annotations

from enum import StrEnum

from stock_selection.models import PeerGroup, Security


class PeerLevel(StrEnum):
    SECTOR = "sector"
    INDUSTRY_GROUP = "industry_group"
    INDUSTRY = "industry"
    SUB_INDUSTRY = "sub_industry"


def build_peer_groups(
    securities: list[Security],
    level: PeerLevel,
    min_group_size: int = 1,
) -> list[PeerGroup]:
    if min_group_size < 1:
        raise ValueError("min_group_size must be >= 1")

    grouped: dict[str, set[str]] = {}
    for security in securities:
        if security.classification is None:
            continue
        bucket = getattr(security.classification, level.value)
        if bucket is None:
            continue
        grouped.setdefault(bucket, set()).add(security.ticker)

    peer_groups: list[PeerGroup] = []
    for bucket in sorted(grouped):
        members = sorted(grouped[bucket])
        if len(members) < min_group_size:
            continue
        peer_groups.append(
            PeerGroup(
                name=f"{level.value}:{bucket}",
                level=level.value,
                members=members,
            )
        )
    return peer_groups


def build_standard_peer_maps(
    securities: list[Security],
    min_group_size: int = 1,
) -> dict[PeerLevel, list[PeerGroup]]:
    return {
        PeerLevel.SECTOR: build_peer_groups(securities, level=PeerLevel.SECTOR, min_group_size=min_group_size),
        PeerLevel.INDUSTRY: build_peer_groups(securities, level=PeerLevel.INDUSTRY, min_group_size=min_group_size),
        PeerLevel.SUB_INDUSTRY: build_peer_groups(
            securities,
            level=PeerLevel.SUB_INDUSTRY,
            min_group_size=min_group_size,
        ),
    }
