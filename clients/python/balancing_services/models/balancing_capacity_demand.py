from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field


if TYPE_CHECKING:
    from ..models.period import Period


T = TypeVar("T", bound="BalancingCapacityDemand")


@_attrs_define
class BalancingCapacityDemand:
    """
    Attributes:
        period (Period):
        total_demand_in_mw (float): The full capacity requirement in MW Example: 300.0.
        local_demand_in_mw (float): The part of the requirement in MW that must be procured within the area itself;
            total minus local may be covered from other areas Example: 120.0.
    """

    period: Period
    total_demand_in_mw: float
    local_demand_in_mw: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        total_demand_in_mw = self.total_demand_in_mw

        local_demand_in_mw = self.local_demand_in_mw

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "totalDemandInMw": total_demand_in_mw,
                "localDemandInMw": local_demand_in_mw,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        total_demand_in_mw = d.pop("totalDemandInMw")

        local_demand_in_mw = d.pop("localDemandInMw")

        balancing_capacity_demand = cls(
            period=period,
            total_demand_in_mw=total_demand_in_mw,
            local_demand_in_mw=local_demand_in_mw,
        )

        balancing_capacity_demand.additional_properties = d
        return balancing_capacity_demand

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
