"""Tests for the nested procurement object on capacity datasets.

In the 2.0 API the capacity price/volume groupings carry a required
``procurement`` object that nests the ``procuredAt`` timestamp. These tests
verify that the nested structure round-trips through ``from_dict``.
"""
import datetime
from typing import Any

from balancing_services.models.balancing_capacity_prices import BalancingCapacityPrices
from balancing_services.models.balancing_capacity_volumes import BalancingCapacityVolumes


class TestBalancingCapacityPricesProcurement:
    """Test that BalancingCapacityPrices parses the nested procurement object."""

    def test_procured_at_is_parsed(self):
        """procuredAt nested in procurement is parsed into a datetime."""
        result = make_prices({"procurement": {"procuredAt": "2024-12-31T23:00:00Z"}})

        assert isinstance(result.procurement.procured_at, datetime.datetime)
        assert result.procurement.procured_at.year == 2024
        assert result.procurement.procured_at.month == 12


class TestBalancingCapacityVolumesProcurement:
    """Test that BalancingCapacityVolumes parses the nested procurement object."""

    def test_procured_at_is_parsed(self):
        """procuredAt nested in procurement is parsed into a datetime."""
        result = make_volumes({"procurement": {"procuredAt": "2024-12-31T23:00:00Z"}})

        assert isinstance(result.procurement.procured_at, datetime.datetime)


# Helper functions

def make_prices(overrides: dict[str, Any] | None = None) -> BalancingCapacityPrices:
    """Create BalancingCapacityPrices with happy-path defaults."""
    if overrides is None:
        overrides = {}

    base_data = {
        "area": "DE",
        "eicCode": "10YDE-VE-------2",
        "reserveType": "FCR",
        "direction": "up",
        "currency": "EUR",
        "procurement": {"procuredAt": "2024-08-15T14:30:00Z"},
        "prices": [],
    }
    data = {**base_data, **overrides}
    return BalancingCapacityPrices.from_dict(data)


def make_volumes(overrides: dict[str, Any] | None = None) -> BalancingCapacityVolumes:
    """Create BalancingCapacityVolumes with happy-path defaults."""
    if overrides is None:
        overrides = {}

    base_data = {
        "area": "DE",
        "eicCode": "10YDE-VE-------2",
        "reserveType": "FCR",
        "direction": "up",
        "procurement": {"procuredAt": "2024-08-15T14:30:00Z"},
        "volumes": [],
    }
    data = {**base_data, **overrides}
    return BalancingCapacityVolumes.from_dict(data)
