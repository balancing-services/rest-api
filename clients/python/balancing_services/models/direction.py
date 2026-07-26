from typing import Literal, cast

Direction = Literal["down", "symmetric", "up"]

DIRECTION_VALUES: set[Direction] = {
    "down",
    "symmetric",
    "up",
}


def check_direction(value: str) -> Direction:
    if value in DIRECTION_VALUES:
        return cast(Direction, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DIRECTION_VALUES!r}")
