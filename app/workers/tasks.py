import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionFactory
from app.repositories.price import PriceRepository
from app.services.price import PriceService


@celery_app.task(name="app.workers.tasks.fetch_prices_task")
def fetch_prices_task() -> None:
    asyncio.run(_fetch_prices())


async def _fetch_prices() -> None:
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            repository = PriceRepository(session)
            service = PriceService(repository)
            await service.fetch_and_save_prices()
    finally:
        await engine.dispose()