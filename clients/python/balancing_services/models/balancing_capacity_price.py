from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.price_type import PriceType, check_price_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.period import Period


T = TypeVar("T", bound="BalancingCapacityPrice")


@_attrs_define
class BalancingCapacityPrice:
    """
    Attributes:
        period (Period):
        price_per_mw_per_hour (float): Price per MW per hour in the specified currency Example: 12.5.
        price_type (PriceType | Unset): Average or marginal price
    """

    period: Period
    price_per_mw_per_hour: float
    price_type: PriceType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        price_per_mw_per_hour = self.price_per_mw_per_hour

        price_type: str | Unset = UNSET
        if not isinstance(self.price_type, Unset):
            price_type = self.price_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "pricePerMwPerHour": price_per_mw_per_hour,
            }
        )
        if price_type is not UNSET:
            field_dict["priceType"] = price_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        price_per_mw_per_hour = d.pop("pricePerMwPerHour")

        _price_type = d.pop("priceType", UNSET)
        price_type: PriceType | Unset
        if isinstance(_price_type, Unset):
            price_type = UNSET
        else:
            price_type = check_price_type(_price_type)

        balancing_capacity_price = cls(
            period=period,
            price_per_mw_per_hour=price_per_mw_per_hour,
            price_type=price_type,
        )

        balancing_capacity_price.additional_properties = d
        return balancing_capacity_price

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
