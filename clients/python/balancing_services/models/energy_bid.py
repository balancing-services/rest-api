from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.period import Period


T = TypeVar("T", bound="EnergyBid")


@_attrs_define
class EnergyBid:
    """
    Attributes:
        period (Period):
        volume (float): Deprecated — use `volumeInMw` instead. Bid volume in MW Example: 100.
        volume_in_mw (float): Bid volume in MW Example: 100.
        price (float): Deprecated — use `pricePerMwh` instead. Bid price per MWh in the specified currency Example:
            55.25.
        price_per_mwh (float): Bid price per MWh in the specified currency Example: 55.25.
    """

    period: Period
    volume: float
    volume_in_mw: float
    price: float
    price_per_mwh: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        volume = self.volume

        volume_in_mw = self.volume_in_mw

        price = self.price

        price_per_mwh = self.price_per_mwh

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "volume": volume,
                "volumeInMw": volume_in_mw,
                "price": price,
                "pricePerMwh": price_per_mwh,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        volume = d.pop("volume")

        volume_in_mw = d.pop("volumeInMw")

        price = d.pop("price")

        price_per_mwh = d.pop("pricePerMwh")

        energy_bid = cls(
            period=period,
            volume=volume,
            volume_in_mw=volume_in_mw,
            price=price,
            price_per_mwh=price_per_mwh,
        )

        energy_bid.additional_properties = d
        return energy_bid

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
