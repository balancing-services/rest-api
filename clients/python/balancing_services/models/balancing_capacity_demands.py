from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.area import Area, check_area
from ..models.demand_basis import DemandBasis, check_demand_basis
from ..models.direction import Direction, check_direction
from ..models.eic_code import EicCode, check_eic_code
from ..models.reserve_type import ReserveType, check_reserve_type

if TYPE_CHECKING:
    from ..models.balancing_capacity_demand import BalancingCapacityDemand
    from ..models.procurement import Procurement


T = TypeVar("T", bound="BalancingCapacityDemands")


@_attrs_define
class BalancingCapacityDemands:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        reserve_type (ReserveType): Reserve type
        direction (Direction): Balancing direction
        procurement (Procurement):
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
    procurement: Procurement
    demand_basis: DemandBasis
    demands: list[BalancingCapacityDemand]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area: str = self.area

        eic_code: str = self.eic_code

        reserve_type: str = self.reserve_type

        direction: str = self.direction

        procurement = self.procurement.to_dict()

        demand_basis: str = self.demand_basis

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
                "procurement": procurement,
                "demandBasis": demand_basis,
                "demands": demands,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.balancing_capacity_demand import BalancingCapacityDemand
        from ..models.procurement import Procurement

        d = dict(src_dict)
        area = check_area(d.pop("area"))

        eic_code = check_eic_code(d.pop("eicCode"))

        reserve_type = check_reserve_type(d.pop("reserveType"))

        direction = check_direction(d.pop("direction"))

        procurement = Procurement.from_dict(d.pop("procurement"))

        demand_basis = check_demand_basis(d.pop("demandBasis"))

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
            procurement=procurement,
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
