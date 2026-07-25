from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.activation_type import ActivationType, check_activation_type
from ..models.area import Area, check_area
from ..models.eic_code import EicCode, check_eic_code
from ..models.reserve_type import ReserveType, check_reserve_type

if TYPE_CHECKING:
    from ..models.balancing_energy_volume import BalancingEnergyVolume


T = TypeVar("T", bound="CrossBorderEnergyVolumes")


@_attrs_define
class CrossBorderEnergyVolumes:
    """
    Attributes:
        from_area (Area): Area code
        from_eic_code (EicCode): Energy Identification Code (EIC)
        to_area (Area): Area code
        to_eic_code (EicCode): Energy Identification Code (EIC)
        reserve_type (ReserveType): Reserve type
        activation_type (ActivationType): Activation type of the balancing energy. Only mFRR distinguishes activation
            types:
            - direct: mFRR activated directly
            - scheduled: mFRR activated on a schedule
            - unspecified: mFRR without a direct/scheduled breakdown — the source does not publish one, or the product does
            not define one
            - notApplicable: the reserve type has no activation-type concept (FCR, aFRR, RR)
        volumes (list[BalancingEnergyVolume]):
    """

    from_area: Area
    from_eic_code: EicCode
    to_area: Area
    to_eic_code: EicCode
    reserve_type: ReserveType
    activation_type: ActivationType
    volumes: list[BalancingEnergyVolume]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from_area: str = self.from_area

        from_eic_code: str = self.from_eic_code

        to_area: str = self.to_area

        to_eic_code: str = self.to_eic_code

        reserve_type: str = self.reserve_type

        activation_type: str = self.activation_type

        volumes = []
        for volumes_item_data in self.volumes:
            volumes_item = volumes_item_data.to_dict()
            volumes.append(volumes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fromArea": from_area,
                "fromEicCode": from_eic_code,
                "toArea": to_area,
                "toEicCode": to_eic_code,
                "reserveType": reserve_type,
                "activationType": activation_type,
                "volumes": volumes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.balancing_energy_volume import BalancingEnergyVolume

        d = dict(src_dict)
        from_area = check_area(d.pop("fromArea"))

        from_eic_code = check_eic_code(d.pop("fromEicCode"))

        to_area = check_area(d.pop("toArea"))

        to_eic_code = check_eic_code(d.pop("toEicCode"))

        reserve_type = check_reserve_type(d.pop("reserveType"))

        activation_type = check_activation_type(d.pop("activationType"))

        volumes = []
        _volumes = d.pop("volumes")
        for volumes_item_data in _volumes:
            volumes_item = BalancingEnergyVolume.from_dict(volumes_item_data)

            volumes.append(volumes_item)

        cross_border_energy_volumes = cls(
            from_area=from_area,
            from_eic_code=from_eic_code,
            to_area=to_area,
            to_eic_code=to_eic_code,
            reserve_type=reserve_type,
            activation_type=activation_type,
            volumes=volumes,
        )

        cross_border_energy_volumes.additional_properties = d
        return cross_border_energy_volumes

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
