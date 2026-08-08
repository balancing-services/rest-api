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
    from ..models.imbalance_price_forecast import ImbalancePriceForecast


T = TypeVar("T", bound="ImbalancePriceForecasts")


@_attrs_define
class ImbalancePriceForecasts:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        currency (Currency): Currency code
        direction (ImbalanceDirection): Imbalance direction
        forecasts (list[ImbalancePriceForecast]):
    """

    area: Area
    eic_code: EicCode
    currency: Currency
    direction: ImbalanceDirection
    forecasts: list[ImbalancePriceForecast]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area: str = self.area

        eic_code: str = self.eic_code

        currency: str = self.currency

        direction: str = self.direction

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
                "currency": currency,
                "direction": direction,
                "forecasts": forecasts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.imbalance_price_forecast import ImbalancePriceForecast

        d = dict(src_dict)
        area = check_area(d.pop("area"))

        eic_code = check_eic_code(d.pop("eicCode"))

        currency = check_currency(d.pop("currency"))

        direction = check_imbalance_direction(d.pop("direction"))

        forecasts = []
        _forecasts = d.pop("forecasts")
        for forecasts_item_data in _forecasts:
            forecasts_item = ImbalancePriceForecast.from_dict(forecasts_item_data)

            forecasts.append(forecasts_item)

        imbalance_price_forecasts = cls(
            area=area,
            eic_code=eic_code,
            currency=currency,
            direction=direction,
            forecasts=forecasts,
        )

        imbalance_price_forecasts.additional_properties = d
        return imbalance_price_forecasts

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
