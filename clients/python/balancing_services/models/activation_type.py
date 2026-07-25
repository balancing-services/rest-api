from typing import Literal

ActivationType = Literal["direct", "notApplicable", "scheduled", "unspecified"]

ACTIVATION_TYPE_VALUES: set[ActivationType] = {
    "direct",
    "notApplicable",
    "scheduled",
    "unspecified",
}


def check_activation_type(value: str) -> ActivationType:
    if value in ACTIVATION_TYPE_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {ACTIVATION_TYPE_VALUES!r}"
    )
