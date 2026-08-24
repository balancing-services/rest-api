from typing import Literal, cast

BidAvailability = Literal["available", "cancelled", "unavailable", "withdrawn"]

BID_AVAILABILITY_VALUES: set[BidAvailability] = {
    "available",
    "cancelled",
    "unavailable",
    "withdrawn",
}


def check_bid_availability(value: str) -> BidAvailability:
    if value in BID_AVAILABILITY_VALUES:
        return cast(BidAvailability, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {BID_AVAILABILITY_VALUES!r}"
    )
