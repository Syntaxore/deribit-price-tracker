import asyncio

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionFactory
from app.repositories.price import PriceRepository
from app.services.price import PriceService


@celery_app.task(name="app.workers.tasks.fetch_prices_task")
def fetch_prices_task() -> None:
    asyncio.run(_fetch_prices())


async def _fetch_prices() -> None:
    async with AsyncSessionFactory() as session:
        repository = PriceRepository(session)
        service = PriceService(repository)
        await service.fetch_and_save_prices()
