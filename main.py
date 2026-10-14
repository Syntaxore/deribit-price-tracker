from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.router import router
from app.db.base import Base
from app.db.session import engine
from app.models import price


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(title="Deribit Price Tracker", lifespan=lifespan)

app.include_router(router)
