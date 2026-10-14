from types import TracebackType
from typing import Self

import aiohttp

from app.core.config import settings


class DeribitClient:

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def get_index_price(self, currency: str) -> float:
        url = f"{settings.DERIBIT_API_URL}/public/get_index_price"
        params = {"index_name": currency.lower()}
        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data["result"]["index_price"]
