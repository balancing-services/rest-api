from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.period import Period


T = TypeVar("T", bound="BalancingEnergyOfferedVolumeRevision")


@_attrs_define
class BalancingEnergyOfferedVolumeRevision:
    """
    Attributes:
        period (Period):
        volume_in_mw (float): Average power in MW over the period Example: 250.5.
        observed_at (datetime.datetime): When this revision was recorded (UTC) Example: 2026-08-19T10:07:31Z.
    """

    period: Period
    volume_in_mw: float
    observed_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        volume_in_mw = self.volume_in_mw

        observed_at = self.observed_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "volumeInMw": volume_in_mw,
                "observedAt": observed_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        volume_in_mw = d.pop("volumeInMw")

        observed_at = datetime.datetime.fromisoformat(d.pop("observedAt").replace("Z", "+00:00"))

        balancing_energy_offered_volume_revision = cls(
            period=period,
            volume_in_mw=volume_in_mw,
            observed_at=observed_at,
        )

        balancing_energy_offered_volume_revision.additional_properties = d
        return balancing_energy_offered_volume_revision

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
