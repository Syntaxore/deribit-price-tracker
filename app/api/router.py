from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.dependencies import get_price_service
from app.schemas.price import PriceListResponse, PriceRead
from app.services.price import PriceService

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/", response_model=PriceListResponse)
async def get_all_prices(
    ticker: Annotated[str, Query(description="Currency ticker, e.g. BTC_USD")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PriceListResponse:
    return await service.get_all(ticker)


@router.get("/latest", response_model=PriceRead)
async def get_latest_price(
    ticker: Annotated[str, Query(description="Currency ticker, e.g. BTC_USD")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PriceRead:
    result = await service.get_latest(ticker)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
    return result


@router.get("/range", response_model=PriceListResponse)
async def get_prices_by_date_range(
    ticker: Annotated[str, Query(description="Currency ticker, e.g. BTC_USD")],
    from_ts: Annotated[int, Query(description="Start of range as UNIX timestamp")],
    to_ts: Annotated[int, Query(description="End of range as UNIX timestamp")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PriceListResponse:
    if from_ts > to_ts:
        raise HTTPException(status_code=400, detail="from_ts must be less than or equal to to_ts")
    return await service.get_by_date_range(ticker, from_ts, to_ts)
