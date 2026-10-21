from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.period import Period
    from ..models.price_per_mw_per_hour_quantile import PricePerMwPerHourQuantile


T = TypeVar("T", bound="BalancingCapacityPriceForecast")


@_attrs_define
class BalancingCapacityPriceForecast:
    """
    Attributes:
        period (Period):
        made_at (datetime.datetime): When this forecast was made (UTC), before the auction's gate closure. All forecasts
            of one auction share it across every page of one traversal — a first page and the pages reached through its
            cursors. Example: 2025-01-01T06:30:02Z.
        price_per_mw_per_hour (float): The point forecast of the price per MW per hour, in the group's currency — today
            the distribution's median, its price at level 0.5. Example: 12.5.
        quantiles (list[PricePerMwPerHourQuantile]): The predictive distribution of the price, as one level/price pair
            per quantile level, ascending by level. Each forecast states the grid it was made on — read the levels off it
            rather than indexing by a position you hardcoded.
    """

    period: Period
    made_at: datetime.datetime
    price_per_mw_per_hour: float
    quantiles: list[PricePerMwPerHourQuantile]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        made_at = self.made_at.isoformat()

        price_per_mw_per_hour = self.price_per_mw_per_hour

        quantiles = []
        for quantiles_item_data in self.quantiles:
            quantiles_item = quantiles_item_data.to_dict()
            quantiles.append(quantiles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "madeAt": made_at,
                "pricePerMwPerHour": price_per_mw_per_hour,
                "quantiles": quantiles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.period import Period
        from ..models.price_per_mw_per_hour_quantile import PricePerMwPerHourQuantile

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        made_at = datetime.datetime.fromisoformat(d.pop("madeAt").replace("Z", "+00:00"))

        price_per_mw_per_hour = d.pop("pricePerMwPerHour")

        quantiles = []
        _quantiles = d.pop("quantiles")
        for quantiles_item_data in _quantiles:
            quantiles_item = PricePerMwPerHourQuantile.from_dict(quantiles_item_data)

            quantiles.append(quantiles_item)

        balancing_capacity_price_forecast = cls(
            period=period,
            made_at=made_at,
            price_per_mw_per_hour=price_per_mw_per_hour,
            quantiles=quantiles,
        )

        balancing_capacity_price_forecast.additional_properties = d
        return balancing_capacity_price_forecast

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
