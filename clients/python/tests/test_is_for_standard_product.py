"""Tests for the experimental isForStandardProduct field on capacity price groups.

Each balancing capacity price group carries an optional, nullable
``isForStandardProduct`` flag. Absent yields the ``UNSET`` sentinel, an
explicit null yields ``None``. These tests pin that distinction, the
round-trip through ``to_dict`` and backward compatibility with payloads that
predate the field.
"""

from typing import Any

import pytest

from balancing_services.models.balancing_capacity_prices import BalancingCapacityPrices
from balancing_services.types import Unset


class TestIsForStandardProductParsing:
    """Test how isForStandardProduct parses on a capacity price group."""

    @pytest.mark.parametrize("value", [True, False])
    def test_boolean_is_parsed(self, value: bool):
        """A boolean isForStandardProduct parses into that bool."""
        assert make_group({"isForStandardProduct": value}).is_for_standard_product is value

    def test_null_is_none(self):
        """An explicit null parses to None."""
        assert make_group({"isForStandardProduct": None}).is_for_standard_product is None

    def test_absent_field_is_unset(self):
        """An absent isForStandardProduct defaults to the UNSET sentinel."""
        assert isinstance(make_group().is_for_standard_product, Unset)


class TestIsForStandardProductRoundTrip:
    """Test that from_dict -> to_dict preserves the field."""

    @pytest.mark.parametrize("value", [True, False, None])
    def test_present_field_round_trips(self, value: bool | None):
        """A true, false or null value survives a from_dict/to_dict round trip."""
        payload = {**BASE_GROUP, "isForStandardProduct": value}

        assert BalancingCapacityPrices.from_dict(payload).to_dict() == payload

    def test_absent_field_is_omitted_from_to_dict(self):
        """An UNSET field is dropped from the serialized dict entirely."""
        assert make_group().to_dict() == BASE_GROUP


# Helper functions

BASE_GROUP: dict[str, Any] = {
    "area": "SK",
    "eicCode": "10YSK-SEPS-----K",
    "reserveType": "mFRR",
    "direction": "up",
    "currency": "EUR",
    "procurement": {"procuredAt": "2025-01-01T10:00:00+00:00"},
    "prices": [
        {
            "period": {"startAt": "2025-01-02T00:00:00+00:00", "endAt": "2025-01-02T01:00:00+00:00"},
            "pricePerMwPerHour": 12.5,
        }
    ],
}


def make_group(overrides: dict[str, Any] | None = None) -> BalancingCapacityPrices:
    """Create a BalancingCapacityPrices group from a happy-path payload with the given overrides."""
    return BalancingCapacityPrices.from_dict({**BASE_GROUP, **(overrides or {})})
