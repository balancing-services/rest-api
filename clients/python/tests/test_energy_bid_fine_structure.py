"""Tests for the experimental bid fine-structure fields on EnergyBid.

The 2.0 API added four nullable, optional fields to the energy bid object:
``divisible``, ``eligibleActivationTypes``, ``minimumVolumeInMw`` and
``availability``. Null and absent are contractually equivalent ("value not
available"), but the generated client distinguishes them in memory: absent
yields the ``UNSET`` sentinel, explicit null yields ``None``. These tests pin
that distinction, the round-trip through ``to_dict``, the pass-through
behaviour of the literal-enum fields on unknown values, and backward
compatibility with payloads that predate the new fields.
"""

from typing import Any

import pytest

from balancing_services.models.bid_availability import (
    BID_AVAILABILITY_VALUES,
    check_bid_availability,
)
from balancing_services.models.eligible_activation_type import (
    ELIGIBLE_ACTIVATION_TYPE_VALUES,
    check_eligible_activation_type,
)
from balancing_services.models.energy_bid import EnergyBid
from balancing_services.types import UNSET, Unset


class TestEnergyBidFieldsPresent:
    """Test that populated fine-structure fields parse into plain Python values."""

    def test_divisible_is_parsed_as_bool(self):
        """divisible parses into a bool."""
        assert make_bid({"divisible": True}).divisible is True
        assert make_bid({"divisible": False}).divisible is False

    def test_eligible_activation_types_is_parsed_as_list_of_strings(self):
        """eligibleActivationTypes parses into a list of bare enum strings."""
        result = make_bid({"eligibleActivationTypes": ["direct", "scheduled"]})

        assert result.eligible_activation_types == ["direct", "scheduled"]

    def test_minimum_volume_in_mw_is_parsed_as_number(self):
        """minimumVolumeInMw parses into a number."""
        assert make_bid({"minimumVolumeInMw": 1.5}).minimum_volume_in_mw == 1.5

    def test_availability_is_parsed_as_string(self):
        """availability parses into a bare enum string."""
        assert make_bid({"availability": "available"}).availability == "available"

    def test_all_four_fields_parse_together(self):
        """A bid carrying every fine-structure field parses all of them."""
        result = make_bid(
            {
                "divisible": True,
                "eligibleActivationTypes": ["direct", "scheduled"],
                "minimumVolumeInMw": 1,
                "availability": "available",
            }
        )

        assert result.volume_in_mw == 100.0
        assert result.price_per_mwh == 55.25
        assert result.divisible is True
        assert result.eligible_activation_types == ["direct", "scheduled"]
        assert result.minimum_volume_in_mw == 1
        assert result.availability == "available"


class TestEnergyBidExplicitNull:
    """Test that an explicit null parses into None for every fine-structure field."""

    def test_null_divisible_is_none(self):
        """A null divisible parses to None."""
        assert make_bid({"divisible": None}).divisible is None

    def test_null_eligible_activation_types_is_none(self):
        """A null eligibleActivationTypes parses to None."""
        assert make_bid({"eligibleActivationTypes": None}).eligible_activation_types is None

    def test_null_minimum_volume_in_mw_is_none(self):
        """A null minimumVolumeInMw parses to None."""
        assert make_bid({"minimumVolumeInMw": None}).minimum_volume_in_mw is None

    def test_null_availability_is_none(self):
        """A null availability parses to None."""
        assert make_bid({"availability": None}).availability is None


class TestEnergyBidAbsentFields:
    """Test that absent fine-structure fields yield the UNSET sentinel, not None."""

    def test_absent_fields_are_unset(self):
        """Every absent fine-structure field defaults to the UNSET sentinel."""
        result = make_bid()

        assert result.divisible is UNSET
        assert result.eligible_activation_types is UNSET
        assert result.minimum_volume_in_mw is UNSET
        assert result.availability is UNSET

    def test_unset_is_distinct_from_none(self):
        """Absent differs from explicit null only in the sentinel; both are falsy."""
        absent = make_bid()
        explicit_null = make_bid(
            {
                "divisible": None,
                "eligibleActivationTypes": None,
                "minimumVolumeInMw": None,
                "availability": None,
            }
        )

        assert isinstance(absent.divisible, Unset)
        assert not isinstance(explicit_null.divisible, Unset)
        assert explicit_null.divisible is None
        assert not absent.divisible
        assert not explicit_null.divisible


