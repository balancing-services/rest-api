"""
Basic tests for the Balancing Services Python client.

These tests verify that the generated client has the expected structure
and can be instantiated correctly.
"""

from balancing_services import AuthenticatedClient, Client
from balancing_services.api.default import (
    get_balancing_capacity_bids,
    get_balancing_capacity_demand,
    get_balancing_capacity_prices,
    get_balancing_capacity_procured_volumes,
    get_balancing_energy_activated_volumes,
    get_balancing_energy_bids,
    get_balancing_energy_demand,
    get_balancing_energy_offered_volumes,
    get_balancing_energy_prices,
    get_balancing_energy_satisfied_demand,
    get_cross_border_available_capacity,
    get_cross_border_energy_volumes,
    get_cross_border_marginal_prices,
    get_current_imbalance_total_volumes,
    get_day_ahead_energy_prices,
    get_imbalance_price_forecasts,
    get_imbalance_price_history,
    get_imbalance_prices,
    get_imbalance_total_volume_history,
    get_imbalance_total_volumes,
)
from balancing_services.models import (
    ImbalancePriceForecast,
    ImbalancePriceForecastQuantile,
    ImbalancePriceForecasts,
    ImbalancePriceForecastsResponse,
    ImbalancePriceHistory,
    ImbalancePriceHistoryResponse,
    ImbalancePriceRevision,
    ImbalanceTotalVolumeHistory,
    ImbalanceTotalVolumeHistoryResponse,
    TotalImbalanceVolumeRevision,
)
from balancing_services.models.activation_type import ACTIVATION_TYPE_VALUES
from balancing_services.models.area import AREA_VALUES
from balancing_services.models.bid_status import BID_STATUS_VALUES
from balancing_services.models.currency import CURRENCY_VALUES
from balancing_services.models.direction import DIRECTION_VALUES
from balancing_services.models.imbalance_direction import IMBALANCE_DIRECTION_VALUES
from balancing_services.models.reserve_type import RESERVE_TYPE_VALUES
from balancing_services.models.total_imbalance_direction import (
    TOTAL_IMBALANCE_DIRECTION_VALUES,
)


class TestClientInstantiation:
    """Test that clients can be created correctly."""

    def test_create_unauthenticated_client(self):
        """Test creating an unauthenticated client."""
        client = Client(base_url="https://api.balancing.services/v2")
        assert client._base_url == "https://api.balancing.services/v2"

    def test_create_authenticated_client(self):
        """Test creating an authenticated client."""
        client = AuthenticatedClient(
            base_url="https://api.balancing.services/v2", token="test_token"
        )
        assert client._base_url == "https://api.balancing.services/v2"
        assert client.token == "test_token"

    def test_create_authenticated_client_with_custom_timeout(self):
        """Test creating an authenticated client with custom timeout."""
        client = AuthenticatedClient(
            base_url="https://api.balancing.services/v2", token="test_token", timeout=30.0
        )
        assert client._base_url == "https://api.balancing.services/v2"
        assert client._timeout == 30.0


