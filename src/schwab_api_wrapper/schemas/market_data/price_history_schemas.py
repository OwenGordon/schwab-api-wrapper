from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Candle(BaseModel):
    close: float
    epoch: datetime = Field(..., alias="datetime")
    datetimeISO8601: Optional[datetime] = None
    high: float
    low: float
    open: float
    volume: int


class CandleList(BaseModel):
    candles: Optional[List[Candle]] = None
    empty: bool
    previousClose: Optional[float] = None
    previousCloseDateEpoch: Optional[datetime] = Field(None, alias="previousCloseDate")
    previousCloseDateISO8601: Optional[datetime] = None
    symbol: str