class TestEnergyBidRoundTrip:
    """Test that from_dict -> to_dict preserves the fine-structure fields."""

    def test_populated_fields_round_trip(self):
        """Populated fine-structure values survive a from_dict/to_dict round trip."""
        payload = {
            "volumeInMw": 100,
            "pricePerMwh": 55.25,
            "divisible": True,
            "eligibleActivationTypes": ["direct", "scheduled"],
            "minimumVolumeInMw": 1,
            "availability": "available",
        }

        assert EnergyBid.from_dict(payload).to_dict() == payload

    def test_explicit_null_serializes_as_none(self):
        """Explicit nulls are kept as None keys in the serialized dict."""
        result = make_bid(
            {
                "divisible": None,
                "eligibleActivationTypes": None,
                "minimumVolumeInMw": None,
                "availability": None,
            }
        ).to_dict()

        assert result["divisible"] is None
        assert result["eligibleActivationTypes"] is None
        assert result["minimumVolumeInMw"] is None
        assert result["availability"] is None

    def test_absent_fields_are_omitted_from_to_dict(self):
        """UNSET fields are dropped from the serialized dict entirely."""
        result = make_bid().to_dict()

        assert result == {"volumeInMw": 100.0, "pricePerMwh": 55.25}

    def test_eligible_activation_types_round_trips_as_new_list(self):
        """The activation-type list is rebuilt, not aliased, on serialization."""
        bid = make_bid({"eligibleActivationTypes": ["direct"]})
        result = bid.to_dict()

        assert result["eligibleActivationTypes"] == ["direct"]
        assert result["eligibleActivationTypes"] is not bid.eligible_activation_types


class TestEnumCheckers:
    """Test the literal-enum check helpers directly."""

    def test_known_values_pass_through(self):
        """Known enum values are returned unchanged as bare strings."""
        assert check_bid_availability("withdrawn") == "withdrawn"
        assert check_eligible_activation_type("scheduled") == "scheduled"

    def test_declared_value_sets(self):
        """The generated value sets match the spec's enum members."""
        assert BID_AVAILABILITY_VALUES == {
            "available",
            "unavailable",
            "cancelled",
            "withdrawn",
        }
        assert ELIGIBLE_ACTIVATION_TYPE_VALUES == {"direct", "scheduled"}

    def test_unknown_availability_raises_type_error(self):
        """check_bid_availability rejects an unknown value with TypeError."""
        with pytest.raises(TypeError, match="expired"):
            check_bid_availability("expired")

    def test_unknown_activation_type_raises_type_error(self):
        """check_eligible_activation_type rejects an unknown value with TypeError."""
        with pytest.raises(TypeError, match="manual"):
            check_eligible_activation_type("manual")


class TestUnknownEnumValuesInPayload:
    """Test that from_dict tolerates enum values the client does not know.

    ``from_dict`` calls the check helpers inside a try/except that swallows the
    TypeError and falls back to casting the raw payload value. An unknown enum
    string therefore passes straight through instead of raising — which is what
    lets an old client keep parsing a response from a newer server.
    """

    def test_unknown_availability_passes_through(self):
        """An unrecognised availability string is kept verbatim rather than raising."""
        assert make_bid({"availability": "expired"}).availability == "expired"

    def test_unknown_activation_type_keeps_whole_list_verbatim(self):
        """One unknown element makes the whole list fall back to the raw payload value."""
        payload_list = ["direct", "manual"]
        result = make_bid({"eligibleActivationTypes": payload_list})

        assert result.eligible_activation_types is payload_list

    def test_non_string_availability_passes_through(self):
        """A non-string availability is kept verbatim rather than raising."""
        assert make_bid({"availability": 42}).availability == 42

    def test_non_list_eligible_activation_types_passes_through(self):
        """A non-list eligibleActivationTypes is kept verbatim rather than raising."""
        assert make_bid({"eligibleActivationTypes": "direct"}).eligible_activation_types == "direct"

    def test_unknown_enum_values_survive_to_dict(self):
        """Unknown enum values round-trip through to_dict, so a relay keeps them intact."""
        serialized = make_bid({"availability": "expired", "eligibleActivationTypes": ["direct", "manual"]}).to_dict()

        assert serialized["availability"] == "expired"
        assert serialized["eligibleActivationTypes"] == ["direct", "manual"]


class TestBackwardCompatibility:
    """Test that pre-fine-structure bid payloads still parse."""

    def test_old_shape_payload_parses(self):
        """A bid with only volumeInMw/pricePerMwh — no new keys — still parses."""
        result = EnergyBid.from_dict({"volumeInMw": 250.0, "pricePerMwh": -12.5})

        assert result.volume_in_mw == 250.0
        assert result.price_per_mwh == -12.5
        assert result.divisible is UNSET
        assert result.availability is UNSET

    def test_unknown_keys_land_in_additional_properties(self):
        """Keys the client does not know are preserved as additional properties."""
        result = EnergyBid.from_dict({"volumeInMw": 100.0, "pricePerMwh": 55.25, "futureField": "x"})

        assert result.additional_keys == ["futureField"]
        assert result["futureField"] == "x"
        assert result.to_dict()["futureField"] == "x"


# Helper functions


def make_bid(overrides: dict[str, Any] | None = None) -> EnergyBid:
    """Create an EnergyBid from a happy-path payload with the given overrides."""
    if overrides is None:
        overrides = {}

    base_data: dict[str, Any] = {
        "volumeInMw": 100.0,
        "pricePerMwh": 55.25,
    }
    data = {**base_data, **overrides}
    return EnergyBid.from_dict(data)
