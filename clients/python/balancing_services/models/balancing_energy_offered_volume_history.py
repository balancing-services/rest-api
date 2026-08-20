from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.activation_type import ActivationType, check_activation_type
from ..models.area import Area, check_area
from ..models.direction import Direction, check_direction
from ..models.eic_code import EicCode, check_eic_code
from ..models.reserve_type import ReserveType, check_reserve_type

if TYPE_CHECKING:
    from ..models.balancing_energy_offered_volume_revision import (
        BalancingEnergyOfferedVolumeRevision,
    )


T = TypeVar("T", bound="BalancingEnergyOfferedVolumeHistory")


@_attrs_define
class BalancingEnergyOfferedVolumeHistory:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        reserve_type (ReserveType): Reserve type
        direction (Direction): Balancing direction
        activation_type (ActivationType): Activation type of the balancing energy. Only mFRR distinguishes activation
            types:
            - direct: mFRR activated directly
            - scheduled: mFRR activated on a schedule
            - unspecified: mFRR without a direct/scheduled breakdown — the source does not publish one, or the product does
            not define one
            - notApplicable: the reserve type has no activation-type concept (FCR, aFRR, RR)
        standard_product (bool): Indicates if this is a European standard balancing product Example: True.
        volumes (list[BalancingEnergyOfferedVolumeRevision]):
    """

    area: Area
    eic_code: EicCode
    reserve_type: ReserveType
    direction: Direction
    activation_type: ActivationType
    standard_product: bool
    volumes: list[BalancingEnergyOfferedVolumeRevision]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area: str = self.area

        eic_code: str = self.eic_code

        reserve_type: str = self.reserve_type

        direction: str = self.direction

        activation_type: str = self.activation_type

        standard_product = self.standard_product

        volumes = []
        for volumes_item_data in self.volumes:
            volumes_item = volumes_item_data.to_dict()
            volumes.append(volumes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "area": area,
                "eicCode": eic_code,
                "reserveType": reserve_type,
                "direction": direction,
                "activationType": activation_type,
                "standardProduct": standard_product,
                "volumes": volumes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.balancing_energy_offered_volume_revision import (
            BalancingEnergyOfferedVolumeRevision,
        )

        d = dict(src_dict)
        area = check_area(d.pop("area"))

        eic_code = check_eic_code(d.pop("eicCode"))

        reserve_type = check_reserve_type(d.pop("reserveType"))

        direction = check_direction(d.pop("direction"))

        activation_type = check_activation_type(d.pop("activationType"))

        standard_product = d.pop("standardProduct")

        volumes = []
        _volumes = d.pop("volumes")
        for volumes_item_data in _volumes:
            volumes_item = BalancingEnergyOfferedVolumeRevision.from_dict(
                volumes_item_data
            )

            volumes.append(volumes_item)

        balancing_energy_offered_volume_history = cls(
            area=area,
            eic_code=eic_code,
            reserve_type=reserve_type,
            direction=direction,
            activation_type=activation_type,
            standard_product=standard_product,
            volumes=volumes,
        )

        balancing_energy_offered_volume_history.additional_properties = d
        return balancing_energy_offered_volume_history

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
