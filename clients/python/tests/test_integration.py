"""
Integration tests using respx to mock HTTP responses.
"""

from datetime import datetime, timezone

import pytest
import respx
from httpx import Response

from balancing_services import AuthenticatedClient
from balancing_services.api.default import (
    get_balancing_capacity_demand,
    get_balancing_energy_bids,
    get_balancing_energy_demand,
    get_balancing_energy_offered_volumes,
    get_balancing_energy_satisfied_demand,
    get_cross_border_available_capacity,
    get_cross_border_energy_volumes,
    get_cross_border_marginal_prices,
    get_cross_zonal_capacity_allocation,
    get_current_imbalance_total_volumes,
    get_day_ahead_energy_prices,
    get_imbalance_price_forecasts,
    get_imbalance_price_history,
    get_imbalance_prices,
    get_imbalance_total_volume_history,
)


@pytest.fixture
def authenticated_client():
    """Create an authenticated client for testing."""
    return AuthenticatedClient(
        base_url="https://api.balancing.services/v2",
        token="test_token_12345"
    )


@pytest.fixture
def mock_imbalance_prices_response():
    """Mock response data for imbalance prices."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "direction": "positive",
                "currency": "EUR",
                "prices": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "pricePerMwh": 45.5
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_balancing_energy_bids_response():
    """Mock response data for balancing energy bids."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "reserveType": "aFRR",
                "direction": "up",
                "standardProduct": True,
                "currency": "EUR",
                "periods": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "bids": [
                            {
                                "volumeInMw": 10.5,
                                "pricePerMwh": 25.0
                            }
                        ]
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_imbalance_prices_success(authenticated_client, mock_imbalance_prices_response):
    """Test successful imbalance prices request."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/prices"
    ).mock(return_value=Response(200, json=mock_imbalance_prices_response))

    response = get_imbalance_prices.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.5


@respx.mock
def test_get_imbalance_prices_unauthorized(authenticated_client):
    """Test unauthorized response (401)."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/prices"
    ).mock(return_value=Response(401, json=error_response))

    response = get_imbalance_prices.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@respx.mock
def test_get_imbalance_prices_bad_request(authenticated_client):
    """Test bad request response (400)."""
    error_response = {
        "type": "invalid-parameter",
        "title": "Bad Request",
        "status": 400,
        "detail": "Invalid period range"
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/prices"
    ).mock(return_value=Response(400, json=error_response))

    response = get_imbalance_prices.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 400
    assert response.parsed is not None
    assert response.parsed.detail == "Invalid period range"


@respx.mock
def test_get_balancing_energy_bids_pagination(authenticated_client, mock_balancing_energy_bids_response):
    """Test pagination with balancing energy bids."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/bids"
    ).mock(return_value=Response(200, json=mock_balancing_energy_bids_response))

    response = get_balancing_energy_bids.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        limit=100
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].periods[0].bids[0].volume_in_mw == 10.5
    assert response.parsed.data[0].periods[0].bids[0].price_per_mwh == 25.0


@respx.mock
def test_authentication_header_included(authenticated_client, mock_imbalance_prices_response):
    """Test that authentication header is included in requests."""
    route = respx.get(
        "https://api.balancing.services/v2/imbalance/prices",
        headers={"Authorization": "Bearer test_token_12345"}
    ).mock(return_value=Response(200, json=mock_imbalance_prices_response))

    response = get_imbalance_prices.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_async_get_imbalance_prices(authenticated_client, mock_imbalance_prices_response):
    """Test async request for imbalance prices."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/prices"
    ).mock(return_value=Response(200, json=mock_imbalance_prices_response))

    response = await get_imbalance_prices.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.5


