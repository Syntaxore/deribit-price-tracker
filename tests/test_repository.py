import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.price import PriceRepository
from app.schemas.price import PriceCreate
from app.models.price import CurrencyPrice


def make_record(ticker: str, price: float, timestamp: int) -> MagicMock:
    record = MagicMock(spec=CurrencyPrice)
    record.id = 1
    record.ticker = ticker
    record.price = price
    record.timestamp = timestamp
    return record


@pytest.mark.asyncio
async def test_create_price():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    repository = PriceRepository(mock_session)
    
    data = PriceCreate(ticker="BTC_USD", price=81000.0, timestamp=1728900000)
    
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    
    result = await repository.create(data)
    
    assert mock_session.add.called
    assert mock_session.commit.called
    assert result.ticker == "BTC_USD"
    assert result.price == 81000.0


@pytest.mark.asyncio
async def test_get_all_by_ticker():
    mock_session = AsyncMock()
    repository = PriceRepository(mock_session)
    
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [
        make_record("BTC_USD", 81000.0, 1728900000),
        make_record("BTC_USD", 80000.0, 1728800000),
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result
    
    result = await repository.get_all("BTC_USD")
    
    assert len(result) == 2
    assert mock_session.execute.called


@pytest.mark.asyncio
async def test_get_latest():
    mock_session = AsyncMock()
    repository = PriceRepository(mock_session)
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = make_record("ETH_USD", 2400.0, 1728900000)
    mock_session.execute.return_value = mock_result
    
    result = await repository.get_latest("ETH_USD")
    
    assert result is not None
    assert result.ticker == "ETH_USD"


@pytest.mark.asyncio
async def test_get_by_date_range():
    mock_session = AsyncMock()
    repository = PriceRepository(mock_session)
    
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [
        make_record("BTC_USD", 81000.0, 1728900000),
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result
    
    result = await repository.get_by_date_range("BTC_USD", 1728800000, 1728900000)
    
    assert len(result) == 1
