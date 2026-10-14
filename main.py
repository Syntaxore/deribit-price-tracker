from fastapi import FastAPI
from app.api.router import router

app = FastAPI(title="Deribit Price Tracker")

app.include_router(router)
