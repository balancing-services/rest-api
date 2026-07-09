from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field


from ..models.area import Area
from ..models.demand_basis import DemandBasis
from ..models.direction import Direction
from ..models.eic_code import EicCode
from ..models.reserve_type import ReserveType
import datetime

if TYPE_CHECKING:
    from ..models.balancing_capacity_demand import BalancingCapacityDemand


T = TypeVar("T", bound="BalancingCapacityDemands")


@_attrs_define
class BalancingCapacityDemands:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        reserve_type (ReserveType): Reserve type
        direction (Direction): Balancing direction
        procured_at (datetime.datetime): Timestamp when the capacity was procured (allocation time or gate closure
            time).
            Used to distinguish different procurements (e.g., yearly vs hourly, or multiple procurement rounds).
             Example: 2024-08-15T14:30:00Z.
        demand_basis (DemandBasis): Whether the demand adds to the delivery period's total requirement (`additive`) or
            restates demand
            already represented by another procurement of the same period (`substitutive`), e.g. a re-run after
            a failed auction. When summing a period's total requirement across procurements, sum additive demand only.
        demands (list[BalancingCapacityDemand]):
    """

    area: Area
    eic_code: EicCode
    reserve_type: ReserveType
    direction: Direction
    procured_at: datetime.datetime
    demand_basis: DemandBasis
    demands: list[BalancingCapacityDemand]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area = self.area.value

        eic_code = self.eic_code.value

        reserve_type = self.reserve_type.value

        direction = self.direction.value

        procured_at = self.procured_at.isoformat()

        demand_basis = self.demand_basis.value

        demands = []
        for demands_item_data in self.demands:
            demands_item = demands_item_data.to_dict()
            demands.append(demands_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "area": area,
                "eicCode": eic_code,
                "reserveType": reserve_type,
                "direction": direction,
                "procuredAt": procured_at,
                "demandBasis": demand_basis,
                "demands": demands,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.balancing_capacity_demand import BalancingCapacityDemand

        d = dict(src_dict)
        area = Area(d.pop("area"))

        eic_code = EicCode(d.pop("eicCode"))

        reserve_type = ReserveType(d.pop("reserveType"))

        direction = Direction(d.pop("direction"))

        procured_at = datetime.datetime.fromisoformat(d.pop("procuredAt").replace("Z", "+00:00"))

        demand_basis = DemandBasis(d.pop("demandBasis"))

        demands = []
        _demands = d.pop("demands")
        for demands_item_data in _demands:
            demands_item = BalancingCapacityDemand.from_dict(demands_item_data)

            demands.append(demands_item)

        balancing_capacity_demands = cls(
            area=area,
            eic_code=eic_code,
            reserve_type=reserve_type,
            direction=direction,
            procured_at=procured_at,
            demand_basis=demand_basis,
            demands=demands,
        )

        balancing_capacity_demands.additional_properties = d
        return balancing_capacity_demands

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
