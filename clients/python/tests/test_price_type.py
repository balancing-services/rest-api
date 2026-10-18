"""Tests for the capacity price type parameter and the experimental price fields.

The balancing capacity prices endpoint takes an optional ``price-type`` query
parameter, and each capacity price carries an optional ``priceType`` field. An
absent field yields the ``UNSET`` sentinel. These tests pin the query parameter,
the round-trip through ``to_dict``, the rejection of unknown enum values and
backward compatibility with payloads that predate the field.
"""

import datetime
from typing import Any

import pytest

from balancing_services.api.default.get_balancing_capacity_prices import _get_kwargs
from balancing_services.models.balancing_capacity_price import BalancingCapacityPrice
from balancing_services.models.price_type import (
    PRICE_TYPE_VALUES,
    check_price_type,
)
from balancing_services.types import UNSET, Unset


class TestPriceTypeQueryParameter:
    """Test how price_type is sent on the capacity prices request."""

    def test_default_sends_average(self):
        """Without an explicit price_type the request asks for the average price."""
        assert make_params()["price-type"] == "average"

    def test_marginal_is_sent(self):
        """price_type="marginal" is sent as the price-type query parameter."""
        assert make_params(price_type="marginal")["price-type"] == "marginal"

    def test_unset_omits_parameter(self):
        """An explicit UNSET drops the parameter, leaving the server default."""
        assert "price-type" not in make_params(price_type=UNSET)


class TestCapacityPriceFieldPresent:
    """Test that a populated experimental field parses into a bare enum string."""

    def test_price_type_is_parsed_as_string(self):
        """priceType parses into a bare enum string."""
        assert make_price({"priceType": "marginal"}).price_type == "marginal"


class TestCapacityPriceAbsentField:
    """Test that an absent experimental field yields the UNSET sentinel, not None."""

    def test_absent_field_is_unset(self):
        """An absent priceType defaults to the UNSET sentinel."""
        assert isinstance(make_price().price_type, Unset)


class TestCapacityPriceRoundTrip:
    """Test that from_dict -> to_dict preserves the experimental field."""

    def test_populated_field_round_trips(self):
        """A populated value survives a from_dict/to_dict round trip."""
        payload = {**BASE_PRICE, "priceType": "average"}

        assert BalancingCapacityPrice.from_dict(payload).to_dict() == payload

    def test_absent_field_is_omitted_from_to_dict(self):
        """An UNSET field is dropped from the serialized dict entirely."""
        assert make_price().to_dict() == BASE_PRICE


class TestEnumChecker:
    """Test the literal-enum check helper directly."""

    def test_declared_value_set(self):
        """The generated value set matches the spec's enum members."""
        assert PRICE_TYPE_VALUES == {"average", "marginal"}

    def test_known_value_passes_through(self):
        """A known enum value is returned unchanged as a bare string."""
        assert check_price_type("marginal") == "marginal"

    def test_unknown_value_raises_type_error(self):
        """The check helper rejects an unknown value with TypeError."""
        with pytest.raises(TypeError, match="median"):
            check_price_type("median")


class TestUnknownEnumValuesInPayload:
    """Test that from_dict rejects enum values the client does not know."""

    def test_unknown_value_raises_type_error(self):
        """An unrecognised priceType fails parsing with TypeError."""
        with pytest.raises(TypeError, match="median"):
            make_price({"priceType": "median"})


class TestBackwardCompatibility:
    """Test that capacity price payloads without priceType still parse."""

    def test_old_shape_payload_parses(self):
        """A price with only period/pricePerMwPerHour still parses."""
        result = BalancingCapacityPrice.from_dict(BASE_PRICE)

        assert result.price_per_mw_per_hour == 12.5
        assert result.period.start_at == datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
        assert result.price_type is UNSET


# Helper functions

BASE_PRICE: dict[str, Any] = {
    "period": {"startAt": "2025-01-01T00:00:00+00:00", "endAt": "2025-01-01T01:00:00+00:00"},
    "pricePerMwPerHour": 12.5,
}


def make_price(overrides: dict[str, Any] | None = None) -> BalancingCapacityPrice:
    """Create a BalancingCapacityPrice from a happy-path payload with the given overrides."""
    return BalancingCapacityPrice.from_dict({**BASE_PRICE, **(overrides or {})})


def make_params(**kwargs: Any) -> dict[str, Any]:
    """Build the capacity prices request query parameters with the given overrides."""
    request = _get_kwargs(
        area="EE",
        period_start_at=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
        period_end_at=datetime.datetime(2025, 1, 2, tzinfo=datetime.timezone.utc),
        reserve_type="aFRR",
        **kwargs,
    )
    return request["params"]
