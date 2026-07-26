from typing import Literal, cast

ReserveType = Literal["aFRR", "FCR", "mFRR", "RR"]

RESERVE_TYPE_VALUES: set[ReserveType] = {
    "aFRR",
    "FCR",
    "mFRR",
    "RR",
}


def check_reserve_type(value: str) -> ReserveType:
    if value in RESERVE_TYPE_VALUES:
        return cast(ReserveType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {RESERVE_TYPE_VALUES!r}"
    )
