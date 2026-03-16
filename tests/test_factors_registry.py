import pytest
from pydantic import ValidationError

from stock_selection.factors import (
    FactorDefinition,
    FactorRegistry,
    MissingDataPolicy,
    PillarName,
    build_canonical_registry,
)
from stock_selection.models import MetricDirection


def test_factor_definition_rejects_duplicate_required_inputs() -> None:
    with pytest.raises(ValidationError):
        FactorDefinition(
            name="dup_inputs",
            pillar=PillarName.RP,
            direction=MetricDirection.HIGHER_IS_BETTER,
            description="Factor with duplicate dependencies.",
            required_inputs=["prices", "prices"],
        )


def test_registry_rejects_duplicate_registration() -> None:
    definition = FactorDefinition(
        name="custom_factor",
        pillar=PillarName.G,
        direction=MetricDirection.HIGHER_IS_BETTER,
        description="Custom growth factor.",
        required_inputs=["fundamentals.revenue_growth_yoy"],
    )
    registry = FactorRegistry()
    registry.register(definition)

    with pytest.raises(ValueError):
        registry.register(definition)


def test_registry_get_unknown_factor_raises_key_error() -> None:
    registry = FactorRegistry()
    with pytest.raises(KeyError):
        registry.get("does_not_exist")


def test_registry_list_all_is_deterministically_sorted() -> None:
    registry = FactorRegistry()
    second = FactorDefinition(
        name="z_factor",
        pillar=PillarName.V,
        direction=MetricDirection.LOWER_IS_BETTER,
        description="Second factor.",
        required_inputs=["estimates.forward_pe"],
    )
    first = FactorDefinition(
        name="a_factor",
        pillar=PillarName.Q,
        direction=MetricDirection.HIGHER_IS_BETTER,
        description="First factor.",
        required_inputs=["fundamentals.return_on_equity"],
        missing_data_policy=MissingDataPolicy.DROP_SECURITY,
    )
    registry.register(second)
    registry.register(first)

    listed = registry.list_all()
    assert [item.name for item in listed] == ["a_factor", "z_factor"]


def test_build_canonical_registry_contains_one_factor_per_pillar() -> None:
    registry = build_canonical_registry()
    listed = registry.list_all()

    assert len(listed) == 6
    assert {item.pillar for item in listed} == {
        PillarName.RP,
        PillarName.G,
        PillarName.Q,
        PillarName.V,
        PillarName.R,
        PillarName.S,
    }