@pytest.fixture
def mock_offered_volumes_response():
    """Mock response data for offered balancing energy volumes."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "reserveType": "aFRR",
                "direction": "up",
                "activationType": "direct",
                "standardProduct": True,
                "volumes": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "volumeInMw": 50.0
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_cross_zonal_allocation_response():
    """Mock response data for cross-zonal capacity allocation."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "fromArea": "EE",
                "fromEicCode": "10Y1001A1001A39I",
                "toArea": "LV",
                "toEicCode": "10YLV-1001A00074",
                "reserveType": "aFRR",
                "volumes": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "volumeInMw": 25.0
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_balancing_energy_offered_volumes_success(authenticated_client, mock_offered_volumes_response):
    """Test successful offered balancing energy volumes request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/offered-volumes"
    ).mock(return_value=Response(200, json=mock_offered_volumes_response))

    response = get_balancing_energy_offered_volumes.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    assert response.parsed.data[0].volumes[0].volume_in_mw == 50.0


@respx.mock
def test_get_balancing_energy_offered_volumes_unauthorized(authenticated_client):
    """Test unauthorized response (401) for offered volumes."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/energy/offered-volumes"
    ).mock(return_value=Response(401, json=error_response))

    response = get_balancing_energy_offered_volumes.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_balancing_energy_offered_volumes(authenticated_client, mock_offered_volumes_response):
    """Test async request for offered balancing energy volumes."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/offered-volumes"
    ).mock(return_value=Response(200, json=mock_offered_volumes_response))

    response = await get_balancing_energy_offered_volumes.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].volumes[0].volume_in_mw == 50.0


@respx.mock
def test_get_cross_zonal_capacity_allocation_success(authenticated_client, mock_cross_zonal_allocation_response):
    """Test successful cross-zonal capacity allocation request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/capacity/cross-zonal-allocation"
    ).mock(return_value=Response(200, json=mock_cross_zonal_allocation_response))

    response = get_cross_zonal_capacity_allocation.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="LV"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].from_area == "EE"
    assert response.parsed.data[0].to_area == "LV"
    assert response.parsed.data[0].volumes[0].volume_in_mw == 25.0


@respx.mock
def test_get_cross_zonal_capacity_allocation_unauthorized(authenticated_client):
    """Test unauthorized response (401) for cross-zonal allocation."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/capacity/cross-zonal-allocation"
    ).mock(return_value=Response(401, json=error_response))

    response = get_cross_zonal_capacity_allocation.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="LV"
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_cross_zonal_capacity_allocation(authenticated_client, mock_cross_zonal_allocation_response):
    """Test async request for cross-zonal capacity allocation."""
    respx.get(
        "https://api.balancing.services/v2/balancing/capacity/cross-zonal-allocation"
    ).mock(return_value=Response(200, json=mock_cross_zonal_allocation_response))

    response = await get_cross_zonal_capacity_allocation.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="LV"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].volumes[0].volume_in_mw == 25.0


@pytest.fixture
def mock_balancing_energy_demand_response():
    """Mock response data for balancing energy demand (also used for satisfied demand)."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "reserveType": "aFRR",
                "direction": "up",
                "activationType": "notApplicable",
                "standardProduct": True,
                "volumes": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "volumeInMw": 80.0
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_balancing_energy_demand_success(authenticated_client, mock_balancing_energy_demand_response):
    """Test successful balancing energy demand request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/demand"
    ).mock(return_value=Response(200, json=mock_balancing_energy_demand_response))

    response = get_balancing_energy_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    assert response.parsed.data[0].reserve_type == "aFRR"
    assert response.parsed.data[0].direction == "up"
    assert response.parsed.data[0].volumes[0].volume_in_mw == 80.0


@respx.mock
def test_get_balancing_energy_demand_pagination(authenticated_client, mock_balancing_energy_demand_response):
    """Test balancing energy demand pagination - cursor/limit sent, nextCursor parsed."""
    paginated_response = {
        **mock_balancing_energy_demand_response,
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/balancing/energy/demand"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_balancing_energy_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"


@respx.mock
def test_get_balancing_energy_demand_unauthorized(authenticated_client):
    """Test unauthorized response (401) for balancing energy demand."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/energy/demand"
    ).mock(return_value=Response(401, json=error_response))

    response = get_balancing_energy_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_balancing_energy_demand(authenticated_client, mock_balancing_energy_demand_response):
    """Test async request for balancing energy demand."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/demand"
    ).mock(return_value=Response(200, json=mock_balancing_energy_demand_response))

    response = await get_balancing_energy_demand.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].volumes[0].volume_in_mw == 80.0


@respx.mock
def test_get_balancing_energy_satisfied_demand_success(authenticated_client, mock_balancing_energy_demand_response):
    """Test successful satisfied balancing energy demand request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/satisfied-demand"
    ).mock(return_value=Response(200, json=mock_balancing_energy_demand_response))

    response = get_balancing_energy_satisfied_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    assert response.parsed.data[0].reserve_type == "aFRR"
    assert response.parsed.data[0].volumes[0].volume_in_mw == 80.0


@respx.mock
def test_get_balancing_energy_satisfied_demand_pagination(authenticated_client, mock_balancing_energy_demand_response):
    """Test satisfied balancing energy demand pagination - cursor/limit sent, nextCursor parsed."""
    paginated_response = {
        **mock_balancing_energy_demand_response,
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/balancing/energy/satisfied-demand"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_balancing_energy_satisfied_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"


@respx.mock
def test_get_balancing_energy_satisfied_demand_unauthorized(authenticated_client):
    """Test unauthorized response (401) for satisfied balancing energy demand."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/energy/satisfied-demand"
    ).mock(return_value=Response(401, json=error_response))

    response = get_balancing_energy_satisfied_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_balancing_energy_satisfied_demand(authenticated_client, mock_balancing_energy_demand_response):
    """Test async request for satisfied balancing energy demand."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/satisfied-demand"
    ).mock(return_value=Response(200, json=mock_balancing_energy_demand_response))

    response = await get_balancing_energy_satisfied_demand.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].volumes[0].volume_in_mw == 80.0


