"""Tests for the experimental isForStandardProduct field on capacity groups.

Each balancing capacity price, volume and demand group carries an optional,
nullable ``isForStandardProduct`` flag. Absent yields the ``UNSET`` sentinel,
an explicit null yields ``None``. These tests pin that distinction, the
round-trip through ``to_dict`` and backward compatibility with payloads that
predate the field.
"""

from typing import Any

import pytest

from balancing_services.models.balancing_capacity_demands import BalancingCapacityDemands
from balancing_services.models.balancing_capacity_prices import BalancingCapacityPrices
from balancing_services.models.balancing_capacity_volumes import BalancingCapacityVolumes
from balancing_services.types import Unset

GroupModel = type[BalancingCapacityPrices] | type[BalancingCapacityVolumes] | type[BalancingCapacityDemands]


@pytest.fixture(params=["prices", "volumes", "demands"])
def model(request: pytest.FixtureRequest) -> GroupModel:
    """Each capacity group model that carries isForStandardProduct."""
    return GROUP_MODELS[request.param]


class TestIsForStandardProductParsing:
    """Test how isForStandardProduct parses on a capacity group."""

    @pytest.mark.parametrize("value", [True, False])
    def test_boolean_is_parsed(self, model: GroupModel, value: bool):
        """A boolean isForStandardProduct parses into that bool."""
        assert make_group(model, {"isForStandardProduct": value}).is_for_standard_product is value

    def test_null_is_none(self, model: GroupModel):
        """An explicit null parses to None."""
        assert make_group(model, {"isForStandardProduct": None}).is_for_standard_product is None

    def test_absent_field_is_unset(self, model: GroupModel):
        """An absent isForStandardProduct defaults to the UNSET sentinel."""
        assert isinstance(make_group(model).is_for_standard_product, Unset)


class TestIsForStandardProductRoundTrip:
    """Test that from_dict -> to_dict preserves the field."""

    @pytest.mark.parametrize("value", [True, False, None])
    def test_present_field_round_trips(self, model: GroupModel, value: bool | None):
        """A true, false or null value survives a from_dict/to_dict round trip."""
        payload = {**BASE_GROUPS[model], "isForStandardProduct": value}

        assert model.from_dict(payload).to_dict() == payload

    def test_absent_field_is_omitted_from_to_dict(self, model: GroupModel):
        """An UNSET field is dropped from the serialized dict entirely."""
        assert make_group(model).to_dict() == BASE_GROUPS[model]


# Helper functions

GROUP_MODELS: dict[str, GroupModel] = {
    "prices": BalancingCapacityPrices,
    "volumes": BalancingCapacityVolumes,
    "demands": BalancingCapacityDemands,
}

PERIOD: dict[str, Any] = {"startAt": "2025-01-02T00:00:00+00:00", "endAt": "2025-01-02T01:00:00+00:00"}

GROUP_HEADER: dict[str, Any] = {
    "area": "SK",
    "eicCode": "10YSK-SEPS-----K",
    "reserveType": "mFRR",
    "direction": "up",
    "procurement": {"procuredAt": "2025-01-01T10:00:00+00:00"},
}

BASE_GROUPS: dict[GroupModel, dict[str, Any]] = {
    BalancingCapacityPrices: {
        **GROUP_HEADER,
        "currency": "EUR",
        "prices": [{"period": PERIOD, "pricePerMwPerHour": 12.5}],
    },
    BalancingCapacityVolumes: {
        **GROUP_HEADER,
        "volumes": [{"period": PERIOD, "volumeInMw": 100.0}],
    },
    BalancingCapacityDemands: {
        **GROUP_HEADER,
        "demandBasis": "additive",
        "demands": [{"period": PERIOD, "totalDemandInMw": 120.0, "localDemandInMw": 80.0}],
    },
}


def make_group(
    model: GroupModel, overrides: dict[str, Any] | None = None
) -> BalancingCapacityPrices | BalancingCapacityVolumes | BalancingCapacityDemands:
    """Create a capacity group of the given model from a happy-path payload with the given overrides."""
    return model.from_dict({**BASE_GROUPS[model], **(overrides or {})})
