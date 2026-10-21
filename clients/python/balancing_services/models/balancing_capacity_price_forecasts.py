from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.area import Area, check_area
from ..models.currency import Currency, check_currency
from ..models.direction import Direction, check_direction
from ..models.eic_code import EicCode, check_eic_code
from ..models.reserve_type import ReserveType, check_reserve_type

if TYPE_CHECKING:
    from ..models.balancing_capacity_price_forecast import (
        BalancingCapacityPriceForecast,
    )
    from ..models.procurement import Procurement


T = TypeVar("T", bound="BalancingCapacityPriceForecasts")


@_attrs_define
class BalancingCapacityPriceForecasts:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        reserve_type (ReserveType): Reserve type
        direction (Direction): Balancing direction
        currency (Currency): Currency code
        procurement (Procurement):
        forecasts (list[BalancingCapacityPriceForecast]):
    """

    area: Area
    eic_code: EicCode
    reserve_type: ReserveType
    direction: Direction
    currency: Currency
    procurement: Procurement
    forecasts: list[BalancingCapacityPriceForecast]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area: str = self.area

        eic_code: str = self.eic_code

        reserve_type: str = self.reserve_type

        direction: str = self.direction

        currency: str = self.currency

        procurement = self.procurement.to_dict()

        forecasts = []
        for forecasts_item_data in self.forecasts:
            forecasts_item = forecasts_item_data.to_dict()
            forecasts.append(forecasts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "area": area,
                "eicCode": eic_code,
                "reserveType": reserve_type,
                "direction": direction,
                "currency": currency,
                "procurement": procurement,
                "forecasts": forecasts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.balancing_capacity_price_forecast import (
            BalancingCapacityPriceForecast,
        )
        from ..models.procurement import Procurement

        d = dict(src_dict)
        area = check_area(d.pop("area"))

        eic_code = check_eic_code(d.pop("eicCode"))

        reserve_type = check_reserve_type(d.pop("reserveType"))

        direction = check_direction(d.pop("direction"))

        currency = check_currency(d.pop("currency"))

        procurement = Procurement.from_dict(d.pop("procurement"))

        forecasts = []
        _forecasts = d.pop("forecasts")
        for forecasts_item_data in _forecasts:
            forecasts_item = BalancingCapacityPriceForecast.from_dict(
                forecasts_item_data
            )

            forecasts.append(forecasts_item)

        balancing_capacity_price_forecasts = cls(
            area=area,
            eic_code=eic_code,
            reserve_type=reserve_type,
            direction=direction,
            currency=currency,
            procurement=procurement,
            forecasts=forecasts,
        )

        balancing_capacity_price_forecasts.additional_properties = d
        return balancing_capacity_price_forecasts

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
