from pydantic import BaseModel


class PriceCreate(BaseModel):
    ticker: str
    price: float
    timestamp: int


class PriceRead(BaseModel):
    id: int
    ticker: str
    price: float
    timestamp: int

    model_config = {"from_attributes": True}


class PriceListResponse(BaseModel):
    ticker: str
    items: list[PriceRead]
    total: int
