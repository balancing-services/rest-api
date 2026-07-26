from typing import Literal, cast

BidStatus = Literal["accepted", "offered"]

BID_STATUS_VALUES: set[BidStatus] = {
    "accepted",
    "offered",
}


def check_bid_status(value: str) -> BidStatus:
    if value in BID_STATUS_VALUES:
        return cast(BidStatus, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {BID_STATUS_VALUES!r}"
    )
