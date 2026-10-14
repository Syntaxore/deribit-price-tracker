import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.price import PriceRepository
from app.models.price import CurrencyPrice


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return PriceRepository(mock_session)


@pytest.fixture
def sample_record():
    record = MagicMock(spec=CurrencyPrice)
    record.id = 1
    record.ticker = "BTC_USD"
    record.price = 81000.0
    record.timestamp = 1728900000
    return record
