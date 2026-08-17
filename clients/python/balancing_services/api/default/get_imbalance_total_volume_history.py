import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.area import Area
from ...models.imbalance_total_volume_history_response import (
    ImbalanceTotalVolumeHistoryResponse,
)
from ...models.problem import Problem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    area: Area,
    period_start_at: datetime.datetime,
    period_end_at: datetime.datetime,
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

    params["cursor"] = cursor

    params["limit"] = limit

    json_updated_since: str | Unset = UNSET
    if not isinstance(updated_since, Unset):
        json_updated_since = updated_since.isoformat()
    params["updated-since"] = json_updated_since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/imbalance/total-volumes/history",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ImbalanceTotalVolumeHistoryResponse | Problem | None:
    if response.status_code == 200:
        response_200 = ImbalanceTotalVolumeHistoryResponse.from_dict(response.json())

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
) -> Response[ImbalanceTotalVolumeHistoryResponse | Problem]:
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
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> Response[ImbalanceTotalVolumeHistoryResponse | Problem]:
    """Get the revision history of the total imbalance volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the total imbalance volumes on `/imbalance/total-volumes` reached their current
    values: the sequence of values held for a period, each stamped with the `observedAt` it was
    recorded at. The response is the `/imbalance/total-volumes` shape with `observedAt` added to
    each entry of `volumes`, which carries the revision entries, each period's ascending by
    `observedAt` and the periods themselves in page order. A period appears once per change of
    the value served for it — its direction or its magnitude — except for entries sharing an
    `observedAt`, which are all returned because no order is recorded within an instant.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ImbalanceTotalVolumeHistoryResponse | Problem]
    """

    kwargs = _get_kwargs(
        area=area,
        period_start_at=period_start_at,
        period_end_at=period_end_at,
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
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> ImbalanceTotalVolumeHistoryResponse | Problem | None:
    """Get the revision history of the total imbalance volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the total imbalance volumes on `/imbalance/total-volumes` reached their current
    values: the sequence of values held for a period, each stamped with the `observedAt` it was
    recorded at. The response is the `/imbalance/total-volumes` shape with `observedAt` added to
    each entry of `volumes`, which carries the revision entries, each period's ascending by
    `observedAt` and the periods themselves in page order. A period appears once per change of
    the value served for it — its direction or its magnitude — except for entries sharing an
    `observedAt`, which are all returned because no order is recorded within an instant.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ImbalanceTotalVolumeHistoryResponse | Problem
    """

    return sync_detailed(
        client=client,
        area=area,
        period_start_at=period_start_at,
        period_end_at=period_end_at,
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
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> Response[ImbalanceTotalVolumeHistoryResponse | Problem]:
    """Get the revision history of the total imbalance volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the total imbalance volumes on `/imbalance/total-volumes` reached their current
    values: the sequence of values held for a period, each stamped with the `observedAt` it was
    recorded at. The response is the `/imbalance/total-volumes` shape with `observedAt` added to
    each entry of `volumes`, which carries the revision entries, each period's ascending by
    `observedAt` and the periods themselves in page order. A period appears once per change of
    the value served for it — its direction or its magnitude — except for entries sharing an
    `observedAt`, which are all returned because no order is recorded within an instant.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ImbalanceTotalVolumeHistoryResponse | Problem]
    """

    kwargs = _get_kwargs(
        area=area,
        period_start_at=period_start_at,
        period_end_at=period_end_at,
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
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
    updated_since: datetime.datetime | Unset = UNSET,
) -> ImbalanceTotalVolumeHistoryResponse | Problem | None:
    """Get the revision history of the total imbalance volumes for an area

     **Experimental** - This endpoint is under active development and may change without notice.

    Returns how the total imbalance volumes on `/imbalance/total-volumes` reached their current
    values: the sequence of values held for a period, each stamped with the `observedAt` it was
    recorded at. The response is the `/imbalance/total-volumes` shape with `observedAt` added to
    each entry of `volumes`, which carries the revision entries, each period's ascending by
    `observedAt` and the periods themselves in page order. A period appears once per change of
    the value served for it — its direction or its magnitude — except for entries sharing an
    `observedAt`, which are all returned because no order is recorded within an instant.

    Args:
        area (Area): Area code
        period_start_at (datetime.datetime):  Example: 2025-01-01T00:00:00Z.
        period_end_at (datetime.datetime):  Example: 2025-01-02T00:00:00Z.
        cursor (str | Unset):  Example: v1:AAAAAYwBAgMEBQYHCAkKCw==.
        limit (int | Unset):  Default: 100. Example: 100.
        updated_since (datetime.datetime | Unset):  Example: 2025-01-02T09:15:00Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ImbalanceTotalVolumeHistoryResponse | Problem
    """

    return (
        await asyncio_detailed(
            client=client,
            area=area,
            period_start_at=period_start_at,
            period_end_at=period_end_at,
            cursor=cursor,
            limit=limit,
            updated_since=updated_since,
        )
    ).parsed
