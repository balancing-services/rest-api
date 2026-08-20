import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.area import Area
from ...models.balancing_energy_activated_volume_history_response import (
    BalancingEnergyActivatedVolumeHistoryResponse,
)
from ...models.problem import Problem
from ...models.reserve_type import ReserveType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    area: Area,
    period_start_at: datetime.datetime,
    period_end_at: datetime.datetime,
    reserve_type: ReserveType,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_area: str = area
    params["area"] = json_area

    json_period_start_at = period_start_at.isoformat()
    params["period-start-at"] = json_period_start_at

    json_period_end_at = period_end_at.isoformat()
    params["period-end-at"] = json_period_end_at

    json_reserve_type: str = reserve_type
    params["reserve-type"] = json_reserve_type

    params["cursor"] = cursor

    params["limit"] = limit

    json_updated_since: str | Unset = UNSET
    if not isinstance(updated_since, Unset):
        json_updated_since = updated_since.isoformat()
    params["updated-since"] = json_updated_since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/balancing/energy/activated-volumes/history",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BalancingEnergyActivatedVolumeHistoryResponse | Problem | None:
    if response.status_code == 200:
        response_200 = BalancingEnergyActivatedVolumeHistoryResponse.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 400:
        response_400 = Problem.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Problem.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Problem.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Problem.from_dict(response.json())

        return response_404

    if response.status_code == 429:
        response_429 = Problem.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = Problem.from_dict(response.json())

        return response_500

    if response.status_code == 501:
        response_501 = Problem.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[BalancingEnergyActivatedVolumeHistoryResponse | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    area: Area,
    period_start_at: datetime.datetime,
    period_end_at: datetime.datetime,
    reserve_type: ReserveType,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> Response[BalancingEnergyActivatedVolumeHistoryResponse | Problem]:
    """Get the revision history of the activated balancing energy volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the activated balancing energy volumes on `/balancing/energy/activated-volumes`
    reached their current values: the sequence of values held for a period, each stamped with the
    `observedAt` it was recorded at. The response is the `/balancing/energy/activated-volumes`
    shape with `observedAt` added to each entry of `volumes`, which carries the revision entries,
    ascending by `observedAt`.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        reserve_type (ReserveType): Reserve type
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BalancingEnergyActivatedVolumeHistoryResponse | Problem]
    """

    kwargs = _get_kwargs(
        area=area,
        period_start_at=period_start_at,
        period_end_at=period_end_at,
        reserve_type=reserve_type,
        cursor=cursor,
        limit=limit,
        updated_since=updated_since,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    area: Area,
    period_start_at: datetime.datetime,
    period_end_at: datetime.datetime,
    reserve_type: ReserveType,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> BalancingEnergyActivatedVolumeHistoryResponse | Problem | None:
    """Get the revision history of the activated balancing energy volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the activated balancing energy volumes on `/balancing/energy/activated-volumes`
    reached their current values: the sequence of values held for a period, each stamped with the
    `observedAt` it was recorded at. The response is the `/balancing/energy/activated-volumes`
    shape with `observedAt` added to each entry of `volumes`, which carries the revision entries,
    ascending by `observedAt`.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        reserve_type (ReserveType): Reserve type
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BalancingEnergyActivatedVolumeHistoryResponse | Problem
    """

    return sync_detailed(
        client=client,
        area=area,
        period_start_at=period_start_at,
        period_end_at=period_end_at,
        reserve_type=reserve_type,
        cursor=cursor,
        limit=limit,
        updated_since=updated_since,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    area: Area,
    period_start_at: datetime.datetime,
    period_end_at: datetime.datetime,
    reserve_type: ReserveType,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> Response[BalancingEnergyActivatedVolumeHistoryResponse | Problem]:
    """Get the revision history of the activated balancing energy volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the activated balancing energy volumes on `/balancing/energy/activated-volumes`
    reached their current values: the sequence of values held for a period, each stamped with the
    `observedAt` it was recorded at. The response is the `/balancing/energy/activated-volumes`
    shape with `observedAt` added to each entry of `volumes`, which carries the revision entries,
    ascending by `observedAt`.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        reserve_type (ReserveType): Reserve type
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BalancingEnergyActivatedVolumeHistoryResponse | Problem]
    """

    kwargs = _get_kwargs(
        area=area,
        period_start_at=period_start_at,
        period_end_at=period_end_at,
        reserve_type=reserve_type,
        cursor=cursor,
        limit=limit,
        updated_since=updated_since,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    area: Area,
    period_start_at: datetime.datetime,
    period_end_at: datetime.datetime,
    reserve_type: ReserveType,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> BalancingEnergyActivatedVolumeHistoryResponse | Problem | None:
    """Get the revision history of the activated balancing energy volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the activated balancing energy volumes on `/balancing/energy/activated-volumes`
    reached their current values: the sequence of values held for a period, each stamped with the
    `observedAt` it was recorded at. The response is the `/balancing/energy/activated-volumes`
    shape with `observedAt` added to each entry of `volumes`, which carries the revision entries,
    ascending by `observedAt`.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        reserve_type (ReserveType): Reserve type
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BalancingEnergyActivatedVolumeHistoryResponse | Problem
    """

    return (
        await asyncio_detailed(
            client=client,
            area=area,
            period_start_at=period_start_at,
            period_end_at=period_end_at,
            reserve_type=reserve_type,
            cursor=cursor,
            limit=limit,
            updated_since=updated_since,
        )
    ).parsed
