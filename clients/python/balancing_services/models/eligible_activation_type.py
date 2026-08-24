from typing import Literal, cast

EligibleActivationType = Literal["direct", "scheduled"]

ELIGIBLE_ACTIVATION_TYPE_VALUES: set[EligibleActivationType] = {
    "direct",
    "scheduled",
}


def check_eligible_activation_type(value: str) -> EligibleActivationType:
    if value in ELIGIBLE_ACTIVATION_TYPE_VALUES:
        return cast(EligibleActivationType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {ELIGIBLE_ACTIVATION_TYPE_VALUES!r}"
    )
