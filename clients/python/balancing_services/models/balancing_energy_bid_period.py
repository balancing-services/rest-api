from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.energy_bid import EnergyBid
    from ..models.period import Period


T = TypeVar("T", bound="BalancingEnergyBidPeriod")


@_attrs_define
class BalancingEnergyBidPeriod:
    """
    Attributes:
        period (Period):
        bids (list[EnergyBid]): The bids for this delivery period. No ordering is guaranteed — sort by price client-side
            if you need the merit order.
    """

    period: Period
    bids: list[EnergyBid]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        bids = []
        for bids_item_data in self.bids:
            bids_item = bids_item_data.to_dict()
            bids.append(bids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "bids": bids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.energy_bid import EnergyBid
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        bids = []
        _bids = d.pop("bids")
        for bids_item_data in _bids:
            bids_item = EnergyBid.from_dict(bids_item_data)

            bids.append(bids_item)

        balancing_energy_bid_period = cls(
            period=period,
            bids=bids,
        )

        balancing_energy_bid_period.additional_properties = d
        return balancing_energy_bid_period

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
