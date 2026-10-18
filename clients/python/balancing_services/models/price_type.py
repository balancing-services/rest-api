from typing import Literal, cast

PriceType = Literal["average", "marginal"]

PRICE_TYPE_VALUES: set[PriceType] = {
    "average",
    "marginal",
}


def check_price_type(value: str) -> PriceType:
    if value in PRICE_TYPE_VALUES:
        return cast(PriceType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {PRICE_TYPE_VALUES!r}"
    )
