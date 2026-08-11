from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.period import Period


T = TypeVar("T", bound="ImbalancePriceRevision")


@_attrs_define
class ImbalancePriceRevision:
    """
    Attributes:
        period (Period):
        price_per_mwh (float): Price per MWh in the specified currency Example: 45.5.
        observed_at (datetime.datetime): When this revision was recorded (UTC) Example: 2026-08-04T10:07:31Z.
    """

    period: Period
    price_per_mwh: float
    observed_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.to_dict()

        price_per_mwh = self.price_per_mwh

        observed_at = self.observed_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "pricePerMwh": price_per_mwh,
                "observedAt": observed_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.period import Period

        d = dict(src_dict)
        period = Period.from_dict(d.pop("period"))

        price_per_mwh = d.pop("pricePerMwh")

        observed_at = datetime.datetime.fromisoformat(d.pop("observedAt").replace("Z", "+00:00"))

        imbalance_price_revision = cls(
            period=period,
            price_per_mwh=price_per_mwh,
            observed_at=observed_at,
        )

        imbalance_price_revision.additional_properties = d
        return imbalance_price_revision

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
