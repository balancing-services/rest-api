from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.area import Area, check_area
from ..models.eic_code import EicCode, check_eic_code

if TYPE_CHECKING:
    from ..models.total_imbalance_volume import TotalImbalanceVolume


T = TypeVar("T", bound="ImbalanceTotalVolumes")


@_attrs_define
class ImbalanceTotalVolumes:
    """
    Attributes:
        area (Area): Area code
        eic_code (EicCode): Energy Identification Code (EIC)
        volumes (list[TotalImbalanceVolume]): Array of total imbalance volumes for each period, direction can vary per
            period
    """

    area: Area
    eic_code: EicCode
    volumes: list[TotalImbalanceVolume]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area: str = self.area

        eic_code: str = self.eic_code

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
                "volumes": volumes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.total_imbalance_volume import TotalImbalanceVolume

        d = dict(src_dict)
        area = check_area(d.pop("area"))

        eic_code = check_eic_code(d.pop("eicCode"))

        volumes = []
        _volumes = d.pop("volumes")
        for volumes_item_data in _volumes:
            volumes_item = TotalImbalanceVolume.from_dict(volumes_item_data)

            volumes.append(volumes_item)

        imbalance_total_volumes = cls(
            area=area,
            eic_code=eic_code,
            volumes=volumes,
        )

        imbalance_total_volumes.additional_properties = d
        return imbalance_total_volumes

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
