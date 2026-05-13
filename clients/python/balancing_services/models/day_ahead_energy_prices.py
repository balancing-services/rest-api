from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.area import Area
from ..models.currency import Currency
from ..models.eic_code import EicCode

if TYPE_CHECKING:
    from ..models.day_ahead_energy_price import DayAheadEnergyPrice


T = TypeVar("T", bound="DayAheadEnergyPrices")


@_attrs_define
class DayAheadEnergyPrices:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        currency (Currency): Currency code
        prices (list[DayAheadEnergyPrice]):
    """

    area: Area
    eic_code: EicCode
    currency: Currency
    prices: list[DayAheadEnergyPrice]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area = self.area.value

        eic_code = self.eic_code.value

        currency = self.currency.value

        prices = []
        for prices_item_data in self.prices:
            prices_item = prices_item_data.to_dict()
            prices.append(prices_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "area": area,
                "eicCode": eic_code,
                "currency": currency,
                "prices": prices,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.day_ahead_energy_price import DayAheadEnergyPrice

        d = dict(src_dict)
        area = Area(d.pop("area"))

        eic_code = EicCode(d.pop("eicCode"))

        currency = Currency(d.pop("currency"))

        prices = []
        _prices = d.pop("prices")
        for prices_item_data in _prices:
            prices_item = DayAheadEnergyPrice.from_dict(prices_item_data)

            prices.append(prices_item)

        day_ahead_energy_prices = cls(
            area=area,
            eic_code=eic_code,
            currency=currency,
            prices=prices,
        )

        day_ahead_energy_prices.additional_properties = d
        return day_ahead_energy_prices

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