class TestAPIEndpointsExist:
    """Test that all expected API endpoints are available."""

    def test_imbalance_endpoints_exist(self):
        """Test that imbalance endpoints are available."""
        assert hasattr(get_imbalance_prices, "sync_detailed")
        assert hasattr(get_imbalance_prices, "asyncio_detailed")
        assert hasattr(get_imbalance_price_forecasts, "sync_detailed")
        assert hasattr(get_imbalance_price_forecasts, "asyncio_detailed")
        assert hasattr(get_imbalance_price_history, "sync_detailed")
        assert hasattr(get_imbalance_price_history, "asyncio_detailed")
        assert hasattr(get_imbalance_total_volumes, "sync_detailed")
        assert hasattr(get_imbalance_total_volumes, "asyncio_detailed")
        assert hasattr(get_current_imbalance_total_volumes, "sync_detailed")
        assert hasattr(get_current_imbalance_total_volumes, "asyncio_detailed")
        assert hasattr(get_imbalance_total_volume_history, "sync_detailed")
        assert hasattr(get_imbalance_total_volume_history, "asyncio_detailed")

    def test_imbalance_price_forecast_models_exist(self):
        """Test that the imbalance price forecast models are exported and shaped as expected."""
        forecast = ImbalancePriceForecast.from_dict(
            {
                "period": {
                    "startAt": "2025-01-01T00:00:00Z",
                    "endAt": "2025-01-01T00:15:00Z",
                },
                "quantiles": [{"level": 0.5, "pricePerMwh": 45.5}],
                "madeAt": "2025-01-01T00:05:00Z",
                "degraded": False,
            }
        )
        assert forecast.degraded is False
        assert isinstance(forecast.quantiles[0], ImbalancePriceForecastQuantile)
        assert forecast.quantiles[0].level == 0.5
        assert forecast.quantiles[0].price_per_mwh == 45.5
        assert hasattr(ImbalancePriceForecasts, "from_dict")
        assert hasattr(ImbalancePriceForecastsResponse, "from_dict")

    def test_imbalance_price_history_models_exist(self):
        """Test that the imbalance price history models are exported and shaped as expected."""
        revision = ImbalancePriceRevision.from_dict(
            {
                "period": {
                    "startAt": "2025-01-01T00:00:00Z",
                    "endAt": "2025-01-01T00:15:00Z",
                },
                "pricePerMwh": 41.2,
                "observedAt": "2025-01-01T00:16:04Z",
            }
        )
        assert revision.price_per_mwh == 41.2
        assert revision.observed_at.isoformat() == "2025-01-01T00:16:04+00:00"
        assert hasattr(ImbalancePriceHistory, "from_dict")
        assert hasattr(ImbalancePriceHistoryResponse, "from_dict")

    def test_imbalance_total_volume_history_models_exist(self):
        """Test that the total imbalance volume history models are exported and shaped as expected."""
        revision = TotalImbalanceVolumeRevision.from_dict(
            {
                "period": {
                    "startAt": "2025-01-01T00:00:00Z",
                    "endAt": "2025-01-01T00:15:00Z",
                },
                "averagePowerInMw": 60.5,
                "direction": "surplus",
                "observedAt": "2025-01-01T00:16:04Z",
            }
        )
        assert revision.average_power_in_mw == 60.5
        assert revision.direction == "surplus"
        assert revision.observed_at.isoformat() == "2025-01-01T00:16:04+00:00"
        assert hasattr(ImbalanceTotalVolumeHistory, "from_dict")
        assert hasattr(ImbalanceTotalVolumeHistoryResponse, "from_dict")

    def test_balancing_energy_endpoints_exist(self):
        """Test that balancing energy endpoints are available."""
        assert hasattr(get_balancing_energy_activated_volumes, "sync_detailed")
        assert hasattr(get_balancing_energy_activated_volumes, "asyncio_detailed")
        assert hasattr(get_balancing_energy_prices, "sync_detailed")
        assert hasattr(get_balancing_energy_prices, "asyncio_detailed")
        assert hasattr(get_balancing_energy_bids, "sync_detailed")
        assert hasattr(get_balancing_energy_bids, "asyncio_detailed")
        assert hasattr(get_balancing_energy_offered_volumes, "sync_detailed")
        assert hasattr(get_balancing_energy_offered_volumes, "asyncio_detailed")
        assert hasattr(get_balancing_energy_demand, "sync_detailed")
        assert hasattr(get_balancing_energy_demand, "asyncio_detailed")
        assert hasattr(get_balancing_energy_satisfied_demand, "sync_detailed")
        assert hasattr(get_balancing_energy_satisfied_demand, "asyncio_detailed")
        assert hasattr(get_cross_border_marginal_prices, "sync_detailed")
        assert hasattr(get_cross_border_marginal_prices, "asyncio_detailed")
        assert hasattr(get_cross_border_energy_volumes, "sync_detailed")
        assert hasattr(get_cross_border_energy_volumes, "asyncio_detailed")
        assert hasattr(get_cross_border_available_capacity, "sync_detailed")
        assert hasattr(get_cross_border_available_capacity, "asyncio_detailed")

    def test_balancing_capacity_endpoints_exist(self):
        """Test that balancing capacity endpoints are available."""
        assert hasattr(get_balancing_capacity_bids, "sync_detailed")
        assert hasattr(get_balancing_capacity_bids, "asyncio_detailed")
        assert hasattr(get_balancing_capacity_demand, "sync_detailed")
        assert hasattr(get_balancing_capacity_demand, "asyncio_detailed")
        assert hasattr(get_balancing_capacity_prices, "sync_detailed")
        assert hasattr(get_balancing_capacity_prices, "asyncio_detailed")
        assert hasattr(get_balancing_capacity_procured_volumes, "sync_detailed")
        assert hasattr(get_balancing_capacity_procured_volumes, "asyncio_detailed")

    def test_day_ahead_energy_endpoints_exist(self):
        """Test that day-ahead energy endpoints are available."""
        assert hasattr(get_day_ahead_energy_prices, "sync_detailed")
        assert hasattr(get_day_ahead_energy_prices, "asyncio_detailed")
        assert hasattr(get_day_ahead_energy_prices, "sync")
        assert hasattr(get_day_ahead_energy_prices, "asyncio")


