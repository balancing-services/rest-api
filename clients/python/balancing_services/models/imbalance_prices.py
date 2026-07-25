from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.area import Area, check_area
from ..models.currency import Currency, check_currency
from ..models.eic_code import EicCode, check_eic_code
from ..models.imbalance_direction import ImbalanceDirection, check_imbalance_direction

if TYPE_CHECKING:
    from ..models.imbalance_price import ImbalancePrice


T = TypeVar("T", bound="ImbalancePrices")


@_attrs_define
class ImbalancePrices:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        currency (Currency): Currency code
        direction (ImbalanceDirection): Imbalance direction
        prices (list[ImbalancePrice]):
    """

    area: Area
    eic_code: EicCode
    currency: Currency
    direction: ImbalanceDirection
    prices: list[ImbalancePrice]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area: str = self.area

        eic_code: str = self.eic_code

        currency: str = self.currency

        direction: str = self.direction

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
                "direction": direction,
                "prices": prices,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.imbalance_price import ImbalancePrice

        d = dict(src_dict)
        area = check_area(d.pop("area"))

        eic_code = check_eic_code(d.pop("eicCode"))

        currency = check_currency(d.pop("currency"))

        direction = check_imbalance_direction(d.pop("direction"))

        prices = []
        _prices = d.pop("prices")
        for prices_item_data in _prices:
            prices_item = ImbalancePrice.from_dict(prices_item_data)

            prices.append(prices_item)

        imbalance_prices = cls(
            area=area,
            eic_code=eic_code,
            currency=currency,
            direction=direction,
            prices=prices,
        )

        imbalance_prices.additional_properties = d
        return imbalance_prices

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