@pytest.fixture
def mock_balancing_capacity_demand_response():
    """Mock response data for balancing capacity demand."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "reserveType": "aFRR",
                "direction": "up",
                "procurement": {"procuredAt": "2024-12-31T09:00:00Z"},
                "demandBasis": "additive",
                "demands": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "totalDemandInMw": 80.0,
                        "localDemandInMw": 30.0
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_balancing_capacity_demand_success(authenticated_client, mock_balancing_capacity_demand_response):
    """Test successful balancing capacity demand request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/capacity/demand"
    ).mock(return_value=Response(200, json=mock_balancing_capacity_demand_response))

    response = get_balancing_capacity_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    assert response.parsed.data[0].reserve_type == "aFRR"
    assert response.parsed.data[0].direction == "up"
    assert response.parsed.data[0].demand_basis == "additive"
    assert response.parsed.data[0].demands[0].total_demand_in_mw == 80.0
    assert response.parsed.data[0].demands[0].local_demand_in_mw == 30.0


@respx.mock
def test_get_balancing_capacity_demand_pagination(authenticated_client, mock_balancing_capacity_demand_response):
    """Test balancing capacity demand pagination - cursor/limit sent, nextCursor parsed."""
    paginated_response = {
        **mock_balancing_capacity_demand_response,
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/balancing/capacity/demand"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_balancing_capacity_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"


@respx.mock
def test_get_balancing_capacity_demand_unauthorized(authenticated_client):
    """Test unauthorized response (401) for balancing capacity demand."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/capacity/demand"
    ).mock(return_value=Response(401, json=error_response))

    response = get_balancing_capacity_demand.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_balancing_capacity_demand(authenticated_client, mock_balancing_capacity_demand_response):
    """Test async request for balancing capacity demand."""
    respx.get(
        "https://api.balancing.services/v2/balancing/capacity/demand"
    ).mock(return_value=Response(200, json=mock_balancing_capacity_demand_response))

    response = await get_balancing_capacity_demand.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR"
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].demands[0].total_demand_in_mw == 80.0


@pytest.fixture
def mock_cross_border_marginal_prices_response():
    """Mock response data for cross-border marginal prices."""
    return {
        "queriedPeriod": {
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-01T01:00:00Z"
        },
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
        "data": [
            {
                "area": "AT",
                "eicCode": "10YAT-APG------L",
                "reserveType": "aFRR",
                "direction": "up",
                "currency": "EUR",
                "prices": [
                    {
                        "period": {
                            "startAt": "2026-03-01T00:00:00Z",
                            "endAt": "2026-03-01T00:15:00Z"
                        },
                        "pricePerMwh": 45.50
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_cross_border_marginal_prices_success(authenticated_client, mock_cross_border_marginal_prices_response):
    """Test successful cross-border marginal prices request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-marginal-prices"
    ).mock(return_value=Response(200, json=mock_cross_border_marginal_prices_response))

    response = get_cross_border_marginal_prices.sync_detailed(
        client=authenticated_client,
        area="AT",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "AT"
    assert response.parsed.data[0].direction == "up"
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.50


@respx.mock
def test_get_cross_border_marginal_prices_unauthorized(authenticated_client):
    """Test unauthorized response (401) for cross-border marginal prices."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-marginal-prices"
    ).mock(return_value=Response(401, json=error_response))

    response = get_cross_border_marginal_prices.sync_detailed(
        client=authenticated_client,
        area="AT",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_cross_border_marginal_prices(authenticated_client, mock_cross_border_marginal_prices_response):
    """Test async request for cross-border marginal prices."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-marginal-prices"
    ).mock(return_value=Response(200, json=mock_cross_border_marginal_prices_response))

    response = await get_cross_border_marginal_prices.asyncio_detailed(
        client=authenticated_client,
        area="AT",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.50


@pytest.fixture
def mock_cross_border_energy_volumes_response():
    """Mock response data for cross-border balancing energy volumes."""
    return {
        "queriedPeriod": {
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "fromArea": "EE",
                "fromEicCode": "10Y1001A1001A39I",
                "toArea": "FI",
                "toEicCode": "10YFI-1--------U",
                "reserveType": "aFRR",
                "activationType": "notApplicable",
                "volumes": [
                    {
                        "period": {
                            "startAt": "2026-03-01T00:00:00Z",
                            "endAt": "2026-03-01T00:15:00Z"
                        },
                        "volumeInMw": 250.5
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_cross_border_energy_volumes_success(authenticated_client, mock_cross_border_energy_volumes_response):
    """Test successful cross-border balancing energy volumes request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-volumes"
    ).mock(return_value=Response(200, json=mock_cross_border_energy_volumes_response))

    response = get_cross_border_energy_volumes.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="EE",
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].from_area == "EE"
    assert response.parsed.data[0].to_area == "FI"
    assert response.parsed.data[0].reserve_type == "aFRR"
    assert response.parsed.data[0].activation_type == "notApplicable"
    assert response.parsed.data[0].volumes[0].volume_in_mw == 250.5


@respx.mock
def test_get_cross_border_energy_volumes_unauthorized(authenticated_client):
    """Test unauthorized response (401) for cross-border balancing energy volumes."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-volumes"
    ).mock(return_value=Response(401, json=error_response))

    response = get_cross_border_energy_volumes.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="EE",
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_cross_border_energy_volumes(authenticated_client, mock_cross_border_energy_volumes_response):
    """Test async request for cross-border balancing energy volumes."""
    respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-volumes"
    ).mock(return_value=Response(200, json=mock_cross_border_energy_volumes_response))

    response = await get_cross_border_energy_volumes.asyncio_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="EE",
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].volumes[0].volume_in_mw == 250.5


@respx.mock
def test_get_cross_border_energy_volumes_pagination(authenticated_client, mock_cross_border_energy_volumes_response):
    """Test cross-border balancing energy volumes pagination - cursor/limit sent, nextCursor parsed."""
    paginated_response = {
        **mock_cross_border_energy_volumes_response,
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/balancing/energy/cross-border-volumes"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_cross_border_energy_volumes.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2026, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        other_area="EE",
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    # The cursor/limit must actually be transmitted as query params (the cursor
    # is what disambiguates the from->to / to->from union halves for this endpoint).
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"
    assert response.parsed.data[0].volumes[0].volume_in_mw == 250.5


@pytest.fixture
def mock_cross_border_available_capacity_response():
    """Mock response data for cross-border available capacity (both border directions)."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "fromArea": "FI",
                "fromEicCode": "10YFI-1--------U",
                "toArea": "SE3",
                "toEicCode": "10Y1001A1001A46L",
                "reserveType": "aFRR",
                "availableCapacities": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "availableCapacityInMw": 150.0
                    }
                ]
            },
            {
                "fromArea": "SE3",
                "fromEicCode": "10Y1001A1001A46L",
                "toArea": "FI",
                "toEicCode": "10YFI-1--------U",
                "reserveType": "aFRR",
                "availableCapacities": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "availableCapacityInMw": 80.5
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_cross_border_available_capacity_success(
    authenticated_client, mock_cross_border_available_capacity_response
):
    """Test successful cross-border available capacity request."""
    respx.get(
        "https://api.balancing.services/v2/balancing/cross-border/available-capacity"
    ).mock(return_value=Response(200, json=mock_cross_border_available_capacity_response))

    response = get_cross_border_available_capacity.sync_detailed(
        client=authenticated_client,
        area="FI",
        other_area="SE3",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    # Both border directions are returned (area -> other-area and other-area -> area).
    assert len(response.parsed.data) == 2
    assert response.parsed.data[0].from_area == "FI"
    assert response.parsed.data[0].to_area == "SE3"
    assert response.parsed.data[0].reserve_type == "aFRR"
    assert response.parsed.data[0].available_capacities[0].available_capacity_in_mw == 150.0
    assert response.parsed.data[1].from_area == "SE3"
    assert response.parsed.data[1].to_area == "FI"
    assert response.parsed.data[1].available_capacities[0].available_capacity_in_mw == 80.5


@respx.mock
def test_get_cross_border_available_capacity_unauthorized(authenticated_client):
    """Test unauthorized response (401) for cross-border available capacity."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/balancing/cross-border/available-capacity"
    ).mock(return_value=Response(401, json=error_response))

    response = get_cross_border_available_capacity.sync_detailed(
        client=authenticated_client,
        area="FI",
        other_area="SE3",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_cross_border_available_capacity(
    authenticated_client, mock_cross_border_available_capacity_response
):
    """Test async request for cross-border available capacity."""
    respx.get(
        "https://api.balancing.services/v2/balancing/cross-border/available-capacity"
    ).mock(return_value=Response(200, json=mock_cross_border_available_capacity_response))

    response = await get_cross_border_available_capacity.asyncio_detailed(
        client=authenticated_client,
        area="FI",
        other_area="SE3",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 2
    assert response.parsed.data[0].available_capacities[0].available_capacity_in_mw == 150.0


@respx.mock
def test_get_cross_border_available_capacity_pagination(
    authenticated_client, mock_cross_border_available_capacity_response
):
    """Test cross-border available capacity pagination - cursor/limit sent, nextCursor parsed."""
    paginated_response = {
        **mock_cross_border_available_capacity_response,
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/balancing/cross-border/available-capacity"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_cross_border_available_capacity.sync_detailed(
        client=authenticated_client,
        area="FI",
        other_area="SE3",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        reserve_type="aFRR",
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"
    # Both border ends must be transmitted as query params.
    assert sent_url.params["area"] == "FI"
    assert sent_url.params["other-area"] == "SE3"


@pytest.fixture
def mock_current_imbalance_total_volumes_response():
    """Mock response data for current (provisional) total imbalance volumes."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T02:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "volumes": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:01:00Z"
                        },
                        "averagePowerMW": 4.2,
                        "averagePowerInMw": 4.2,
                        "direction": "surplus"
                    },
                    {
                        "period": {
                            "startAt": "2025-01-01T00:01:00Z",
                            "endAt": "2025-01-01T00:02:00Z"
                        },
                        "averagePowerMW": 7.5,
                        "averagePowerInMw": 7.5,
                        "direction": "deficit"
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_current_imbalance_total_volumes_success(
    authenticated_client, mock_current_imbalance_total_volumes_response
):
    """Test successful current imbalance total volumes request."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/current"
    ).mock(return_value=Response(200, json=mock_current_imbalance_total_volumes_response))

    response = get_current_imbalance_total_volumes.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 2, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    # Per-minute values carry an unsigned magnitude plus a direction.
    assert response.parsed.data[0].volumes[0].average_power_in_mw == 4.2
    assert response.parsed.data[0].volumes[0].direction == "surplus"
    assert response.parsed.data[0].volumes[1].average_power_in_mw == 7.5
    assert response.parsed.data[0].volumes[1].direction == "deficit"


@respx.mock
def test_get_current_imbalance_total_volumes_unauthorized(authenticated_client):
    """Test unauthorized response (401) for current imbalance total volumes."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/current"
    ).mock(return_value=Response(401, json=error_response))

    response = get_current_imbalance_total_volumes.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 2, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_current_imbalance_total_volumes(
    authenticated_client, mock_current_imbalance_total_volumes_response
):
    """Test async request for current imbalance total volumes."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/current"
    ).mock(return_value=Response(200, json=mock_current_imbalance_total_volumes_response))

    response = await get_current_imbalance_total_volumes.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 2, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].volumes[0].average_power_in_mw == 4.2


@respx.mock
def test_get_current_imbalance_total_volumes_pagination(
    authenticated_client, mock_current_imbalance_total_volumes_response
):
    """Test current imbalance total volumes pagination - cursor/limit sent, nextCursor parsed."""
    paginated_response = {
        **mock_current_imbalance_total_volumes_response,
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/current"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_current_imbalance_total_volumes.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 2, 0, 0, tzinfo=timezone.utc),
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=120,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "120"


@pytest.fixture
def mock_day_ahead_energy_prices_response():
    """Mock response data for day-ahead energy prices."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-02T00:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "data": [
            {
                "area": "FI",
                "eicCode": "10YFI-1--------U",
                "currency": "EUR",
                "prices": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "pricePerMwh": 45.67
                    },
                    {
                        "period": {
                            "startAt": "2025-01-01T01:00:00Z",
                            "endAt": "2025-01-01T02:00:00Z"
                        },
                        "pricePerMwh": 38.21
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_day_ahead_energy_prices_success(authenticated_client, mock_day_ahead_energy_prices_response):
    """Test successful day-ahead energy prices request."""
    respx.get(
        "https://api.balancing.services/v2/energy/day-ahead/prices"
    ).mock(return_value=Response(200, json=mock_day_ahead_energy_prices_response))

    response = get_day_ahead_energy_prices.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "FI"
    assert response.parsed.data[0].currency == "EUR"
    assert len(response.parsed.data[0].prices) == 2
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.67
    assert response.parsed.data[0].prices[1].price_per_mwh == 38.21


@respx.mock
def test_get_day_ahead_energy_prices_pagination(authenticated_client):
    """Test day-ahead energy prices pagination - response with nextCursor."""
    paginated_response = {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-08T00:00:00Z"
        },
        "hasMore": True,
        "nextUpdatedSince": "2025-01-02T09:15:00Z",
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
        "data": [
            {
                "area": "FI",
                "eicCode": "10YFI-1--------U",
                "currency": "EUR",
                "prices": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T01:00:00Z"
                        },
                        "pricePerMwh": 45.67
                    }
                ]
            }
        ]
    }

    respx.get(
        "https://api.balancing.services/v2/energy/day-ahead/prices"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_day_ahead_energy_prices.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 8, 0, 0, 0, tzinfo=timezone.utc),
        limit=100,
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.67


@respx.mock
def test_get_day_ahead_energy_prices_unauthorized(authenticated_client):
    """Test unauthorized response (401) for day-ahead energy prices."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/energy/day-ahead/prices"
    ).mock(return_value=Response(401, json=error_response))

    response = get_day_ahead_energy_prices.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@respx.mock
def test_get_day_ahead_energy_prices_not_implemented(authenticated_client):
    """Test not implemented response (501) when area has no CC-4 licensed data."""
    error_response = {
        "type": "not-implemented",
        "title": "Not Implemented",
        "status": 501,
        "detail": "Day-ahead prices are not available for this bidding zone"
    }

    respx.get(
        "https://api.balancing.services/v2/energy/day-ahead/prices"
    ).mock(return_value=Response(501, json=error_response))

    response = get_day_ahead_energy_prices.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 501
    assert response.parsed is not None
    assert response.parsed.status == 501


@pytest.mark.asyncio
@respx.mock
async def test_async_get_day_ahead_energy_prices(authenticated_client, mock_day_ahead_energy_prices_response):
    """Test async request for day-ahead energy prices."""
    respx.get(
        "https://api.balancing.services/v2/energy/day-ahead/prices"
    ).mock(return_value=Response(200, json=mock_day_ahead_energy_prices_response))

    response = await get_day_ahead_energy_prices.asyncio_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "FI"
    assert response.parsed.data[0].prices[0].price_per_mwh == 45.67


@pytest.fixture
def mock_imbalance_price_forecasts_response():
    """Mock response data for imbalance price forecasts (nowcasts)."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-01T00:20:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "currency": "EUR",
                "direction": "symmetric",
                "forecasts": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "quantiles": [
                            {"level": 0.1, "pricePerMwh": 12.5},
                            {"level": 0.5, "pricePerMwh": 45.5},
                            {"level": 0.9, "pricePerMwh": 98.0}
                        ],
                        "madeAt": "2025-01-01T00:05:00Z",
                        "degraded": False
                    },
                    {
                        "period": {
                            "startAt": "2025-01-01T00:15:00Z",
                            "endAt": "2025-01-01T00:30:00Z"
                        },
                        "quantiles": [
                            {"level": 0.1, "pricePerMwh": 10.0},
                            {"level": 0.5, "pricePerMwh": 40.0},
                            {"level": 0.9, "pricePerMwh": 91.0}
                        ],
                        "madeAt": "2025-01-01T00:05:00Z",
                        "degraded": True
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_imbalance_price_forecasts_success(authenticated_client, mock_imbalance_price_forecasts_response):
    """Test successful imbalance price forecasts request."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/forecast"
    ).mock(return_value=Response(200, json=mock_imbalance_price_forecasts_response))

    response = get_imbalance_price_forecasts.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert response.parsed.queried_period.start_at == datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"
    assert response.parsed.data[0].eic_code == "10Y1001A1001A39I"
    assert response.parsed.data[0].currency == "EUR"
    assert response.parsed.data[0].direction == "symmetric"

    forecast = response.parsed.data[0].forecasts[0]
    assert forecast.period.start_at == datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert forecast.degraded is False
    assert forecast.made_at == datetime(2025, 1, 1, 0, 5, 0, tzinfo=timezone.utc)
    # Quantiles are level/price pairs, ascending by level - read the levels off the
    # forecast rather than indexing by a hardcoded position.
    levels = [quantile.level for quantile in forecast.quantiles]
    assert levels == sorted(levels)
    assert all(0 < level < 1 for level in levels)
    median = next(quantile for quantile in forecast.quantiles if quantile.level == 0.5)
    assert median.price_per_mwh == 45.5
    assert response.parsed.data[0].forecasts[1].degraded is True


@respx.mock
def test_get_imbalance_price_forecasts_unserved_area_is_empty(authenticated_client):
    """Test that an area without forecast coverage returns an empty result, not an error."""
    empty_response = {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-01T00:20:00Z",
        "data": []
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/forecast"
    ).mock(return_value=Response(200, json=empty_response))

    response = get_imbalance_price_forecasts.sync_detailed(
        client=authenticated_client,
        area="FI",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.data == []
    assert response.parsed.has_more is False


@respx.mock
def test_get_imbalance_price_forecasts_pagination(authenticated_client, mock_imbalance_price_forecasts_response):
    """Test imbalance price forecasts pagination - cursor/limit/updated-since sent, nextCursor parsed."""
    paginated_response = {
        **mock_imbalance_price_forecasts_response,
        "hasMore": True,
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/imbalance/prices/forecast"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_imbalance_price_forecasts.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc),
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
        updated_since=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert response.parsed.next_updated_since == datetime(2025, 1, 1, 0, 20, 0, tzinfo=timezone.utc)
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"
    assert sent_url.params["updated-since"] == "2025-01-01T00:00:00+00:00"


@respx.mock
def test_get_imbalance_price_forecasts_unauthorized(authenticated_client):
    """Test unauthorized response (401) for imbalance price forecasts."""
    error_response = {
        "type": "unauthorized",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Invalid or missing authentication token"
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/forecast"
    ).mock(return_value=Response(401, json=error_response))

    response = get_imbalance_price_forecasts.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 401
    assert response.parsed is not None
    assert response.parsed.status == 401


@pytest.mark.asyncio
@respx.mock
async def test_async_get_imbalance_price_forecasts(authenticated_client, mock_imbalance_price_forecasts_response):
    """Test async request for imbalance price forecasts."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/forecast"
    ).mock(return_value=Response(200, json=mock_imbalance_price_forecasts_response))

    response = await get_imbalance_price_forecasts.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data) == 1
    assert len(response.parsed.data[0].forecasts) == 2
    assert response.parsed.data[0].forecasts[0].quantiles[1].price_per_mwh == 45.5


@pytest.fixture
def mock_imbalance_price_history_response():
    """Mock response data for the imbalance price revision history."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-01T00:20:00Z",
        "data": [
            {
                "area": "BE",
                "eicCode": "10YBE----------2",
                "currency": "EUR",
                "direction": "symmetric",
                "prices": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "pricePerMwh": 41.2,
                        "observedAt": "2025-01-01T00:16:04Z"
                    },
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "pricePerMwh": 38.9,
                        "observedAt": "2025-01-01T01:02:11Z"
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_imbalance_price_history_success(authenticated_client, mock_imbalance_price_history_response):
    """Test successful imbalance price history request."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/history"
    ).mock(return_value=Response(200, json=mock_imbalance_price_history_response))

    response = get_imbalance_price_history.sync_detailed(
        client=authenticated_client,
        area="BE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "BE"
    assert response.parsed.data[0].currency == "EUR"
    assert response.parsed.data[0].direction == "symmetric"

    # One period, two entries: the same quarter revised once. They are distinguished
    # only by observedAt, which ascends, and the last one is the value served now.
    revisions = response.parsed.data[0].prices
    assert len(revisions) == 2
    assert all(
        revision.period.start_at == datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        for revision in revisions
    )
    observed_at = [revision.observed_at for revision in revisions]
    assert observed_at == sorted(observed_at)
    assert observed_at[0] == datetime(2025, 1, 1, 0, 16, 4, tzinfo=timezone.utc)
    assert revisions[0].price_per_mwh == 41.2
    assert revisions[-1].price_per_mwh == 38.9


@respx.mock
def test_get_imbalance_price_history_before_log_start_is_empty(authenticated_client):
    """Test that a window predating the revision log returns an empty result, not an error."""
    empty_response = {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-01T00:20:00Z",
        "data": []
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/history"
    ).mock(return_value=Response(200, json=empty_response))

    response = get_imbalance_price_history.sync_detailed(
        client=authenticated_client,
        area="BE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.data == []
    assert response.parsed.has_more is False


@respx.mock
def test_get_imbalance_price_history_pagination(authenticated_client, mock_imbalance_price_history_response):
    """Test imbalance price history pagination - cursor/limit/updated-since sent, nextCursor parsed."""
    paginated_response = {
        **mock_imbalance_price_history_response,
        "hasMore": True,
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/imbalance/prices/history"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_imbalance_price_history.sync_detailed(
        client=authenticated_client,
        area="BE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc),
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
        updated_since=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert response.parsed.next_updated_since == datetime(2025, 1, 1, 0, 20, 0, tzinfo=timezone.utc)
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"
    assert sent_url.params["updated-since"] == "2025-01-01T00:00:00+00:00"


@pytest.mark.asyncio
@respx.mock
async def test_async_get_imbalance_price_history(authenticated_client, mock_imbalance_price_history_response):
    """Test async request for the imbalance price history."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/prices/history"
    ).mock(return_value=Response(200, json=mock_imbalance_price_history_response))

    response = await get_imbalance_price_history.asyncio_detailed(
        client=authenticated_client,
        area="BE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data[0].prices) == 2
    assert response.parsed.data[0].prices[-1].observed_at == datetime(
        2025, 1, 1, 1, 2, 11, tzinfo=timezone.utc
    )


@pytest.fixture
def mock_imbalance_total_volume_history_response():
    """Mock response data for the total imbalance volume revision history."""
    return {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-01T00:20:00Z",
        "data": [
            {
                "area": "EE",
                "eicCode": "10Y1001A1001A39I",
                "volumes": [
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "averagePowerInMw": 60.5,
                        "direction": "surplus",
                        "observedAt": "2025-01-01T00:16:04Z"
                    },
                    {
                        "period": {
                            "startAt": "2025-01-01T00:00:00Z",
                            "endAt": "2025-01-01T00:15:00Z"
                        },
                        "averagePowerInMw": 12.8,
                        "direction": "deficit",
                        "observedAt": "2025-01-01T01:02:11Z"
                    }
                ]
            }
        ]
    }


@respx.mock
def test_get_imbalance_total_volume_history_success(
    authenticated_client, mock_imbalance_total_volume_history_response
):
    """Test successful total imbalance volume history request."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/history"
    ).mock(return_value=Response(200, json=mock_imbalance_total_volume_history_response))

    response = get_imbalance_total_volume_history.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is False
    assert len(response.parsed.data) == 1
    assert response.parsed.data[0].area == "EE"

    # One period, two entries: the same quarter revised once. They are distinguished
    # only by observedAt, which ascends, and the last one is the value served now.
    # A revision can flip the direction as well as the magnitude.
    revisions = response.parsed.data[0].volumes
    assert len(revisions) == 2
    assert all(
        revision.period.start_at == datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        for revision in revisions
    )
    observed_at = [revision.observed_at for revision in revisions]
    assert observed_at == sorted(observed_at)
    assert observed_at[0] == datetime(2025, 1, 1, 0, 16, 4, tzinfo=timezone.utc)
    assert revisions[0].average_power_in_mw == 60.5
    assert revisions[0].direction == "surplus"
    assert revisions[-1].average_power_in_mw == 12.8
    assert revisions[-1].direction == "deficit"


@respx.mock
def test_get_imbalance_total_volume_history_before_log_start_is_empty(authenticated_client):
    """Test that a window predating the revision log returns an empty result, not an error."""
    empty_response = {
        "queriedPeriod": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-01-01T01:00:00Z"
        },
        "hasMore": False,
        "nextUpdatedSince": "2025-01-01T00:20:00Z",
        "data": []
    }

    respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/history"
    ).mock(return_value=Response(200, json=empty_response))

    response = get_imbalance_total_volume_history.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.data == []
    assert response.parsed.has_more is False


@respx.mock
def test_get_imbalance_total_volume_history_pagination(
    authenticated_client, mock_imbalance_total_volume_history_response
):
    """Test total imbalance volume history pagination - cursor/limit/updated-since sent, nextCursor parsed."""
    paginated_response = {
        **mock_imbalance_total_volume_history_response,
        "hasMore": True,
        "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
    }

    route = respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/history"
    ).mock(return_value=Response(200, json=paginated_response))

    response = get_imbalance_total_volume_history.sync_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc),
        cursor="v1:AAAAAYwBAgMEBQYHCAkKCw==",
        limit=100,
        updated_since=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert response.parsed.has_more is True
    assert response.parsed.next_cursor == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert response.parsed.next_updated_since == datetime(2025, 1, 1, 0, 20, 0, tzinfo=timezone.utc)
    sent_url = route.calls.last.request.url
    assert sent_url.params["cursor"] == "v1:AAAAAYwBAgMEBQYHCAkKCw=="
    assert sent_url.params["limit"] == "100"
    assert sent_url.params["updated-since"] == "2025-01-01T00:00:00+00:00"


@pytest.mark.asyncio
@respx.mock
async def test_async_get_imbalance_total_volume_history(
    authenticated_client, mock_imbalance_total_volume_history_response
):
    """Test async request for the total imbalance volume history."""
    respx.get(
        "https://api.balancing.services/v2/imbalance/total-volumes/history"
    ).mock(return_value=Response(200, json=mock_imbalance_total_volume_history_response))

    response = await get_imbalance_total_volume_history.asyncio_detailed(
        client=authenticated_client,
        area="EE",
        period_start_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        period_end_at=datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    assert response.status_code == 200
    assert response.parsed is not None
    assert len(response.parsed.data[0].volumes) == 2
    assert response.parsed.data[0].volumes[-1].observed_at == datetime(
        2025, 1, 1, 1, 2, 11, tzinfo=timezone.utc
    )
