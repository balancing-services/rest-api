from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.imbalance_price_forecast_quantile import (
        ImbalancePriceForecastQuantile,
    )
    from ..models.period import Period


T = TypeVar("T", bound="ImbalancePriceForecast")


@_attrs_define
class ImbalancePriceForecast:
    """
    Attributes:
        period (Period):
        quantiles (list[ImbalancePriceForecastQuantile]): The predictive distribution of the price, as one level/price
            pair per quantile level, ascending by level. Each forecast states the grid it was made on — read the levels off
            it rather than indexing by a position you hardcoded.
        made_at (datetime.datetime): When this forecast was made (UTC). Example: 2025-01-01T00:05:00Z.
        degraded (bool): True when the forecast was computed from incomplete or stale inputs. It is still served, but is
            less trustworthy — use with care.
    """

    period: Period
    quantiles: list[ImbalancePriceForecastQuantile]
    made_at: datetime.datetime
    degraded: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        quantiles = []
        for quantiles_item_data in self.quantiles:
            quantiles_item = quantiles_item_data.to_dict()
            quantiles.append(quantiles_item)

        made_at = self.made_at.isoformat()

        degraded = self.degraded

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "quantiles": quantiles,
                "madeAt": made_at,
                "degraded": degraded,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.imbalance_price_forecast_quantile import (
            ImbalancePriceForecastQuantile,
        )
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        quantiles = []
        _quantiles = d.pop("quantiles")
        for quantiles_item_data in _quantiles:
            quantiles_item = ImbalancePriceForecastQuantile.from_dict(
                quantiles_item_data
            )

            quantiles.append(quantiles_item)

        made_at = datetime.datetime.fromisoformat(d.pop("madeAt").replace("Z", "+00:00"))

        degraded = d.pop("degraded")

        imbalance_price_forecast = cls(
            period=period,
            quantiles=quantiles,
            made_at=made_at,
            degraded=degraded,
        )

        imbalance_price_forecast.additional_properties = d
        return imbalance_price_forecast

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
