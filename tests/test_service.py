import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.price import PriceService
from app.schemas.price import PriceCreate
from app.models.price import CurrencyPrice


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    return PriceService(mock_repository)


def make_record(ticker: str, price: float, timestamp: int) -> MagicMock:
    record = MagicMock(spec=CurrencyPrice)
    record.id = 1
    record.ticker = ticker
    record.price = price
    record.timestamp = timestamp
    return record


@pytest.mark.asyncio
async def test_get_all_returns_list(service, mock_repository):
    mock_repository.get_all.return_value = [
        make_record("BTC_USD", 81000.0, 1728900000),
        make_record("BTC_USD", 80000.0, 1728800000),
    ]
    result = await service.get_all("btc_usd")
    assert result.ticker == "BTC_USD"
    assert result.total == 2
    mock_repository.get_all.assert_called_once_with("BTC_USD")


@pytest.mark.asyncio
async def test_get_latest_returns_price(service, mock_repository):
    mock_repository.get_latest.return_value = make_record("ETH_USD", 2400.0, 1728900000)
    result = await service.get_latest("eth_usd")
    assert result.ticker == "ETH_USD"
    assert result.price == 2400.0


@pytest.mark.asyncio
async def test_get_latest_returns_none_when_no_data(service, mock_repository):
    mock_repository.get_latest.return_value = None
    result = await service.get_latest("btc_usd")
    assert result is None


@pytest.mark.asyncio
async def test_get_by_date_range(service, mock_repository):
    mock_repository.get_by_date_range.return_value = [
        make_record("BTC_USD", 81000.0, 1728900000),
    ]
    result = await service.get_by_date_range("btc_usd", 1728800000, 1728900000)
    assert result.total == 1
    mock_repository.get_by_date_range.assert_called_once_with("BTC_USD", 1728800000, 1728900000)


@pytest.mark.asyncio
async def test_fetch_and_save_prices(service, mock_repository):
    with patch("app.services.price.DeribitClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_index_price.side_effect = [81000.0, 2400.0]
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        await service.fetch_and_save_prices()

        assert mock_repository.create.call_count == 2
        call_args = [call.args[0] for call in mock_repository.create.call_args_list]
        assert call_args[0].ticker == "BTC_USD"
        assert call_args[1].ticker == "ETH_USD"
