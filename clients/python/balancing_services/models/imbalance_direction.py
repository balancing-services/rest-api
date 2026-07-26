from typing import Literal, cast

ImbalanceDirection = Literal["negative", "positive", "symmetric"]

IMBALANCE_DIRECTION_VALUES: set[ImbalanceDirection] = {
    "negative",
    "positive",
    "symmetric",
}


def check_imbalance_direction(value: str) -> ImbalanceDirection:
    if value in IMBALANCE_DIRECTION_VALUES:
        return cast(ImbalanceDirection, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {IMBALANCE_DIRECTION_VALUES!r}"
    )
