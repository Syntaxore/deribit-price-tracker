import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.price import CurrencyPrice
from main import app


def make_record(ticker: str, price: float, timestamp: int) -> MagicMock:
    record = MagicMock(spec=CurrencyPrice)
    record.id = 1
    record.ticker = ticker
    record.price = price
    record.timestamp = timestamp
    return record


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.fixture
def client(mock_service):
    from app.api.dependencies import get_price_service
    app.dependency_overrides[get_price_service] = lambda: mock_service
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_all_prices(client, mock_service):
    from app.schemas.price import PriceListResponse, PriceRead
    mock_service.get_all.return_value = PriceListResponse(
        ticker="BTC_USD",
        items=[PriceRead(id=1, ticker="BTC_USD", price=81000.0, timestamp=1728900000)],
        total=1,
    )
    async with client as c:
        response = await c.get("/prices/?ticker=BTC_USD")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "BTC_USD"
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_latest_price(client, mock_service):
    from app.schemas.price import PriceRead
    mock_service.get_latest.return_value = PriceRead(
        id=1, ticker="ETH_USD", price=2400.0, timestamp=1728900000
    )
    async with client as c:
        response = await c.get("/prices/latest?ticker=ETH_USD")
    assert response.status_code == 200
    assert response.json()["price"] == 2400.0


@pytest.mark.asyncio
async def test_get_latest_price_not_found(client, mock_service):
    mock_service.get_latest.return_value = None
    async with client as c:
        response = await c.get("/prices/latest?ticker=BTC_USD")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_prices_by_range(client, mock_service):
    from app.schemas.price import PriceListResponse, PriceRead
    mock_service.get_by_date_range.return_value = PriceListResponse(
        ticker="BTC_USD",
        items=[PriceRead(id=1, ticker="BTC_USD", price=81000.0, timestamp=1728900000)],
        total=1,
    )
    async with client as c:
        response = await c.get("/prices/range?ticker=BTC_USD&from_ts=1728800000&to_ts=1728900000")
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_prices_by_range_invalid_dates(client, mock_service):
    async with client as c:
        response = await c.get("/prices/range?ticker=BTC_USD&from_ts=1728900000&to_ts=1728800000")
    assert response.status_code == 400
