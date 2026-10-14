from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import CurrencyPrice
from app.repositories.base import BaseRepository
from app.schemas.price import PriceCreate


class PriceRepository(BaseRepository[CurrencyPrice]):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: PriceCreate) -> CurrencyPrice:
        record = CurrencyPrice(
            ticker=data.ticker,
            price=data.price,
            timestamp=data.timestamp,
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_all(self, ticker: str) -> list[CurrencyPrice]:
        result = await self.session.execute(
            select(CurrencyPrice)
            .where(CurrencyPrice.ticker == ticker)
            .order_by(CurrencyPrice.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_latest(self, ticker: str) -> CurrencyPrice | None:
        result = await self.session.execute(
            select(CurrencyPrice)
            .where(CurrencyPrice.ticker == ticker)
            .order_by(CurrencyPrice.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_date_range(
        self, ticker: str, from_ts: int, to_ts: int
    ) -> list[CurrencyPrice]:
        result = await self.session.execute(
            select(CurrencyPrice)
            .where(
                CurrencyPrice.ticker == ticker,
                CurrencyPrice.timestamp >= from_ts,
                CurrencyPrice.timestamp <= to_ts,
            )
            .order_by(CurrencyPrice.timestamp.desc())
        )
        return list(result.scalars().all())
