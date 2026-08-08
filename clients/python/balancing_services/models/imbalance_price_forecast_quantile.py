from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ImbalancePriceForecastQuantile")


@_attrs_define
class ImbalancePriceForecastQuantile:
    """
    Attributes:
        level (float): The quantile level, as a decimal strictly between 0 and 1 — 0.5 being the median, and the pair
            0.1/0.9 bounding the central 80% interval. Example: 0.5.
        price_per_mwh (float): Forecast price per MWh at this level, in the group's currency Example: 45.5.
    """

    level: float
    price_per_mwh: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        level = self.level

        price_per_mwh = self.price_per_mwh

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "level": level,
                "pricePerMwh": price_per_mwh,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        level = d.pop("level")

        price_per_mwh = d.pop("pricePerMwh")

        imbalance_price_forecast_quantile = cls(
            level=level,
            price_per_mwh=price_per_mwh,
        )

        imbalance_price_forecast_quantile.additional_properties = d
        return imbalance_price_forecast_quantile

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
