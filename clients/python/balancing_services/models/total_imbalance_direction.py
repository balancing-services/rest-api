from typing import Literal

TotalImbalanceDirection = Literal["balanced", "deficit", "surplus"]

TOTAL_IMBALANCE_DIRECTION_VALUES: set[TotalImbalanceDirection] = {
    "balanced",
    "deficit",
    "surplus",
}


def check_total_imbalance_direction(value: str) -> TotalImbalanceDirection:
    if value in TOTAL_IMBALANCE_DIRECTION_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {TOTAL_IMBALANCE_DIRECTION_VALUES!r}"
    )
