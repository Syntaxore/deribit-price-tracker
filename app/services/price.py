import time

from app.clients.deribit import DeribitClient
from app.repositories.price import PriceRepository
from app.schemas.price import PriceCreate, PriceRead, PriceListResponse

TRACKED_TICKERS = ["btc_usd", "eth_usd"]


class PriceService:

    def __init__(self, repository: PriceRepository):
        self.repository = repository

    async def fetch_and_save_prices(self) -> None:
        async with DeribitClient() as client:
            for ticker in TRACKED_TICKERS:
                price = await client.get_index_price(ticker)
                await self.repository.create(
                    PriceCreate(
                        ticker=ticker.upper(),
                        price=price,
                        timestamp=int(time.time()),
                    )
                )

    async def get_all(self, ticker: str) -> PriceListResponse:
        records = await self.repository.get_all(ticker.upper())
        items = [PriceRead.model_validate(r) for r in records]
        return PriceListResponse(ticker=ticker.upper(), items=items, total=len(items))

    async def get_latest(self, ticker: str) -> PriceRead | None:
        record = await self.repository.get_latest(ticker.upper())
        if record is None:
            return None
        return PriceRead.model_validate(record)

    async def get_by_date_range(
        self, ticker: str, from_ts: int, to_ts: int
    ) -> PriceListResponse:
        records = await self.repository.get_by_date_range(ticker.upper(), from_ts, to_ts)
        items = [PriceRead.model_validate(r) for r in records]
        return PriceListResponse(ticker=ticker.upper(), items=items, total=len(items))
