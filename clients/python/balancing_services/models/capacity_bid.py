from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.bid_status import BidStatus, check_bid_status

if TYPE_CHECKING:
    from ..models.procurement import Procurement


T = TypeVar("T", bound="CapacityBid")


@_attrs_define
class CapacityBid:
    """
    Attributes:
        capacity_in_mw (float): Bid capacity in MW Example: 50.
        price_per_mw_per_hour (float): Bid price per MW per hour in the specified currency Example: 12.5.
        status (BidStatus): Status of a capacity bid:
            - offered: Bid was offered but not accepted
            - accepted: Bid was accepted (at least partially accepted)
        procurement (Procurement):
    """

    capacity_in_mw: float
    price_per_mw_per_hour: float
    status: BidStatus
    procurement: Procurement
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capacity_in_mw = self.capacity_in_mw

        price_per_mw_per_hour = self.price_per_mw_per_hour

        status: str = self.status

        procurement = self.procurement.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "capacityInMw": capacity_in_mw,
                "pricePerMwPerHour": price_per_mw_per_hour,
                "status": status,
                "procurement": procurement,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.procurement import Procurement

        d = dict(src_dict)
        capacity_in_mw = d.pop("capacityInMw")

        price_per_mw_per_hour = d.pop("pricePerMwPerHour")

        status = check_bid_status(d.pop("status"))

        procurement = Procurement.from_dict(d.pop("procurement"))

        capacity_bid = cls(
            capacity_in_mw=capacity_in_mw,
            price_per_mw_per_hour=price_per_mw_per_hour,
            status=status,
            procurement=procurement,
        )

        capacity_bid.additional_properties = d
        return capacity_bid

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
