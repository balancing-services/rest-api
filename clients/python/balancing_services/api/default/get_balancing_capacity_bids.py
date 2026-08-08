import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.area import Area
from ...models.balancing_capacity_bids_response import BalancingCapacityBidsResponse
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
        "url": "/balancing/capacity/bids",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BalancingCapacityBidsResponse | Problem | None:
    if response.status_code == 200:
        response_200 = BalancingCapacityBidsResponse.from_dict(response.json())

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
) -> Response[BalancingCapacityBidsResponse | Problem]:
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
) -> Response[BalancingCapacityBidsResponse | Problem]:
    """Get balancing capacity bids

     Returns balancing capacity bids for the specified area within the given time period. Prices are
    in the specified currency per MW per hour.

    Bids are grouped by their shared dimensions (area, reserve type, direction, currency), and inside
    each group by delivery period: each entry of `periods` states the period once and carries that
    period's bids. Period entries ascend by period start within their group. Each bid carries the
    procurement it was submitted to (`procurement.procuredAt`) — a single period entry can mix bids
    from multiple procurement rounds.

    Supports cursor-based pagination for large result sets; `limit` counts individual bids, not
    groups or period entries. Groups and period entries are assembled per page: when `hasMore` is
    true the last period entry may continue on the next page, so merge entries on their group's
    dimensions plus the period when accumulating pages. Bids within a period entry are returned in no
    guaranteed order — sort by price client-side if you need the merit order. When polling with
    `updated-since`, change is tracked per stored bid set rather than per bid — each procurement
    round of a period is its own set: a changed set is re-delivered with its unchanged bids
    included, so the period entries of a poll are not necessarily contiguous. A period entry may
    span more than one set, and a set that changes again mid-drain is deferred to the next poll,
    so a filtered response is not guaranteed to carry a period's complete bid set — re-fetch
    without `updated-since` to reconcile withdrawals.

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
        Response[BalancingCapacityBidsResponse | Problem]
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
) -> BalancingCapacityBidsResponse | Problem | None:
    """Get balancing capacity bids

     Returns balancing capacity bids for the specified area within the given time period. Prices are
    in the specified currency per MW per hour.

    Bids are grouped by their shared dimensions (area, reserve type, direction, currency), and inside
    each group by delivery period: each entry of `periods` states the period once and carries that
    period's bids. Period entries ascend by period start within their group. Each bid carries the
    procurement it was submitted to (`procurement.procuredAt`) — a single period entry can mix bids
    from multiple procurement rounds.

    Supports cursor-based pagination for large result sets; `limit` counts individual bids, not
    groups or period entries. Groups and period entries are assembled per page: when `hasMore` is
    true the last period entry may continue on the next page, so merge entries on their group's
    dimensions plus the period when accumulating pages. Bids within a period entry are returned in no
    guaranteed order — sort by price client-side if you need the merit order. When polling with
    `updated-since`, change is tracked per stored bid set rather than per bid — each procurement
    round of a period is its own set: a changed set is re-delivered with its unchanged bids
    included, so the period entries of a poll are not necessarily contiguous. A period entry may
    span more than one set, and a set that changes again mid-drain is deferred to the next poll,
    so a filtered response is not guaranteed to carry a period's complete bid set — re-fetch
    without `updated-since` to reconcile withdrawals.

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
        BalancingCapacityBidsResponse | Problem
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
) -> Response[BalancingCapacityBidsResponse | Problem]:
    """Get balancing capacity bids

     Returns balancing capacity bids for the specified area within the given time period. Prices are
    in the specified currency per MW per hour.

    Bids are grouped by their shared dimensions (area, reserve type, direction, currency), and inside
    each group by delivery period: each entry of `periods` states the period once and carries that
    period's bids. Period entries ascend by period start within their group. Each bid carries the
    procurement it was submitted to (`procurement.procuredAt`) — a single period entry can mix bids
    from multiple procurement rounds.

    Supports cursor-based pagination for large result sets; `limit` counts individual bids, not
    groups or period entries. Groups and period entries are assembled per page: when `hasMore` is
    true the last period entry may continue on the next page, so merge entries on their group's
    dimensions plus the period when accumulating pages. Bids within a period entry are returned in no
    guaranteed order — sort by price client-side if you need the merit order. When polling with
    `updated-since`, change is tracked per stored bid set rather than per bid — each procurement
    round of a period is its own set: a changed set is re-delivered with its unchanged bids
    included, so the period entries of a poll are not necessarily contiguous. A period entry may
    span more than one set, and a set that changes again mid-drain is deferred to the next poll,
    so a filtered response is not guaranteed to carry a period's complete bid set — re-fetch
    without `updated-since` to reconcile withdrawals.

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
        Response[BalancingCapacityBidsResponse | Problem]
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
) -> BalancingCapacityBidsResponse | Problem | None:
    """Get balancing capacity bids

     Returns balancing capacity bids for the specified area within the given time period. Prices are
    in the specified currency per MW per hour.

    Bids are grouped by their shared dimensions (area, reserve type, direction, currency), and inside
    each group by delivery period: each entry of `periods` states the period once and carries that
    period's bids. Period entries ascend by period start within their group. Each bid carries the
    procurement it was submitted to (`procurement.procuredAt`) — a single period entry can mix bids
    from multiple procurement rounds.

    Supports cursor-based pagination for large result sets; `limit` counts individual bids, not
    groups or period entries. Groups and period entries are assembled per page: when `hasMore` is
    true the last period entry may continue on the next page, so merge entries on their group's
    dimensions plus the period when accumulating pages. Bids within a period entry are returned in no
    guaranteed order — sort by price client-side if you need the merit order. When polling with
    `updated-since`, change is tracked per stored bid set rather than per bid — each procurement
    round of a period is its own set: a changed set is re-delivered with its unchanged bids
    included, so the period entries of a poll are not necessarily contiguous. A period entry may
    span more than one set, and a set that changes again mid-drain is deferred to the next poll,
    so a filtered response is not guaranteed to carry a period's complete bid set — re-fetch
    without `updated-since` to reconcile withdrawals.

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
        BalancingCapacityBidsResponse | Problem
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
