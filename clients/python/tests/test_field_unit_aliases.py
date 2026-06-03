"""
Contract tests keeping the deprecated unit-less fields and their explicit-unit
replacements in sync in the OpenAPI specification (GH-3803).

Every ambiguous field (``volume``, ``price``, ``capacity``, ``averagePowerMW``)
is kept for backwards compatibility but marked deprecated, and a new field that
carries the unit in its name (``volumeInMw``, ``pricePerMwh`` …) is added with
the *same* value. These tests fail if the pair ever drifts apart — a differing
type/example, one of them missing or no longer required, the deprecation flag
dropped — or if a new deprecated field is introduced without registering its
explicit-unit sibling here.
"""

from pathlib import Path

import pytest
import yaml

# clients/python/tests/<this file>  ->  parents[3] is the repository root.
OPENAPI_PATH = Path(__file__).resolve().parents[3] / "openapi.yaml"

# schema name -> {deprecated field: explicit-unit replacement}
ALIASED_FIELDS: dict[str, dict[str, str]] = {
    "ImbalancePrice": {"price": "pricePerMwh"},
    "TotalImbalanceVolume": {"averagePowerMW": "averagePowerInMw"},
    "BalancingEnergyVolume": {"volume": "volumeInMw"},
    "BalancingEnergyPrice": {"price": "pricePerMwh"},
    "DayAheadEnergyPrice": {"price": "pricePerMwh"},
    "EnergyBid": {"volume": "volumeInMw", "price": "pricePerMwh"},
    "CapacityBid": {"capacity": "capacityInMw", "price": "pricePerMwPerHour"},
    "BalancingCapacityPrice": {"price": "pricePerMwPerHour"},
    "BalancingCapacityVolume": {"volume": "volumeInMw"},
    "CrossBorderMarginalPrice": {"price": "pricePerMwh"},
}

# Schema keys describing the value itself; the alias must agree on each so the
# two fields stay interchangeable.
SYNCED_KEYS = ("type", "format", "example")


@pytest.fixture(scope="module")
def schemas() -> dict:
    """All component schemas from the canonical OpenAPI spec."""
    spec = yaml.safe_load(OPENAPI_PATH.read_text())
    return spec["components"]["schemas"]


def _alias_pairs():
    for schema, mapping in ALIASED_FIELDS.items():
        for deprecated, replacement in mapping.items():
            yield pytest.param(
                schema,
                deprecated,
                replacement,
                id=f"{schema}.{deprecated}->{replacement}",
            )


@pytest.mark.parametrize(("schema", "deprecated", "replacement"), list(_alias_pairs()))
def test_alias_in_sync(schemas, schema, deprecated, replacement):
    """The deprecated field and its explicit-unit replacement agree on everything."""
    properties = schemas[schema]["properties"]
    required = schemas[schema].get("required", [])

    assert deprecated in properties, f"{schema}.{deprecated} is missing"
    assert replacement in properties, f"{schema}.{replacement} is missing"

    old = properties[deprecated]
    new = properties[replacement]

    # Only the old field is deprecated.
    assert old.get("deprecated") is True, f"{schema}.{deprecated} must be deprecated"
    assert new.get("deprecated") is not True, f"{schema}.{replacement} must not be deprecated"

    # Both are always present, so a consumer can switch fields freely.
    assert deprecated in required, f"{schema}.{deprecated} must stay required"
    assert replacement in required, f"{schema}.{replacement} must be required"

    # Same value shape -> the two fields carry the same value.
    for key in SYNCED_KEYS:
        assert old.get(key) == new.get(key), (
            f"{schema}: {deprecated}.{key}={old.get(key)!r} "
            f"differs from {replacement}.{key}={new.get(key)!r}"
        )

    # The deprecated field points consumers at its replacement.
    assert replacement in old.get("description", ""), (
        f"{schema}.{deprecated} description should reference {replacement}"
    )


def test_no_unregistered_deprecated_fields(schemas):
    """Every deprecated property must have a registered, in-sync replacement.

    Guards against a future ambiguous field being deprecated without adding the
    explicit-unit sibling (and a matching entry in ``ALIASED_FIELDS``).
    """
    registered = {
        (schema, field)
        for schema, mapping in ALIASED_FIELDS.items()
        for field in mapping
    }
    found = {
        (schema_name, field_name)
        for schema_name, schema in schemas.items()
        for field_name, field in schema.get("properties", {}).items()
        if isinstance(field, dict) and field.get("deprecated") is True
    }

    assert found == registered, (
        "Deprecated fields in openapi.yaml do not match the registered aliases.\n"
        f"  unregistered (deprecated but no alias test): {sorted(found - registered)}\n"
        f"  stale (registered but no longer deprecated):  {sorted(registered - found)}"
    )
