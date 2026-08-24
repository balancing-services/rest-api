from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.bid_availability import BidAvailability, check_bid_availability
from ..models.eligible_activation_type import (
    EligibleActivationType,
    check_eligible_activation_type,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnergyBid")


@_attrs_define
class EnergyBid:
    """
    Attributes:
        volume_in_mw (float): Bid volume in MW Example: 100.
        price_per_mwh (float): Bid price per MWh in the specified currency Example: 55.25.
        divisible (bool | None | Unset): **Experimental** — may change or be removed without notice.

            Whether the TSO may activate only part of the bid: true when partial activation is
            allowed, false when the bid is all-or-nothing. Null (or absent) when the value is not
            available; absent and null are equivalent.
             Example: True.
        eligible_activation_types (list[EligibleActivationType] | None | Unset): **Experimental** — may change or be
            removed without notice.

            The activation modes the bid may be selected for. A set: no element order is promised
            and elements are unique. Null (or absent) when the value is not available; absent and
            null are equivalent.
             Example: ['direct', 'scheduled'].
        minimum_volume_in_mw (float | None | Unset): **Experimental** — may change or be removed without notice.

            Smallest volume in MW the TSO may activate from this bid when activating it partially,
            relayed as published by the source; no cross-field invariant with `divisible` is
            promised. Null (or absent) when the value is not available; absent and null are
            equivalent.
             Example: 1.
        availability (BidAvailability | None | Unset): **Experimental** — may change or be removed without notice.

            The lifecycle state the source published the bid in. Null (or absent) when the value
            is not available; absent and null are equivalent.
             Example: available.
    """

    volume_in_mw: float
    price_per_mwh: float
    divisible: bool | None | Unset = UNSET
    eligible_activation_types: list[EligibleActivationType] | None | Unset = UNSET
    minimum_volume_in_mw: float | None | Unset = UNSET
    availability: BidAvailability | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volume_in_mw = self.volume_in_mw

        price_per_mwh = self.price_per_mwh

        divisible: bool | None | Unset
        if isinstance(self.divisible, Unset):
            divisible = UNSET
        else:
            divisible = self.divisible

        eligible_activation_types: list[str] | None | Unset
        if isinstance(self.eligible_activation_types, Unset):
            eligible_activation_types = UNSET
        elif isinstance(self.eligible_activation_types, list):
            eligible_activation_types = []
            for (
                eligible_activation_types_type_0_item_data
            ) in self.eligible_activation_types:
                eligible_activation_types_type_0_item: str = (
                    eligible_activation_types_type_0_item_data
                )
                eligible_activation_types.append(eligible_activation_types_type_0_item)

        else:
            eligible_activation_types = self.eligible_activation_types

        minimum_volume_in_mw: float | None | Unset
        if isinstance(self.minimum_volume_in_mw, Unset):
            minimum_volume_in_mw = UNSET
        else:
            minimum_volume_in_mw = self.minimum_volume_in_mw

        availability: None | str | Unset
        if isinstance(self.availability, Unset):
            availability = UNSET
        elif isinstance(self.availability, str):
            availability = self.availability
        else:
            availability = self.availability

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "volumeInMw": volume_in_mw,
                "pricePerMwh": price_per_mwh,
            }
        )
        if divisible is not UNSET:
            field_dict["divisible"] = divisible
        if eligible_activation_types is not UNSET:
            field_dict["eligibleActivationTypes"] = eligible_activation_types
        if minimum_volume_in_mw is not UNSET:
            field_dict["minimumVolumeInMw"] = minimum_volume_in_mw
        if availability is not UNSET:
            field_dict["availability"] = availability

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        volume_in_mw = d.pop("volumeInMw")

        price_per_mwh = d.pop("pricePerMwh")

        def _parse_divisible(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        divisible = _parse_divisible(d.pop("divisible", UNSET))

        def _parse_eligible_activation_types(
            data: object,
        ) -> list[EligibleActivationType] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                eligible_activation_types_type_0 = []
                _eligible_activation_types_type_0 = data
                for (
                    eligible_activation_types_type_0_item_data
                ) in _eligible_activation_types_type_0:
                    eligible_activation_types_type_0_item = (
                        check_eligible_activation_type(
                            eligible_activation_types_type_0_item_data
                        )
                    )

                    eligible_activation_types_type_0.append(
                        eligible_activation_types_type_0_item
                    )

                return eligible_activation_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EligibleActivationType] | None | Unset, data)

        eligible_activation_types = _parse_eligible_activation_types(
            d.pop("eligibleActivationTypes", UNSET)
        )

        def _parse_minimum_volume_in_mw(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        minimum_volume_in_mw = _parse_minimum_volume_in_mw(
            d.pop("minimumVolumeInMw", UNSET)
        )

        def _parse_availability(data: object) -> BidAvailability | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                availability_type_1 = check_bid_availability(data)

                return availability_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BidAvailability | None | Unset, data)

        availability = _parse_availability(d.pop("availability", UNSET))

        energy_bid = cls(
            volume_in_mw=volume_in_mw,
            price_per_mwh=price_per_mwh,
            divisible=divisible,
            eligible_activation_types=eligible_activation_types,
            minimum_volume_in_mw=minimum_volume_in_mw,
            availability=availability,
        )

        energy_bid.additional_properties = d
        return energy_bid

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
