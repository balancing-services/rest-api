from typing import Literal, cast

Currency = Literal["BGN", "CHF", "EUR", "HUF", "PLN", "RON", "UAH"]

CURRENCY_VALUES: set[Currency] = {
    "BGN",
    "CHF",
    "EUR",
    "HUF",
    "PLN",
    "RON",
    "UAH",
}


def check_currency(value: str) -> Currency:
    if value in CURRENCY_VALUES:
        return cast(Currency, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CURRENCY_VALUES!r}")