class TestEnums:
    """Test that all expected enum string values are recognized.

    Under ``literal_enums`` the generated types are ``Literal`` string aliases
    with a companion ``*_VALUES`` set of accepted wire strings; there is no
    member access (``Area.EE``) any more.
    """

    def test_area_values(self):
        """Test Area accepted values."""
        assert "EE" in AREA_VALUES
        assert "FI" in AREA_VALUES
        assert "LV" in AREA_VALUES
        # Verify it's a comprehensive set
        assert len(AREA_VALUES) >= 40  # At least 40 areas as per spec

    def test_reserve_type_values(self):
        """Test ReserveType accepted values."""
        assert "FCR" in RESERVE_TYPE_VALUES
        assert "aFRR" in RESERVE_TYPE_VALUES
        assert "mFRR" in RESERVE_TYPE_VALUES
        assert "RR" in RESERVE_TYPE_VALUES

    def test_direction_values(self):
        """Test Direction accepted values."""
        assert "up" in DIRECTION_VALUES
        assert "down" in DIRECTION_VALUES

    def test_imbalance_direction_values(self):
        """Test ImbalanceDirection accepted values."""
        assert "positive" in IMBALANCE_DIRECTION_VALUES
        assert "symmetric" in IMBALANCE_DIRECTION_VALUES
        assert "negative" in IMBALANCE_DIRECTION_VALUES

    def test_total_imbalance_direction_values(self):
        """Test TotalImbalanceDirection accepted values."""
        assert "surplus" in TOTAL_IMBALANCE_DIRECTION_VALUES
        assert "deficit" in TOTAL_IMBALANCE_DIRECTION_VALUES
        assert "balanced" in TOTAL_IMBALANCE_DIRECTION_VALUES

    def test_currency_values(self):
        """Test Currency accepted values."""
        assert "EUR" in CURRENCY_VALUES
        assert "BGN" in CURRENCY_VALUES
        assert "CHF" in CURRENCY_VALUES

    def test_activation_type_values(self):
        """Test ActivationType accepted values."""
        assert "direct" in ACTIVATION_TYPE_VALUES
        assert "scheduled" in ACTIVATION_TYPE_VALUES
        assert "notApplicable" in ACTIVATION_TYPE_VALUES

    def test_bid_status_values(self):
        """Test BidStatus accepted values."""
        assert "offered" in BID_STATUS_VALUES
        assert "accepted" in BID_STATUS_VALUES


class TestClientConfiguration:
    """Test client configuration options."""

    def test_custom_base_url(self):
        """Test that custom base URL is respected."""
        client = Client(base_url="https://custom.example.com/api")
        assert client._base_url == "https://custom.example.com/api"

    def test_client_has_with_headers_method(self):
        """Test that client has method to add headers."""
        client = AuthenticatedClient(
            base_url="https://api.balancing.services/v2", token="test_token"
        )
        assert hasattr(client, "with_headers")

    def test_authenticated_client_includes_token(self):
        """Test that authenticated client has token configured."""
        client = AuthenticatedClient(
            base_url="https://api.balancing.services/v2", token="test_token_12345"
        )
        assert client.token == "test_token_12345"
        assert client.prefix == "Bearer"
        assert client.auth_header_name == "Authorization"

    def test_client_requests_gzip_encoding(self):
        """Test that client sends Accept-Encoding: gzip header."""
        client = Client(base_url="https://api.balancing.services/v2")
        httpx_client = client.get_httpx_client()
        assert "gzip" in httpx_client.headers.get("accept-encoding", "")

    def test_authenticated_client_requests_gzip_encoding(self):
        """Test that authenticated client sends Accept-Encoding: gzip header."""
        client = AuthenticatedClient(
            base_url="https://api.balancing.services/v2", token="test_token"
        )
        httpx_client = client.get_httpx_client()
        assert "gzip" in httpx_client.headers.get("accept-encoding", "")
