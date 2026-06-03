"""
Tests over the *generated* client models, verifying the GH-3803 explicit-unit
fields are actually present after regeneration (``generate.sh``).

Unlike ``test_field_unit_aliases.py`` (which checks the OpenAPI source), these
exercise the checked-in generated code. If the client is not regenerated after
the spec changes, the new field lands in ``additional_properties`` instead of
becoming a typed attribute, and every case here fails — turning "forgot to run
generate.sh" into a red test rather than a silently stale published client.
"""

import attrs
import pytest

from balancing_services.models import (
    BalancingCapacityPrice,
    BalancingCapacityVolume,
    BalancingEnergyPrice,
    BalancingEnergyVolume,
    CapacityBid,
    CrossBorderMarginalPrice,
    DayAheadEnergyPrice,
    EnergyBid,
    ImbalancePrice,
    TotalImbalanceVolume,
)

PERIOD = {"startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-01T01:00:00Z"}

# Each pair is (deprecated_attr, deprecated_json, new_attr, new_json).
# Each case is (model, from_dict payload with both keys set to equal values, pairs).
MODEL_CASES = [
    (
        ImbalancePrice,
        {"period": PERIOD, "price": 45.5, "pricePerMwh": 45.5},
        [("price", "price", "price_per_mwh", "pricePerMwh")],
    ),
    (
        BalancingEnergyPrice,
        {"period": PERIOD, "price": 45.5, "pricePerMwh": 45.5},
        [("price", "price", "price_per_mwh", "pricePerMwh")],
    ),
    (
        DayAheadEnergyPrice,
        {"period": PERIOD, "price": 45.67, "pricePerMwh": 45.67},
        [("price", "price", "price_per_mwh", "pricePerMwh")],
    ),
    (
        CrossBorderMarginalPrice,
        {"period": PERIOD, "price": 45.5, "pricePerMwh": 45.5},
        [("price", "price", "price_per_mwh", "pricePerMwh")],
    ),
    (
        BalancingCapacityPrice,
        {"period": PERIOD, "price": 12.5, "pricePerMwPerHour": 12.5},
        [("price", "price", "price_per_mw_per_hour", "pricePerMwPerHour")],
    ),
    (
        BalancingEnergyVolume,
        {"period": PERIOD, "volume": 250.5, "volumeInMw": 250.5},
        [("volume", "volume", "volume_in_mw", "volumeInMw")],
    ),
    (
        BalancingCapacityVolume,
        {"period": PERIOD, "volume": 50.0, "volumeInMw": 50.0},
        [("volume", "volume", "volume_in_mw", "volumeInMw")],
    ),
    (
        EnergyBid,
        {"period": PERIOD, "volume": 100.0, "volumeInMw": 100.0, "price": 55.25, "pricePerMwh": 55.25},
        [
            ("volume", "volume", "volume_in_mw", "volumeInMw"),
            ("price", "price", "price_per_mwh", "pricePerMwh"),
        ],
    ),
    (
        CapacityBid,
        {
            "period": PERIOD,
            "capacity": 50.0,
            "capacityInMw": 50.0,
            "price": 12.5,
            "pricePerMwPerHour": 12.5,
            "status": "accepted",
        },
        [
            ("capacity", "capacity", "capacity_in_mw", "capacityInMw"),
            ("price", "price", "price_per_mw_per_hour", "pricePerMwPerHour"),
        ],
    ),
    (
        TotalImbalanceVolume,
        {"period": PERIOD, "averagePowerMW": 60.5, "averagePowerInMw": 60.5, "direction": "deficit"},
        [("average_power_mw", "averagePowerMW", "average_power_in_mw", "averagePowerInMw")],
    ),
]

CASE_IDS = [model.__name__ for model, _payload, _pairs in MODEL_CASES]


@pytest.mark.parametrize(("model", "payload", "pairs"), MODEL_CASES, ids=CASE_IDS)
def test_model_exposes_typed_alias_fields(model, payload, pairs):
    """Both the deprecated field and its replacement are typed, required attributes.

    Fails if the client was not regenerated from the updated spec (the new field
    would not exist as an attrs field).
    """
    fields = attrs.fields_dict(model)
    for deprecated_attr, _deprecated_json, new_attr, _new_json in pairs:
        assert new_attr in fields, (
            f"{model.__name__}.{new_attr} is missing — regenerate the client with generate.sh"
        )
        assert deprecated_attr in fields, f"{model.__name__}.{deprecated_attr} is missing"

        # Both required (no default) so neither silently disappears for consumers.
        assert fields[new_attr].default is attrs.NOTHING, f"{model.__name__}.{new_attr} must be required"
        assert fields[deprecated_attr].default is attrs.NOTHING, (
            f"{model.__name__}.{deprecated_attr} must be required"
        )


@pytest.mark.parametrize(("model", "payload", "pairs"), MODEL_CASES, ids=CASE_IDS)
def test_alias_fields_round_trip_in_sync(model, payload, pairs):
    """The explicit-unit field round-trips through the documented camelCase key
    and stays in sync with the deprecated field."""
    instance = model.from_dict(payload)
    dumped = instance.to_dict()

    for deprecated_attr, deprecated_json, new_attr, new_json in pairs:
        expected = payload[new_json]

        # Deserialized into a typed attribute, not swept into additional_properties.
        assert new_json not in instance.additional_properties, (
            f"{model.__name__}.{new_json} parsed into additional_properties — client is stale"
        )

        # Value carried onto both attributes and stays in sync.
        assert getattr(instance, new_attr) == expected
        assert getattr(instance, deprecated_attr) == getattr(instance, new_attr)

        # Re-serialized under both documented JSON keys with matching values.
        assert dumped[new_json] == expected
        assert dumped[deprecated_json] == dumped[new_json]
